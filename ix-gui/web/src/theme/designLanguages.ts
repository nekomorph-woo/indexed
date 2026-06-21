/**
 * 设计语言 token —— 从 indexed `_shared/design-languages/<id>/meta.md` 提炼。
 *
 * 每个设计语言的 meta.md 都有「Token 摘要」表（主色/背景/表面/字体/形状/动效）。
 * 这里是 GUI 内置的 6 种皮肤，token 被注入为 CSS 变量（见 tokens.css 与 themeStore）。
 *
 * 真相源仍是 _shared/design-languages/；Tauri 阶段会改为运行时读 meta.md/prompt.md 动态解析，
 * 但 web 阶段用这套固化值足够展示主题切换能力。
 */
export interface DesignLanguage {
  id: string;
  name: string;
  tags: string[];
  tokens: {
    primary: string;
    bg: string;
    surface: string;
    surfaceAlt: string;
    text: string;
    textMuted: string;
    border: string;
    accent: string;
    danger: string;
    radius: string; // 卡片圆角
    radiusPill: string;
    fontFamily: string;
    easing: string;
    monoFontFamily: string;
    // 状态色（随主题切换；StatusDot / Badge / Agent 执行结果用）
    success: string;
    warning: string;
    // 阴影（Card / 浮层用；industrial 是 neumorphic 双阴影）
    shadow: string;
    shadowHover: string;
    // 辅助形状与布局
    radiusSm: string; // 输入框/小卡片圆角
    sidebarW: string; // 左侧资产树宽度
    headerH: string; // 顶部导航高度
  };
}

