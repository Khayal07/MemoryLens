import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// In Docker the API is reachable as the `api` service, not localhost. Override
// with VITE_API_PROXY; default to localhost for running the dev server natively.
const apiTarget = process.env.VITE_API_PROXY ?? "http://localhost:8000";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": apiTarget,
    },
    // Bind-mounted source on a Windows/WSL host doesn't emit inotify events into
    // the Linux container, so Vite never sees edits and serves stale transforms.
    // Poll for changes so HMR actually works under Docker Desktop.
    watch: { usePolling: true, interval: 300 },
  },
});
