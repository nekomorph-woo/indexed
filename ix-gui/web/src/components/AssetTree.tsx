/**
 * 资产树 —— 只读展示 indexed 五桶结构（零侵入铁律：纯读，不写）。
 * 通过 backend.workspace.readWorkspaceTree() 调 Rust WorkspaceIo 扫描真实磁盘。
 */
import { useEffect, useState } from "react";
import { backend } from "@/api/backend";
import type { TreeNode } from "@/api/contract";
import { Spinner } from "./ui";

function NodeIcon({ node }: { node: TreeNode }) {
  if (node.kind === "bucket") return <span>🪣</span>;
  if (node.kind === "file") {
    if (node.name.endsWith(".yaml") || node.name.endsWith(".yml")) return <span>⚙️</span>;
    if (node.name.endsWith(".md")) return <span>📄</span>;
    if (node.name.endsWith(".py")) return <span>🐍</span>;
    if (node.name.endsWith(".html")) return <span>🌐</span>;
    return <span>📃</span>;
  }
  return <span>📁</span>;
}

function TreeNodeRow({
  node,
  depth,
  selected,
  onSelect,
}: {
  node: TreeNode;
  depth: number;
  selected: string | null;
  onSelect: (path: string) => void;
}) {
  const [open, setOpen] = useState(depth < 2);
  const hasChildren = node.children && node.children.length > 0;
  const isSelected = selected === node.path;

  return (
    <div>
      <div
        onClick={() => onSelect(node.path)}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 6,
          padding: "4px 8px",
          paddingLeft: depth * 16 + 8,
          cursor: "pointer",
          borderRadius: "var(--ix-radius-sm)",
          background: isSelected ? "color-mix(in srgb, var(--ix-primary) 14%, transparent)" : "transparent",
          color: isSelected ? "var(--ix-primary)" : "var(--ix-text)",
          fontWeight: node.kind === "bucket" ? 600 : 400,
          fontSize: 13,
          transition: "background 0.15s var(--ix-easing)",
        }}
        onMouseEnter={(e) => {
          if (!isSelected) e.currentTarget.style.background = "var(--ix-surface-alt)";
        }}
        onMouseLeave={(e) => {
          if (!isSelected) e.currentTarget.style.background = "transparent";
        }}
      >
        {hasChildren ? (
          <span
            onClick={(e) => {
              e.stopPropagation();
              setOpen(!open);
            }}
            style={{ width: 12, display: "inline-block", color: "var(--ix-text-muted)", userSelect: "none" }}
          >
            {open ? "▾" : "▸"}
          </span>
        ) : (
          <span style={{ width: 12 }} />
        )}
        <NodeIcon node={node} />
        <span>{node.name}</span>
      </div>
      {open &&
        hasChildren &&
        node.children!.map((c: TreeNode) => (
          <TreeNodeRow key={c.path} node={c} depth={depth + 1} selected={selected} onSelect={onSelect} />
        ))}
    </div>
  );
}

export function AssetTree({ onSelect }: { onSelect: (path: string) => void }) {
  const [tree, setTree] = useState<TreeNode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    backend.workspace
      .readWorkspaceTree()
      .then(setTree)
      .catch((e) => setError(String(e)));
  }, []);

  const handleSelect = (path: string) => {
    setSelected(path);
    onSelect(path);
  };

  if (error)
    return <div style={{ padding: 16, color: "var(--ix-danger)", fontSize: 13 }}>加载失败: {error}</div>;
  if (!tree)
    return (
      <div style={{ padding: 16 }}>
        <Spinner />
      </div>
    );

  return (
    <div style={{ padding: "8px 6px", overflowY: "auto", height: "100%" }}>
      <TreeNodeRow node={tree} depth={0} selected={selected} onSelect={handleSelect} />
    </div>
  );
}
