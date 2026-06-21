/**
 * 共享 UI 原语。全部用 CSS 变量（设计令牌），随主题切换自动适配 6 种设计语言。
 */
import { CSSProperties, ReactNode } from "react";

export function Button({
  children,
  variant = "default",
  size = "md",
  disabled,
  onClick,
  title,
  style,
}: {
  children: ReactNode;
  variant?: "default" | "primary" | "danger" | "ghost";
  size?: "sm" | "md";
  disabled?: boolean;
  onClick?: () => void;
  title?: string;
  style?: CSSProperties;
}) {
  const bg = {
    default: "var(--ix-surface-alt)",
    primary: "var(--ix-primary)",
    danger: "var(--ix-danger)",
    ghost: "transparent",
  }[variant];
  const color = variant === "primary" || variant === "danger" ? "#fff" : "var(--ix-text)";
  const border = variant === "ghost" ? "1px solid transparent" : "1px solid var(--ix-border)";
  return (
    <button
      title={title}
      disabled={disabled}
      onClick={onClick}
      style={{
        background: bg,
        color,
        border,
        borderRadius: "var(--ix-radius-pill)",
        padding: size === "sm" ? "4px 12px" : "8px 18px",
        fontSize: size === "sm" ? "12px" : "14px",
        fontWeight: 500,
        opacity: disabled ? 0.5 : 1,
        transition: "all 0.2s var(--ix-easing)",
        ...style,
      }}
    >
      {children}
    </button>
  );
}

export function Card({ children, style }: { children: ReactNode; style?: CSSProperties }) {
  return (
    <div
      style={{
        background: "var(--ix-surface)",
        border: "1px solid var(--ix-border)",
        borderRadius: "var(--ix-radius)",
        boxShadow: "var(--ix-shadow)",
        ...style,
      }}
    >
      {children}
    </div>
  );
}

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: "neutral" | "success" | "warning" | "danger" | "primary";
}) {
  const color = {
    neutral: "var(--ix-text-muted)",
    success: "var(--ix-success)",
    warning: "var(--ix-warning)",
    danger: "var(--ix-danger)",
    primary: "var(--ix-primary)",
  }[tone];
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 10px",
        borderRadius: "var(--ix-radius-pill)",
        fontSize: "11px",
        fontWeight: 600,
        color,
        background: "color-mix(in srgb, currentColor 14%, transparent)",
        border: `1px solid color-mix(in srgb, ${color} 40%, transparent)`,
      }}
    >
      {children}
    </span>
  );
}

export function StatusDot({ status }: { status: "running" | "completed" | "failed" }) {
  const c = status === "completed" ? "var(--ix-success)" : status === "failed" ? "var(--ix-danger)" : "var(--ix-warning)";
  return (
    <span
      style={{
        display: "inline-block",
        width: 10,
        height: 10,
        borderRadius: "var(--ix-radius-pill)",
        background: c,
        boxShadow: status === "running" ? `0 0 0 0 ${c}` : "none",
        animation: status === "running" ? "ix-pulse 1.4s infinite" : "none",
      }}
    />
  );
}

export function Spinner({ size = 16 }: { size?: number }) {
  return (
    <span
      style={{
        display: "inline-block",
        width: size,
        height: size,
        border: "2px solid var(--ix-border)",
        borderTopColor: "var(--ix-primary)",
        borderRadius: "var(--ix-radius-pill)",
        animation: "ix-spin 0.7s linear infinite",
      }}
    />
  );
}

export function EmptyState({ icon, title, hint }: { icon: string; title: string; hint?: string }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 8,
        padding: "48px 24px",
        color: "var(--ix-text-muted)",
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: 40, opacity: 0.5 }}>{icon}</div>
      <div style={{ fontSize: 15, fontWeight: 500, color: "var(--ix-text)" }}>{title}</div>
      {hint && <div style={{ fontSize: 13 }}>{hint}</div>}
    </div>
  );
}

export function Field({
  label,
  required,
  hint,
  children,
}: {
  label: string;
  required?: boolean;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <span style={{ fontSize: 13, fontWeight: 500, color: "var(--ix-text)" }}>
        {label}
        {required && <span style={{ color: "var(--ix-danger)", marginLeft: 4 }}>*</span>}
      </span>
      {children}
      {hint && <span style={{ fontSize: 12, color: "var(--ix-text-muted)" }}>{hint}</span>}
    </label>
  );
}

export const inputStyle: CSSProperties = {
  background: "var(--ix-bg)",
  color: "var(--ix-text)",
  border: "1px solid var(--ix-border)",
  borderRadius: "var(--ix-radius-sm)",
  padding: "8px 12px",
  fontSize: 14,
  fontFamily: "var(--ix-font)",
  width: "100%",
  outline: "none",
};

export function Tabs({
  tabs,
  active,
  onChange,
}: {
  tabs: { id: string; label: string }[];
  active: string;
  onChange: (id: string) => void;
}) {
  return (
    <div style={{ display: "flex", gap: 4, borderBottom: "1px solid var(--ix-border)" }}>
      {tabs.map((t) => (
        <button
          key={t.id}
          onClick={() => onChange(t.id)}
          style={{
            background: "transparent",
            border: "none",
            borderBottom: active === t.id ? "2px solid var(--ix-primary)" : "2px solid transparent",
            color: active === t.id ? "var(--ix-primary)" : "var(--ix-text-muted)",
            padding: "10px 16px",
            fontSize: 13,
            fontWeight: 500,
            transition: "all 0.2s var(--ix-easing)",
          }}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}
