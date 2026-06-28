// components/graph/GraphViewer.tsx
'use client';
import { useQuery } from '@tanstack/react-query';
import { apiGet } from '@/lib/api';
import dynamic from 'next/dynamic';
import { GraphData } from '@/types';
// ForceGraph2D is client-only
const ForceGraph2D = dynamic(
  () => import('react-force-graph').then((mod) => mod.ForceGraph2D),
  { ssr: false }
);
export default function GraphViewer({ botId }: { botId: string }) {
  const { data, isLoading, error } = useQuery<GraphData>({
    queryKey: ['graph', botId],
    queryFn: () => apiGet(`/api/bots/${botId}/graph`),
  });
  if (isLoading) return <div className="p-4">Loading graph...</div>;
  if (error) return <div className="p-4 text-red-500">Error: {(error as Error).message}</div>;
  if (!data || data.node_count === 0) {
    return <div className="p-4 text-gray-500">No graph data available for this bot.</div>;
  }
  // Transform for ForceGraph format
  const graphData = {
    nodes: data.nodes.map((n) => ({ id: n.id, name: n.name, type: n.type })),
    links: data.edges.map((e) => ({ source: e.source, target: e.target, label: e.relation })),
  };

  return (
    <div className="border rounded-lg overflow-hidden h-[600px]">
      <ForceGraph2D
        graphData={graphData}
        nodeLabel="name"
        linkLabel="label"
        nodeColor={(node: any) => {
          const colors: Record<string, string> = {
            PLACE: '#3b82f6',
            PERMIT: '#f59e0b',
            ACTIVITY: '#10b981',
            ORG: '#8b5cf6',
            OTHER: '#6b7280',
          };
          return colors[node.type] || '#6b7280';
        }}
        nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D) => {
          const label = node.name;
          const fontSize = 12;
          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = '#fff';
          ctx.beginPath();
          ctx.arc(node.x, node.y, 8, 0, 2 * Math.PI);
          ctx.fill();
          ctx.fillStyle = '#000';
          ctx.fillText(label, node.x, node.y + 20);
        }}
        linkWidth={1}
        linkColor={() => '#9ca3af'}
      />
    </div>
  );
}
