import { useQuery } from "@tanstack/react-query";
import {
  m,
  useMotionValueEvent,
  useReducedMotion,
  useScroll,
  useTransform,
} from "framer-motion";
import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import useMediaQuery from "../lib/useMediaQuery";

/** Signed-out landing: a scroll-driven aperture story. Each scene is a tall wrapper
 *  with a sticky viewport; scroll progress drives the animation, so the story plays
 *  at the reader's pace. Reduced motion → everything renders settled. */

const SENTENCE = "twelve angry people arguing in one room over a verdict…";
const FINAL_CONFIDENCE = 87;

const FALLBACK_CATEGORIES = [
  { key: "movies", icon: "🎬", display_name: "Movies" },
  { key: "tv", icon: "📺", display_name: "TV Series" },
  { key: "songs", icon: "🎵", display_name: "Songs" },
  { key: "books", icon: "📚", display_name: "Books" },
  { key: "games", icon: "🎮", display_name: "Games" },
  { key: "actors", icon: "🎭", display_name: "Actors" },
];

/** Scene 1 — a giant aperture ring draws itself and irises open onto the title. */
function ApertureScene({ reduce, coarse }: { reduce: boolean; coarse: boolean }) {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end end"] });
  // Partial rings at rest so the first paint already reads as an aperture.
  const draw = useTransform(scrollYProgress, [0, 0.55], [0.22, 1]);
  const scale = useTransform(scrollYProgress, [0, 0.6], [1.55, 1]);
  const rotate = useTransform(scrollYProgress, [0, 1], [-40, 25]);
  const titleOpacity = useTransform(scrollYProgress, [0.18, 0.5], [0, 1]);
  const titleY = useTransform(scrollYProgress, [0.18, 0.5], [28, 0]);
  const hintOpacity = useTransform(scrollYProgress, [0, 0.12], [1, 0]);
  // Touch devices can't afford re-rasterizing a near-fullscreen SVG stroke every
  // frame: draw full rings and fade the whole svg in via composited opacity instead.
  const svgOpacity = useTransform(scrollYProgress, [0, 0.4], [0, 0.7]);
  const drawStyle = { pathLength: reduce || coarse ? 1 : draw };

  return (
    <div ref={ref} className={reduce ? "" : "relative h-[220vh]"}>
      <div
        className={`flex items-center justify-center overflow-hidden ${
          reduce ? "min-h-[70vh] py-20" : "sticky top-0 h-screen"
        }`}
      >
        <m.svg
          aria-hidden="true"
          viewBox="0 0 400 400"
          className="absolute h-[88vmin] w-[88vmin] opacity-70 will-change-transform"
          style={
            reduce
              ? undefined
              : coarse
                ? { scale, rotate, opacity: svgOpacity }
                : { scale, rotate }
          }
        >
          {/* Staggered start angles so partial draw reads as iris blades, not arcs. */}
          <m.circle
            cx="200" cy="200" r="180" fill="none"
            stroke="var(--color-violet)" strokeWidth="1.5" strokeLinecap="round"
            style={drawStyle}
          />
          <m.circle
            cx="200" cy="200" r="140" fill="none"
            stroke="var(--color-amber)" strokeWidth="1" strokeDasharray="3 10"
            transform="rotate(140 200 200)"
            style={drawStyle}
          />
          <m.circle
            cx="200" cy="200" r="102" fill="none"
            stroke="var(--color-violet-soft)" strokeWidth="2" strokeLinecap="round"
            transform="rotate(250 200 200)"
            style={drawStyle}
          />
        </m.svg>

        <m.div
          className="relative px-6 text-center"
          style={reduce ? undefined : { opacity: titleOpacity, y: titleY }}
        >
          <p className="mb-4 text-[0.85rem] font-semibold uppercase tracking-[0.2em] text-violet-soft">
            MemoryLens
          </p>
          <h1 className="font-display text-[clamp(2.8rem,8vw,5.2rem)] font-bold leading-[1.02] tracking-[-0.035em]">
            You almost have it.
            <br />
            <span className="bg-gradient-to-r from-violet-soft via-violet to-amber bg-clip-text text-transparent">
              Bring it into focus.
            </span>
          </h1>
        </m.div>

        {!reduce && (
          <m.p
            style={{ opacity: hintOpacity }}
            className="absolute bottom-10 text-[0.9rem] tracking-[0.12em] text-faint"
          >
            scroll to focus ↓
          </m.p>
        )}
      </div>
    </div>
  );
}

