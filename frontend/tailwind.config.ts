import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        buy: "#16a34a",
        sell: "#dc2626",
        hold: "#6b7280"
      }
    }
  },
  plugins: []
};

export default config;
