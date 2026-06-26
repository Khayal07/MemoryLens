import { useEffect, useState } from "react";

export default function App() {
  const [apiStatus, setApiStatus] = useState<string>("checking…");

  useEffect(() => {
    fetch("/api/v1/health")
      .then((r) => r.json())
      .then((d) => setApiStatus(d.status))
      .catch(() => setApiStatus("unreachable"));
  }, []);

  return (
    <main className="app">
      <h1>MemoryLens</h1>
      <p>Find things you only partially remember.</p>
      <p className="status">API: {apiStatus}</p>
    </main>
  );
}
