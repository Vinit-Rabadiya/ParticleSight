import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Expose VITE_API_URL to the frontend bundle
  // Set this env var in Vercel to point at the Render backend URL
});
