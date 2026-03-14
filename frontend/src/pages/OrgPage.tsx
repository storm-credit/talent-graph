import { useCallback, useEffect, useState } from "react";
import {
  ReactFlow,
  type Node,
  type Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { api } from "../api";
import type { GraphResponse } from "../types";

function mapToFlowNodes(graph: GraphResponse): Node[] {
  const deptNodes = graph.nodes.filter((n) => n.type === "department");
  const roleNodes = graph.nodes.filter((n) => n.type === "role");
  const personNodes = graph.nodes.filter((n) => n.type === "person");

  const nodes: Node[] = [];
  const deptSpacing = 350;
  const roleSpacing = 200;

  deptNodes.forEach((dept, di) => {
    const x = di * deptSpacing;
    nodes.push({
      id: dept.id,
      position: { x, y: 0 },
      data: { label: dept.label },
      style: {
        background: "#18181b",
        border: "2px solid #10b981",
        borderRadius: 12,
        padding: 12,
        color: "#10b981",
        fontWeight: 700,
        fontSize: 14,
      },
    });

    // Find roles connected to this dept
    const deptRoles = graph.edges
      .filter((e) => e.source === dept.id)
      .map((e) => roleNodes.find((r) => r.id === e.target))
      .filter(Boolean);

    deptRoles.forEach((role, ri) => {
      if (!role) return;
      nodes.push({
        id: role.id,
        position: { x: x + ri * roleSpacing - ((deptRoles.length - 1) * roleSpacing) / 2, y: 120 },
        data: { label: `${role.label}\nL${role.data.level || "?"}` },
        style: {
          background: "#18181b",
          border: "1px solid #3f3f46",
          borderRadius: 8,
          padding: 10,
          color: "#a1a1aa",
          fontSize: 12,
          whiteSpace: "pre-line" as const,
          textAlign: "center" as const,
        },
      });

      // Find people connected to this role
      const rolePeople = graph.edges
        .filter((e) => e.source === role.id)
        .map((e) => personNodes.find((p) => p.id === e.target))
        .filter(Boolean);

      rolePeople.forEach((person, pi) => {
        if (!person) return;
        const fitScore = person.data.fit_score as number | null;
        const burnout = person.data.burnout_risk as number;
        const morale = person.data.morale as number;
        const departed = person.data.departed as boolean;

        const borderColor = departed
          ? "#71717a"
          : fitScore !== null && fitScore !== undefined
            ? fitScore >= 0.7
              ? "#10b981"
              : fitScore >= 0.4
                ? "#f59e0b"
                : "#ef4444"
            : "#52525b";

        const moraleIcon = morale >= 0.7 ? "" : morale >= 0.4 ? " ⚡" : " ⚠";

        nodes.push({
          id: person.id,
          position: {
            x: x + ri * roleSpacing - ((deptRoles.length - 1) * roleSpacing) / 2 + pi * 160 - ((rolePeople.length - 1) * 160) / 2,
            y: 250,
          },
          data: {
            label: departed
              ? `${person.label}\n(departed)`
              : `${person.label}\n${fitScore !== null && fitScore !== undefined ? `Fit: ${(fitScore * 100).toFixed(0)}` : ""}${burnout > 0.3 ? ` · 🔥${(burnout * 100).toFixed(0)}%` : ""}${moraleIcon}`,
          },
          style: {
            background: departed ? "#27272a" : "#18181b",
            border: `2px ${departed ? "dashed" : "solid"} ${borderColor}`,
            borderRadius: 10,
            padding: 8,
            color: departed ? "#71717a" : "#e4e4e7",
            fontSize: 11,
            whiteSpace: "pre-line" as const,
            textAlign: "center" as const,
            opacity: departed ? 0.5 : 1,
          },
        });
      });
    });
  });

  return nodes;
}

function mapToFlowEdges(graph: GraphResponse): Edge[] {
  return graph.edges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    style: { stroke: "#3f3f46" },
    animated: e.label === "assigned",
  }));
}

export function OrgPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  useEffect(() => {
    api.getGraph().then((graph) => {
      setNodes(mapToFlowNodes(graph));
      setEdges(mapToFlowEdges(graph));
    });
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-zinc-100">Organization</h1>
      <div className="h-[calc(100vh-160px)] bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#27272a" gap={20} />
          <Controls
            style={{ background: "#18181b", border: "1px solid #3f3f46", borderRadius: 8 }}
          />
          <MiniMap
            style={{ background: "#18181b", border: "1px solid #3f3f46" }}
            nodeColor="#3f3f46"
          />
        </ReactFlow>
      </div>
    </div>
  );
}
