module.exports = {
  content: [
    "./templates/**/*.html",
    "./apps/**/templates/**/*.html",
    "./assets/js/**/*.js",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "Segoe UI", "sans-serif"],
      },
      boxShadow: {
        shell: "0 20px 45px -30px rgba(15, 23, 42, 0.45)",
        card: "0 1px 2px 0 rgba(15, 23, 42, 0.04), 0 12px 30px -18px rgba(15, 23, 42, 0.25)",
        lift: "0 18px 40px -24px rgba(79, 70, 229, 0.45)",
      },
      colors: {
        brand: {
          50: "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
        },
        slateink: {
          950: "#0f172a",
        },
      },
      keyframes: {
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in-up": "fade-in-up 0.4s ease both",
      },
    },
  },
  plugins: [],
}
