"""
GraphRAG: builds a lightweight knowledge graph (entities + relations)
from ingested chunks, and uses graph traversal to answer multi-hop
questions that pure vector/keyword search handles poorly
(e.g. "What permits do I need for treks near Annapurna that also
require a guide?").
 
This is intentionally a *lightweight* graph layer (not a full GraphRAG
community-detection pipeline) — entities/relations are extracted with a
cheap LLM call per chunk and stored in SQLite + networkx for traversal.
"""
import json
import uuid
import logging
import networkx as nx
from sqlalchemy.orm import Session
 
from app.models.graph import GraphNode, GraphEdge
from app.services.llm import fast_json_completion
 
logger = logging.getLogger(__name__)
 
ENTITY_EXTRACTION_SYSTEM = (
    "You extract structured knowledge graph triples from text for a travel/tourism "
    "knowledge base. Be concise and only extract clearly stated facts."
)
 
 
def extract_entities_and_relations(text: str) -> dict:
    """
    Returns {"entities": [{"name":..., "type":...}], "relations": [{"source":..., "relation":..., "target":...}]}
    """
    prompt = (
        "From the following text, extract key entities (places, treks, permits, "
        "organizations, activities, requirements) and relationships between them. "
        "Limit to at most 6 entities and 6 relations, focusing on the most important facts.\n\n"
        "Return ONLY a JSON object in this exact shape:\n"
        '{"entities": [{"name": "string", "type": "PLACE|PERMIT|ACTIVITY|ORG|OTHER"}], '
        '"relations": [{"source": "entity name", "relation": "short verb phrase", "target": "entity name"}]}\n\n'
        f"Text:\n{text[:1500]}"

    )
    result = fast_json_completion(prompt, system=ENTITY_EXTRACTION_SYSTEM, max_tokens=600)
    if not result:
        return {"entities": [], "relations": []}
    return {
        "entities": result.get("entities", []) or [],
        "relations": result.get("relations", []) or [],
    }
 
 
def upsert_graph_from_chunk(db: Session, bot_id: str, chunk_id: str, text: str):
    """Extract entities/relations from a single chunk and merge into the bot's graph."""
    extraction = extract_entities_and_relations(text)
    name_to_node: dict[str, GraphNode] = {}
 
    for ent in extraction["entities"]:
        name = (ent.get("name") or "").strip()
        if not name:
            continue
        existing = db.query(GraphNode).filter(
            GraphNode.bot_id == bot_id, GraphNode.name.ilike(name)
        ).first()
        if existing:
            try:
                sources = json.loads(existing.source_chunk_ids or "[]")
            except json.JSONDecodeError:
                sources = []
            if chunk_id not in sources:
                sources.append(chunk_id)
            existing.source_chunk_ids = json.dumps(sources)
            name_to_node[name.lower()] = existing
        else:
            node = GraphNode(
                id=str(uuid.uuid4()),
                bot_id=bot_id,
                name=name,
                entity_type=ent.get("type", "OTHER"),
                source_chunk_ids=json.dumps([chunk_id]),
            )
            db.add(node)
            name_to_node[name.lower()] = node
 
    db.flush()  # ensure node IDs are available for edges
 
    for rel in extraction["relations"]:
        src_name = (rel.get("source") or "").strip().lower()
        tgt_name = (rel.get("target") or "").strip().lower()
        relation = (rel.get("relation") or "related_to").strip()
        if not src_name or not tgt_name:
            continue
 
        src_node = name_to_node.get(src_name) or db.query(GraphNode).filter(
            GraphNode.bot_id == bot_id, GraphNode.name.ilike(src_name)
        ).first()
        tgt_node = name_to_node.get(tgt_name) or db.query(GraphNode).filter(
            GraphNode.bot_id == bot_id, GraphNode.name.ilike(tgt_name)
        ).first()
        if not src_node or not tgt_node:
            continue
 

        existing_edge = db.query(GraphEdge).filter(
            GraphEdge.bot_id == bot_id,
            GraphEdge.source_node_id == src_node.id,
            GraphEdge.target_node_id == tgt_node.id,
            GraphEdge.relation == relation,
        ).first()
        if existing_edge:
            existing_edge.weight += 1.0
        else:
            db.add(GraphEdge(
                id=str(uuid.uuid4()),
                bot_id=bot_id,
                source_node_id=src_node.id,
                target_node_id=tgt_node.id,
                relation=relation,
                source_chunk_ids=json.dumps([chunk_id]),
            ))
 
    db.commit()
 
 
