from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.graph import GraphNode, GraphEdge
from app.routers.bots import _get_owned_bot
router = APIRouter(prefix="/api/bots/{bot_id}/graph", tags=["graph"])
@router.get("")
def get_graph(bot_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Returns the full extracted knowledge graph for this bot, for inspection/visualization."""
    bot = _get_owned_bot(db, bot_id, user)
    nodes = db.query(GraphNode).filter(GraphNode.bot_id == bot.id).all()
    edges = db.query(GraphEdge).filter(GraphEdge.bot_id == bot.id).all()
    node_lookup = {n.id: n.name for n in nodes}
    return {
        "nodes": [{"id": n.id, "name": n.name, "type": n.entity_type} for n in nodes],
        "edges": [
            {
                "source": node_lookup.get(e.source_node_id, "?"),
                "target": node_lookup.get(e.target_node_id, "?"),
                "relation": e.relation,
                "weight": e.weight,
            }
            for e in edges
        ],
        "node_count": len(nodes),
        "edge_count": len(edges),
    }
