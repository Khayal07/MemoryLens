import { useQuery } from "@tanstack/react-query";
import {
  forceCenter,
  forceCollide,
  forceLink,
  forceManyBody,
  forceSimulation,
  type SimulationLinkDatum,
  type SimulationNodeDatum,
} from "d3-force";
import { m, useReducedMotion } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";
import PosterPlaceholder from "../components/PosterPlaceholder";
import EmptyState from "../components/ui/EmptyState";
import Eyebrow from "../components/ui/Eyebrow";
import Skeleton from "../components/ui/Skeleton";
import { developIn, stagger } from "../components/motion/variants";
import { api } from "../lib/api";
import type { ConstellationNode } from "../lib/types";

const W = 900;
const H = 560;

/** Star colour per category — matches the app's category identities. */
const COLORS: Record<string, string> = {
  movies: "#7c6bf5",
  tv: "#6b8af5",
  songs: "#f5b468",
  books: "#67d4e0",
  games: "#7ce08a",
  actors: "#e07cc3",
};
const FALLBACK_COLOR = "#9a93c9";

interface SimNode extends SimulationNodeDatum {
  data: ConstellationNode;
}
type SimLink = SimulationLinkDatum<SimNode> & { weight: number };

/** Memory Constellation — everything the user has found or saved as a star map:
 *  glowing category-coloured nodes sized by how often they surfaced, linked by
 *  embedding similarity. Free-form (AI-named) finds float unlinked on purpose. */
