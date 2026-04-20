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
      },
      colors: {
        brand: {
          50: "#effafc",
          100: "#d8f3f8",
          200: "#b4e7f1",
          300: "#7dd4e3",
          400: "#43bed1",
          500: "#1e9db5",
          600: "#1a7f96",
          700: "#19667a",
          800: "#1a5465",
          900: "#1a4755",
        },
        slateink: {
          950: "#0f172a",
        },
      },
    },
  },
  plugins: [],
}
