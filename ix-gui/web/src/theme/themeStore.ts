/**
 * 主题状态：选中的设计语言 id（持久化到 localStorage）。
 * 应用 token → CSS 变量的注入。
 */
import { create } from "zustand";
import { designLanguages } from "./designLanguages";

const STORAGE_KEY = "ix-gui:design-language";

function loadInitial(): string {
  if (typeof localStorage !== "undefined") {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && designLanguages[saved]) return saved;
  }
  return "material-you";
}

interface ThemeState {
  current: string;
  setTheme: (id: string) => void;
}

export const useThemeStore = create<ThemeState>((set) => ({
  current: loadInitial(),
  setTheme: (id) => {
    if (!designLanguages[id]) return;
    localStorage.setItem(STORAGE_KEY, id);
    set({ current: id });
  },
}));

/** 把当前设计语言的 token 注入为 CSS 变量（root 上） */
export function applyTheme(id: string) {
  const dl = designLanguages[id];
  if (!dl) return;
  const root = document.documentElement;
  const t = dl.tokens;
  // 核心 13 个
  root.style.setProperty("--ix-primary", t.primary);
  root.style.setProperty("--ix-bg", t.bg);
  root.style.setProperty("--ix-surface", t.surface);
  root.style.setProperty("--ix-surface-alt", t.surfaceAlt);
  root.style.setProperty("--ix-text", t.text);
  root.style.setProperty("--ix-text-muted", t.textMuted);
  root.style.setProperty("--ix-border", t.border);
  root.style.setProperty("--ix-accent", t.accent);
  root.style.setProperty("--ix-danger", t.danger);
  root.style.setProperty("--ix-radius", t.radius);
  root.style.setProperty("--ix-radius-pill", t.radiusPill);
  root.style.setProperty("--ix-font", t.fontFamily);
  root.style.setProperty("--ix-easing", t.easing);
  // 状态色（StatusDot / Badge / 执行结果用，随主题切换）
  root.style.setProperty("--ix-success", t.success);
  root.style.setProperty("--ix-warning", t.warning);
  // 阴影（Card / 浮层用）
  root.style.setProperty("--ix-shadow", t.shadow);
  root.style.setProperty("--ix-shadow-hover", t.shadowHover);
  // 辅助形状与布局
  root.style.setProperty("--ix-radius-sm", t.radiusSm);
  root.style.setProperty("--ix-sidebar-w", t.sidebarW);
  root.style.setProperty("--ix-header-h", t.headerH);
  root.style.setProperty("--ix-font-mono", t.monoFontFamily);
}