export default function Constellation() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["constellation"],
    queryFn: api.constellation,
  });
  const reduce = useReducedMotion();
  const [nodes, setNodes] = useState<SimNode[]>([]);
  const [links, setLinks] = useState<SimLink[]>([]);
  const [hovered, setHovered] = useState<SimNode | null>(null);
  const simRef = useRef<ReturnType<typeof forceSimulation<SimNode>> | null>(null);

  // Pan/zoom is just the SVG viewBox — nothing else has to know about it.
  const [view, setView] = useState({ x: 0, y: 0, w: W, h: H });
  const viewRef = useRef(view);
  viewRef.current = view;
  const svgRef = useRef<SVGSVGElement | null>(null);
  const dragRef = useRef<{ px: number; py: number } | null>(null);
  // Distance dragged since pointerdown — suppresses the click-through on release.
  const movedRef = useRef(0);

  const MIN_W = W / 5; // 5× max zoom-in
  const MAX_W = W * 2.5; // 2.5× max zoom-out

  function zoomBy(factor: number, cx?: number, cy?: number) {
    setView((v) => {
      const w = Math.min(MAX_W, Math.max(MIN_W, v.w * factor));
      const h = w * (H / W);
      const fx = cx ?? v.x + v.w / 2;
      const fy = cy ?? v.y + v.h / 2;
      // Keep the focus point stationary while the box scales around it.
      const kx = (fx - v.x) / v.w;
      const ky = (fy - v.y) / v.h;
      return { x: fx - kx * w, y: fy - ky * h, w, h };
    });
  }

  // Wheel zoom needs a native non-passive listener to preventDefault page scroll.
  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const rect = svg.getBoundingClientRect();
      const v = viewRef.current;
      const cx = v.x + ((e.clientX - rect.left) / rect.width) * v.w;
      const cy = v.y + ((e.clientY - rect.top) / rect.height) * v.h;
      zoomBy(e.deltaY > 0 ? 1.15 : 1 / 1.15, cx, cy);
    };
    svg.addEventListener("wheel", onWheel, { passive: false });
    return () => svg.removeEventListener("wheel", onWheel);
  }, [nodes.length > 0]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!data || data.nodes.length === 0) return;
    const simNodes: SimNode[] = data.nodes.map((n, i) => ({
      data: n,
      x: W / 2 + Math.cos((i / data.nodes.length) * 2 * Math.PI) * 180,
      y: H / 2 + Math.sin((i / data.nodes.length) * 2 * Math.PI) * 140,
    }));
    const byId = new Map(simNodes.map((n) => [n.data.id, n]));
    const simLinks: SimLink[] = data.edges
      .filter((e) => byId.has(e.a) && byId.has(e.b))
      .map((e) => ({ source: byId.get(e.a)!, target: byId.get(e.b)!, weight: e.weight }));

    const sim = forceSimulation<SimNode>(simNodes)
      .force(
        "link",
        forceLink<SimNode, SimLink>(simLinks)
          .distance((l) => 170 - l.weight * 90)
          .strength((l) => 0.25 + l.weight * 0.4),
      )
      .force("charge", forceManyBody().strength(-130))
      .force("center", forceCenter(W / 2, H / 2))
      .force("collide", forceCollide(34))
      .on("tick", () => {
        setNodes([...simNodes]);
        setLinks([...simLinks]);
      });
    simRef.current = sim;

    if (reduce) {
      sim.stop();
      sim.tick(300); // settle instantly, render static
      setNodes([...simNodes]);
      setLinks([...simLinks]);
    } else {
      // Never fully freeze — a faint ambient drift keeps the sky alive.
      sim.alphaTarget(0.02).restart();
    }
    return () => void sim.stop();
  }, [data, reduce]);

  const color = (n: SimNode) => COLORS[n.data.category] ?? FALLBACK_COLOR;
  const radius = (n: SimNode) => 7 + Math.min(n.data.seen_count, 5) * 2;
  const legend = useMemo(
    () => [...new Set(nodes.map((n) => n.data.category))],
    [nodes],
  );

  return (
    <div>
      <m.section variants={stagger(0.08)} initial="hidden" animate="show" className="mb-6">
        <m.div variants={developIn}>
          <Eyebrow>Your sky</Eyebrow>
        </m.div>
        <m.h1
          variants={developIn}
          className="mt-2 font-display text-[2rem] font-bold tracking-[-0.02em]"
        >
          Memory Constellation
        </m.h1>
        <m.p variants={developIn} className="mt-2 max-w-[520px] text-[0.92rem] text-muted">
          Every find becomes a star — colour is its category, size how often it surfaced,
          lines link memories that feel alike. Lone stars are AI-named finds outside the
          catalog.
        </m.p>
      </m.section>

      {isLoading && <Skeleton className="h-[480px]" />}
      {isError && <EmptyState title="Couldn't chart your constellation." />}
      {data && data.nodes.length === 0 && (
        <EmptyState
          title="No stars yet."
          hint="Search for a few memories and they'll appear here."
        />
      )}

      {nodes.length > 0 && (
        <div className="glass relative overflow-hidden rounded-lens">
          <svg
            ref={svgRef}
            viewBox={`${view.x} ${view.y} ${view.w} ${view.h}`}
            className={`block h-auto w-full touch-none ${dragRef.current ? "cursor-grabbing" : "cursor-grab"}`}
            role="img"
            aria-label="Star map of your found items"
            onPointerDown={(e) => {
              e.currentTarget.setPointerCapture(e.pointerId);
              dragRef.current = { px: e.clientX, py: e.clientY };
              movedRef.current = 0;
            }}
            onPointerMove={(e) => {
              const d = dragRef.current;
              if (!d) return;
              const rect = e.currentTarget.getBoundingClientRect();
              const dx = ((e.clientX - d.px) / rect.width) * view.w;
              const dy = ((e.clientY - d.py) / rect.height) * view.h;
              movedRef.current += Math.abs(e.clientX - d.px) + Math.abs(e.clientY - d.py);
              d.px = e.clientX;
              d.py = e.clientY;
              setView((v) => ({ ...v, x: v.x - dx, y: v.y - dy }));
            }}
            onPointerUp={() => (dragRef.current = null)}
            onPointerLeave={() => (dragRef.current = null)}
          >
            {links.map((l, i) => {
              const s = l.source as SimNode;
              const t = l.target as SimNode;
              return (
                <line
                  key={i}
                  x1={s.x}
                  y1={s.y}
                  x2={t.x}
                  y2={t.y}
                  stroke="rgba(124,107,245,0.9)"
                  strokeOpacity={0.12 + l.weight * 0.45}
                  strokeWidth={0.6 + l.weight * 1.6}
                />
              );
            })}
            {nodes.map((n) => (
              <g
                key={n.data.id}
                transform={`translate(${n.x},${n.y})`}
                className="cursor-pointer"
                onMouseEnter={() => setHovered(n)}
                onMouseLeave={() => setHovered((h) => (h?.data.id === n.data.id ? null : h))}
                onClick={() => {
                  // A drag that ended on a node is not a click.
                  if (movedRef.current > 6) return;
                  if (n.data.source_url) window.open(n.data.source_url, "_blank");
                }}
              >
                <circle
                  r={radius(n) * 2.4}
                  fill={color(n)}
                  opacity={hovered?.data.id === n.data.id ? 0.28 : 0.12}
                />
                <circle
                  r={radius(n)}
                  fill={color(n)}
                  style={{ filter: `drop-shadow(0 0 ${radius(n)}px ${color(n)})` }}
                />
                <circle r={radius(n) * 0.45} fill="rgba(255,255,255,0.85)" />
              </g>
            ))}
          </svg>

          {hovered && (
            <div
              className="glass-strong pointer-events-none absolute z-10 flex w-[220px] items-center gap-3 rounded-xl p-3"
              style={{
                left: `min(max(${(((hovered.x ?? 0) - view.x) / view.w) * 100}%, 2%), 72%)`,
                top: `min(max(${(((hovered.y ?? 0) - view.y) / view.h) * 100 + 4}%, 2%), 78%)`,
              }}
            >
              {hovered.data.image_url ? (
                <img
                  src={hovered.data.image_url}
                  alt=""
                  className="h-[72px] w-[50px] rounded-md border border-glass-line object-cover"
                />
              ) : (
                <PosterPlaceholder posterSize="h-[72px] w-[50px]" />
              )}
              <div className="min-w-0">
                <div className="truncate text-[0.9rem] font-semibold">{hovered.data.title}</div>
                <div className="mt-0.5 font-mono text-[0.7rem] text-faint">
                  {hovered.data.category} · seen ×{hovered.data.seen_count}
                </div>
              </div>
            </div>
          )}

          <div className="absolute right-3 top-3 flex flex-col gap-1.5">
            {[
              { label: "Zoom in", glyph: "＋", action: () => zoomBy(1 / 1.3) },
              { label: "Zoom out", glyph: "−", action: () => zoomBy(1.3) },
              { label: "Reset view", glyph: "⌂", action: () => setView({ x: 0, y: 0, w: W, h: H }) },
            ].map((b) => (
              <button
                key={b.label}
                type="button"
                onClick={b.action}
                aria-label={b.label}
                title={b.label}
                className="glass flex h-9 w-9 items-center justify-center rounded-[10px] text-[1rem]
                  text-muted transition-colors hover:border-violet/50 hover:text-ink"
              >
                {b.glyph}
              </button>
            ))}
          </div>

          <div className="pointer-events-none absolute bottom-3 left-4 flex flex-wrap gap-3">
            {legend.map((cat) => (
              <span key={cat} className="flex items-center gap-1.5 font-mono text-[0.7rem] text-faint">
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ background: COLORS[cat] ?? FALLBACK_COLOR }}
                  aria-hidden="true"
                />
                {cat}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