def remove_chunk_from_graph(db: Session, bot_id: str, chunk_id: str):
    """When a chunk is superseded/deleted, strip it from node/edge provenance.
    Nodes/edges with no remaining sources are pruned."""
    nodes = db.query(GraphNode).filter(GraphNode.bot_id == bot_id).all()
    for node in nodes:
        try:
            sources = json.loads(node.source_chunk_ids or "[]")
        except json.JSONDecodeError:
            sources = []
        if chunk_id in sources:
            sources.remove(chunk_id)
            node.source_chunk_ids = json.dumps(sources)
            if not sources:
                db.delete(node)
    db.commit()
 
    edges = db.query(GraphEdge).filter(GraphEdge.bot_id == bot_id).all()
    for edge in edges:
        try:
            sources = json.loads(edge.source_chunk_ids or "[]")
        except json.JSONDecodeError:
            sources = []
        if chunk_id in sources:
            sources.remove(chunk_id)
            edge.source_chunk_ids = json.dumps(sources)
            if not sources:
                db.delete(edge)
    db.commit()
 
 
def build_networkx_graph(db: Session, bot_id: str) -> nx.DiGraph:
    g = nx.DiGraph()
    nodes = db.query(GraphNode).filter(GraphNode.bot_id == bot_id).all()
    for n in nodes:
        g.add_node(n.id, name=n.name, type=n.entity_type)
 
    edges = db.query(GraphEdge).filter(GraphEdge.bot_id == bot_id).all()
    for e in edges:
        g.add_edge(e.source_node_id, e.target_node_id, relation=e.relation, weight=e.weight)

    return g
 
 
def graph_search(db: Session, bot_id: str, query: str, max_hops: int = 2) -> list[dict]:
    """
    Finds entities mentioned in the query (fuzzy match against node names),
    then traverses outward up to `max_hops` to surface related facts that
    pure similarity search would miss. Returns synthetic "chunk-like" results
    (a textual rendering of the relevant subgraph) for inclusion in context.
    """
    nodes = db.query(GraphNode).filter(GraphNode.bot_id == bot_id).all()
    if not nodes:
        return []
 
    lowered_query = query.lower()
    seed_nodes = [n for n in nodes if n.name.lower() in lowered_query or
                  any(word in lowered_query for word in n.name.lower().split() if len(word) > 3)]
    if not seed_nodes:
        return []
 
    g = build_networkx_graph(db, bot_id)
    node_lookup = {n.id: n for n in nodes}
 
    facts = []
    seen_edges = set()
    for seed in seed_nodes:
        if seed.id not in g:
            continue
        for src, tgt in nx.bfs_edges(g, seed.id, depth_limit=max_hops):
            edge_data = g.get_edge_data(src, tgt)
            key = (src, tgt, edge_data.get("relation"))
            if key in seen_edges:
                continue
            seen_edges.add(key)
            src_name = node_lookup.get(src).name if src in node_lookup else g.nodes[src].get("name", "?")
            tgt_name = node_lookup.get(tgt).name if tgt in node_lookup else g.nodes[tgt].get("name", "?")
            relation = edge_data.get("relation", "related to")
            facts.append({
                "chunk_id": f"graph::{src}->{tgt}",
                "text": f"{src_name} {relation} {tgt_name}.",
                "source_file": "knowledge_graph",
                "graph_score": 1.0,
            })
 
    return facts
