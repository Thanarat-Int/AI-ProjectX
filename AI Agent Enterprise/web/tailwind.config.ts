import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0a0d14",
        neon: "#6d7cff",
        cyan: "#00e6ff",
        magenta: "#ff2e93",
        electric: "#7dffb2"
      },
      boxShadow: {
        glow: "0 0 24px rgba(0,230,255,0.35), 0 0 60px rgba(109,124,255,0.25)"
      }
    }
  },
  plugins: []
};

export default config;
