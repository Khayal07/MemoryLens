import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In Docker the API is reachable as the `api` service, not localhost. Override
// with VITE_API_PROXY; default to localhost for running the dev server natively.
const apiTarget = process.env.VITE_API_PROXY ?? "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": apiTarget,
    },
  },
});
