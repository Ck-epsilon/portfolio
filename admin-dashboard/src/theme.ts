// Author: Ck.epsilon & Chaos (AI Programming Assistant)
/** ε-style theme for React-Admin.
 *
 *  Design philosophy: precision over decoration.
 *  - Spacing: 8px grid, no arbitrary padding
 *  - Typography: system font stack, one weight hierarchy
 *  - Color: blue primary, neutral grays, semantic green/red/orange
 *  - Surfaces: subtle elevation via shadow, not borders
 */

import { defaultTheme } from "react-admin";

export const epsilonTheme = {
  ...defaultTheme,
  palette: {
    mode: "light" as const,
    primary: { main: "#0071e3" },
    secondary: { main: "#86868b" },
    background: { default: "#f5f5f7", paper: "#ffffff" },
    error: { main: "#ff3b30" },
    warning: { main: "#ff9500" },
    success: { main: "#34c759" },
    info: { main: "#0071e3" },
    text: {
      primary: "#1d1d1f",
      secondary: "#6e6e73",
      disabled: "#aeaeb2",
    },
  },
  typography: {
    fontFamily: [
      "-apple-system",
      "BlinkMacSystemFont",
      '"SF Pro Text"',
      '"Helvetica Neue"',
      "sans-serif",
    ].join(","),
    fontSize: 14,
    h1: { fontSize: 28, fontWeight: 700, letterSpacing: "-0.022em" },
    h2: { fontSize: 22, fontWeight: 600, letterSpacing: "-0.02em" },
    h3: { fontSize: 17, fontWeight: 600, letterSpacing: "-0.018em" },
    h4: { fontSize: 15, fontWeight: 600 },
    h5: { fontSize: 13, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.04em" },
    h6: { fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em" },
    body1: { fontSize: 15, lineHeight: 1.47, letterSpacing: "-0.015em" },
    body2: { fontSize: 13, lineHeight: 1.45 },
    button: { fontWeight: 500, letterSpacing: "-0.01em" },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { textTransform: "none", borderRadius: 10, padding: "6px 18px" },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06)",
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: { borderBottom: "1px solid rgba(0,0,0,0.06)" },
      },
    },
    RaDatagrid: {
      styleOverrides: {
        root: {
          "& .RaDatagrid-headerCell": {
            fontWeight: 600,
            fontSize: 12,
            textTransform: "uppercase" as const,
            letterSpacing: "0.03em",
            color: "#6e6e73",
          },
        },
      },
    },
    RaMenuItemLink: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          margin: "2px 8px",
        },
      },
    },
  },
};

export const epsilonDarkTheme = {
  ...epsilonTheme,
  palette: {
    ...epsilonTheme.palette,
    mode: "dark" as const,
    background: { default: "#000000", paper: "#1c1c1e" },
    text: {
      primary: "#f5f5f7",
      secondary: "#98989d",
      disabled: "#636366",
    },
  },
  components: {
    ...epsilonTheme.components,
    MuiCard: {
      styleOverrides: {
        root: {
          ...epsilonTheme.components?.MuiCard?.styleOverrides?.root,
          boxShadow: "none",
          border: "1px solid rgba(255,255,255,0.08)",
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: { borderBottom: "1px solid rgba(255,255,255,0.06)" },
      },
    },
  },
};
