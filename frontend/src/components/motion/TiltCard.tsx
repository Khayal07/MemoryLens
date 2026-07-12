import {
  m,
  useMotionTemplate,
  useMotionValue,
  useReducedMotion,
  useSpring,
  useTransform,
} from "framer-motion";
import { useRef, type PointerEvent, type ReactNode } from "react";
import { cn } from "../../lib/cn";
import useMediaQuery from "../../lib/useMediaQuery";

interface Props {
  children: ReactNode;
  /** Applied to the tilting surface — pass the card's glass/rounding here. */
  className?: string;
  /** Max tilt in degrees. */
  max?: number;
}

/** Wraps a surface so it tilts toward the cursor in 3D and a soft violet glow
 *  follows the pointer. Reduced-motion users get a plain, still surface. */
export default function TiltCard({ children, className, max = 7 }: Props) {
  const reduce = useReducedMotion();
  const coarse = useMediaQuery("(hover: none), (pointer: coarse)");
  const ref = useRef<HTMLDivElement>(null);

  const px = useMotionValue(0.5);
  const py = useMotionValue(0.5);
  const rotateX = useSpring(useTransform(py, [0, 1], [max, -max]), { stiffness: 220, damping: 20 });
  const rotateY = useSpring(useTransform(px, [0, 1], [-max, max]), { stiffness: 220, damping: 20 });
  const gx = useTransform(px, (v) => `${v * 100}%`);
  const gy = useTransform(py, (v) => `${v * 100}%`);
  const glow = useMotionTemplate`radial-gradient(280px circle at ${gx} ${gy}, rgba(154,141,255,0.22), transparent 60%)`;

  function onMove(e: PointerEvent<HTMLDivElement>) {
    const r = ref.current?.getBoundingClientRect();
    if (!r) return;
    px.set((e.clientX - r.left) / r.width);
    py.set((e.clientY - r.top) / r.height);
  }
  function onLeave() {
    px.set(0.5);
    py.set(0.5);
  }

  if (reduce || coarse) return <div className={cn("h-full", className)}>{children}</div>;

  return (
    <div ref={ref} onPointerMove={onMove} onPointerLeave={onLeave} className="h-full [perspective:1000px]">
      <m.div
        style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
        className={cn("relative h-full", className)}
      >
        {children}
        <m.div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 rounded-[inherit]"
          style={{ background: glow }}
        />
      </m.div>
    </div>
  );
}
