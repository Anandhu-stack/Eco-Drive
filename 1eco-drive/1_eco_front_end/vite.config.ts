import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  root: "./", // ✅ Ensures Vite looks in the correct folder
  server: {
    port: 5173,
  },
});