/** Scene 2 — a fuzzy memory types itself while the blurred answer develops sharp. */
function RecallScene({ reduce }: { reduce: boolean }) {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end end"] });
  const [chars, setChars] = useState(reduce ? SENTENCE.length : 0);
  const [conf, setConf] = useState(reduce ? FINAL_CONFIDENCE : 0);
  // Only re-render when the integer actually changes, not on every scroll frame.
  const lastChars = useRef(chars);
  const lastConf = useRef(conf);

  const typing = useTransform(scrollYProgress, [0.05, 0.42], [0, 1]);
  useMotionValueEvent(typing, "change", (v) => {
    const next = Math.round(Math.max(0, Math.min(1, v)) * SENTENCE.length);
    if (next !== lastChars.current) {
      lastChars.current = next;
      setChars(next);
    }
  });
  const confProg = useTransform(scrollYProgress, [0.5, 0.85], [0, 1]);
  useMotionValueEvent(confProg, "change", (v) => {
    const next = Math.round(Math.max(0, Math.min(1, v)) * FINAL_CONFIDENCE);
    if (next !== lastConf.current) {
      lastConf.current = next;
      setConf(next);
    }
  });

  // "Develops sharp" via an opacity crossfade between a statically-blurred ghost and
  // the sharp poster — never animates `filter`, so it stays GPU-composited and smooth.
  const ghostOpacity = useTransform(scrollYProgress, [0.45, 0.82], [1, 0]);
  const sharpOpacity = useTransform(scrollYProgress, [0.45, 0.82], [0, 1]);
  const cardOpacity = useTransform(scrollYProgress, [0.38, 0.52], [0, 1]);
  const cardY = useTransform(scrollYProgress, [0.38, 0.55], [48, 0]);

  return (
    <div ref={ref} className={reduce ? "" : "relative h-[260vh]"}>
      <div
        className={`flex flex-col items-center justify-center gap-8 px-6 ${
          reduce ? "min-h-[70vh] py-20" : "sticky top-0 h-screen"
        }`}
      >
        <div className="glass-strong w-full max-w-[640px] rounded-2xl p-5">
          <p className="mb-2 text-[0.78rem] font-semibold uppercase tracking-[0.14em] text-faint">
            You type what you remember
          </p>
          <p className="min-h-[3.2rem] text-[1.25rem] leading-relaxed text-ink" aria-label={SENTENCE}>
            {SENTENCE.slice(0, chars)}
            {!reduce && chars < SENTENCE.length && (
              <span className="ml-0.5 inline-block h-[1.2em] w-[2px] translate-y-[3px] animate-pulse bg-violet-soft" />
            )}
          </p>
        </div>

        <m.div
          className="glass-strong flex w-full max-w-[640px] items-center gap-5 rounded-3xl p-5
            ring-1 ring-violet/40 shadow-glow"
          style={reduce ? undefined : { opacity: cardOpacity, y: cardY }}
        >
          <div aria-hidden="true" className="relative h-40 w-28 shrink-0">
            {!reduce && (
              <m.div
                className="absolute inset-0 flex items-center justify-center rounded-xl
                  bg-[linear-gradient(160deg,#2a2350,#151129_60%,#3d2e12)] text-[2.6rem]
                  blur-[14px] grayscale [will-change:opacity]"
                style={{ opacity: ghostOpacity }}
              >
                ⚖️
              </m.div>
            )}
            <m.div
              className="absolute inset-0 flex items-center justify-center rounded-xl
                bg-[linear-gradient(160deg,#2a2350,#151129_60%,#3d2e12)] text-[2.6rem]
                [will-change:opacity]"
              style={reduce ? undefined : { opacity: sharpOpacity }}
            >
              ⚖️
            </m.div>
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-[0.78rem] font-semibold uppercase tracking-[0.14em] text-faint">
              …and it finds the real thing
            </p>
            <h2 className="mt-1 font-display text-[1.7rem] font-bold tracking-[-0.02em]">
              12 Angry Men
            </h2>
            <p className="mt-1 text-[0.92rem] text-muted">
              A jury of twelve locked in one sweltering room, one holdout voting not guilty.
            </p>
          </div>
          <div className="shrink-0 text-center">
            <span
              className="font-mono text-[1.7rem] font-bold"
              style={{ color: conf >= 75 ? "var(--color-amber)" : "var(--color-violet-soft)" }}
            >
              {conf}%
            </span>
            <p className="text-[0.66rem] tracking-[0.04em] text-faint">
              {conf >= 75 ? "in focus" : "focusing…"}
            </p>
          </div>
        </m.div>
      </div>
    </div>
  );
}

/** Scene 3 — the six category chips orbit in from around the lens. */
function CategoriesScene() {
  const { data } = useQuery({ queryKey: ["categories"], queryFn: api.categories });
  const categories = data?.length ? data : FALLBACK_CATEGORIES;

  return (
    <section className="mx-auto max-w-[760px] px-6 py-28 text-center">
      <h2 className="font-display text-[clamp(1.8rem,4.5vw,2.6rem)] font-bold tracking-[-0.03em]">
        Six shelves of half-memories.
      </h2>
      <p className="mx-auto mt-3 max-w-[480px] text-[1.05rem] text-muted">
        Real catalogs — no invented answers. Pick a shelf and describe the fragment.
      </p>
      <div className="mt-10 flex flex-wrap justify-center gap-3.5">
        {categories.map((c, i) => {
          const angle = (i / categories.length) * Math.PI * 2;
          return (
            <m.div
              key={c.key}
              initial={{
                opacity: 0,
                x: Math.cos(angle) * 180,
                y: Math.sin(angle) * 120,
                rotate: Math.cos(angle) * 20,
              }}
              whileInView={{ opacity: 1, x: 0, y: 0, rotate: 0 }}
              viewport={{ once: true, amount: 0.4 }}
              transition={{ duration: 0.7, delay: i * 0.07, ease: [0.2, 0.7, 0.2, 1] }}
            >
              <Link
                to="/register"
                className="glass flex items-center gap-2.5 rounded-full px-5 py-3 text-[1rem]
                  font-semibold transition-colors hover:border-violet/60 hover:shadow-glow"
              >
                <span aria-hidden="true" className="text-[1.25rem]">{c.icon}</span>
                {c.display_name}
              </Link>
            </m.div>
          );
        })}
      </div>
    </section>
  );
}

/** Scene 4 — the call to action. */
function CtaScene() {
  return (
    <section className="px-6 pb-32 pt-10 text-center">
      <m.div
        initial={{ opacity: 0, y: 32, scale: 0.97 }}
        whileInView={{ opacity: 1, y: 0, scale: 1 }}
        viewport={{ once: true, amount: 0.5 }}
        transition={{ duration: 0.6, ease: [0.2, 0.7, 0.2, 1] }}
        className="glass-strong mx-auto max-w-[640px] rounded-3xl p-10 ring-1 ring-violet/30 shadow-glow"
      >
        <h2 className="font-display text-[clamp(1.9rem,5vw,2.8rem)] font-bold tracking-[-0.03em]">
          That thing on the tip of your tongue?
        </h2>
        <p className="mx-auto mt-3 max-w-[440px] text-[1.05rem] text-muted">
          Create an account to keep every find — history, collections, your memory
          constellation, and a daily guessing challenge.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link
            to="/register"
            className="rounded-full bg-violet px-7 py-3.5 text-[1.02rem] font-semibold text-white
              shadow-glow transition-transform hover:scale-[1.03]"
          >
            Create account
          </Link>
          <Link
            to="/login"
            className="glass rounded-full px-7 py-3.5 text-[1.02rem] font-semibold
              transition-colors hover:border-violet/60"
          >
            Sign in ↗
          </Link>
        </div>
      </m.div>
    </section>
  );
}

export default function Landing() {
  const reduce = useReducedMotion() ?? false;
  // Touch devices stutter on per-frame SVG re-rasterization — lighten those scenes.
  const coarse = useMediaQuery("(hover: none), (pointer: coarse)");
  return (
    // Full-bleed breakout from the layout's 920px column — scenes own the viewport.
    <div className="relative left-1/2 w-screen -translate-x-1/2 -my-12">
      <ApertureScene reduce={reduce} coarse={coarse} />
      <RecallScene reduce={reduce} />
      <CategoriesScene />
      <CtaScene />
    </div>
  );
}
