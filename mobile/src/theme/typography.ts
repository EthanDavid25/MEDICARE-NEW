export const Typography = {
  // Named style presets
  h1: { fontSize: 24, fontWeight: "700" as const, lineHeight: 30 },
  h2: { fontSize: 20, fontWeight: "700" as const, lineHeight: 26 },
  h3: { fontSize: 16, fontWeight: "600" as const, lineHeight: 22 },
  body1: { fontSize: 14, fontWeight: "400" as const, lineHeight: 20 },
  body2: { fontSize: 13, fontWeight: "400" as const, lineHeight: 18 },
  caption: { fontSize: 12, fontWeight: "400" as const, lineHeight: 16 },
  small: { fontSize: 11, fontWeight: "400" as const, lineHeight: 14 },
  button: { fontSize: 14, fontWeight: "600" as const, lineHeight: 18 },

  // Granular values for responsive styles
  fontSize: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
    xxl: 24
  },
  fontWeight: {
    normal: "400" as const,
    medium: "500" as const,
    semiBold: "600" as const,
    bold: "700" as const
  }
};
