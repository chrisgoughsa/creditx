import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f5f7ff",
          100: "#e6ecff",
          200: "#c4d0ff",
          300: "#9cb0ff",
          400: "#6c86ff",
          500: "#3f5cff",
          600: "#1f3fff",
          700: "#112ff1",
          800: "#1126c0",
          900: "#101f96",
        },
      },
      boxShadow: {
        card: "0 10px 30px -12px rgba(15, 23, 42, 0.25)",
      },
    },
  },
  plugins: [],
};

export default config;