export const designLanguages: Record<string, DesignLanguage> = {
  "material-you": {
    id: "material-you",
    name: "Material You (Material Design 3)",
    tags: ["consumer", "rounded", "tonal-surface"],
    tokens: {
      primary: "#6750A4",
      bg: "#FFFBFE",
      surface: "#F3EDF7",
      surfaceAlt: "#E7E0EC",
      text: "#1D1B20",
      textMuted: "#49454F",
      border: "#CAC4D0",
      accent: "#6750A4",
      danger: "#B3261E",
      radius: "24px",
      radiusPill: "999px",
      fontFamily: "Roboto, system-ui, sans-serif",
      easing: "cubic-bezier(0.2, 0, 0, 1)",
      monoFontFamily: "ui-monospace, SFMono-Regular, monospace",
      success: "#2E7D32",
      warning: "#ED6C02",
      shadow: "0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04)",
      shadowHover: "0 4px 12px rgba(0,0,0,0.12)",
      radiusSm: "12px",
      sidebarW: "260px",
      headerH: "48px",
    },
  },
  bauhaus: {
    id: "bauhaus",
    name: "包豪斯几何构成",
    tags: ["geometric", "primary-colors", "hard-shadow"],
    tokens: {
      // 对齐 meta.md 包豪斯三原色：红 #D02020 / 蓝 #1040C0 / 黄 #F0C020
      primary: "#D02020",
      bg: "#F1FAEE",
      surface: "#FFFFFF",
      surfaceAlt: "#E63946",
      text: "#1D1B20",
      textMuted: "#457B9D",
      border: "#1D1B20",
      accent: "#F0C020",
      danger: "#D02020",
      radius: "0px",
      radiusPill: "0px",
      fontFamily: "'Helvetica Neue', Arial, sans-serif",
      easing: "cubic-bezier(0, 0, 1, 1)",
      monoFontFamily: "'Courier New', monospace",
      success: "#2A9D8F",
      warning: "#F4D35E",
      // 硬阴影（无模糊，纯偏移）是包豪斯海报风的标志
      shadow: "4px 4px 0 #1D1B20",
      shadowHover: "8px 8px 0 #1D1B20",
      radiusSm: "0px",
      sidebarW: "240px",
      headerH: "56px",
    },
  },
  newsprint: {
    id: "newsprint",
    name: "报刊编辑",
    tags: ["serif", "grid", "editorial"],
    tokens: {
      // 对齐 meta.md：墨 #111111 / 编辑红 #CC0000
      primary: "#1A1A1A",
      bg: "#F5F1E8",
      surface: "#FFFEF7",
      surfaceAlt: "#E8E2D0",
      text: "#111111",
      textMuted: "#5A5A5A",
      border: "#1A1A1A",
      accent: "#CC0000",
      danger: "#CC0000",
      radius: "2px",
      radiusPill: "0px",
      fontFamily: "Georgia, 'Times New Roman', serif",
      easing: "ease-in-out",
      monoFontFamily: "'Courier New', monospace",
      success: "#2D4A2D",
      warning: "#6B3A00",
      // 报刊用极轻阴影（几乎是线条），符合纸面感
      shadow: "0 1px 0 rgba(0,0,0,0.1)",
      shadowHover: "0 2px 4px rgba(0,0,0,0.15)",
      radiusSm: "2px",
      sidebarW: "280px",
      headerH: "48px",
    },
  },
  "flat-design": {
    id: "flat-design",
    name: "扁平色块",
    tags: ["flat", "saas", "no-shadow"],
    tokens: {
      primary: "#2563EB",
      bg: "#FFFFFF",
      surface: "#F8FAFC",
      surfaceAlt: "#E2E8F0",
      text: "#0F172A",
      textMuted: "#64748B",
      border: "#CBD5E1",
      accent: "#0EA5E9",
      danger: "#EF4444",
      radius: "8px",
      radiusPill: "6px",
      fontFamily: "Inter, system-ui, sans-serif",
      easing: "ease",
      monoFontFamily: "ui-monospace, SFMono-Regular, monospace",
      success: "#10B981",
      warning: "#F59E0B",
      // 扁平风：阴影极轻，几乎不可见
      shadow: "0 1px 2px rgba(0,0,0,0.05)",
      shadowHover: "0 2px 4px rgba(0,0,0,0.08)",
      radiusSm: "6px",
      sidebarW: "260px",
      headerH: "48px",
    },
  },
  "hand-drawn": {
    id: "hand-drawn",
    name: "手绘歪边",
    tags: ["sketch", "sticky-note", "paper-cutout"],
    tokens: {
      primary: "#264653",
      bg: "#FFF9E6",
      surface: "#FFFDF0",
      surfaceAlt: "#FFE8A3",
      text: "#264653",
      textMuted: "#6B7280",
      border: "#264653",
      accent: "#E76F51",
      danger: "#E76F51",
      // 不规则圆角是手绘风的故意效果
      radius: "12px 4px 12px 4px",
      radiusPill: "999px",
      fontFamily: "'Comic Sans MS', 'Segoe Print', cursive",
      easing: "cubic-bezier(0.34, 1.56, 0.64, 1)",
      monoFontFamily: "'Courier New', monospace",
      success: "#6A994E",
      warning: "#F4A261",
      // 偏移阴影像剪纸投影
      shadow: "2px 2px 0 rgba(38,70,83,0.2)",
      shadowHover: "3px 3px 0 rgba(38,70,83,0.3)",
      radiusSm: "4px",
      sidebarW: "260px",
      headerH: "52px",
    },
  },
  "industrial-skeuomorphism": {
    id: "industrial-skeuomorphism",
    name: "工业新拟态",
    tags: ["control-panel", "safety-orange", "neumorphism"],
    tokens: {
      // 对齐 meta.md：底盘 #E0E5EC 工业灰塑料（亮） / 强调 #FF4757 安全橙 / Inter / JetBrains Mono
      primary: "#FF4757",
      bg: "#E0E5EC",
      surface: "#F0F2F5",
      surfaceAlt: "#C5CAD3",
      text: "#1F2937",
      textMuted: "#6B7280",
      border: "#A8AEB8",
      accent: "#FF6B1A",
      danger: "#DC2626",
      radius: "4px",
      radiusPill: "2px",
      fontFamily: "'Inter', system-ui, sans-serif",
      easing: "cubic-bezier(0.4, 0, 0.2, 1)",
      monoFontFamily: "'JetBrains Mono', monospace",
      success: "#16A34A",
      warning: "#EA580C",
      // neumorphic 双阴影：左上亮源 + 右下暗源，制造塑料凸起感
      shadow: "6px 6px 12px rgba(0,0,0,0.2), -6px -6px 12px rgba(255,255,255,0.7)",
      shadowHover: "inset 3px 3px 6px rgba(0,0,0,0.2), inset -3px -3px 6px rgba(255,255,255,0.5)",
      radiusSm: "4px",
      sidebarW: "260px",
      headerH: "52px",
    },
  },
};

export const designLanguageList = Object.values(designLanguages);
