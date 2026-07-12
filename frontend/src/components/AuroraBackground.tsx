import { m, useReducedMotion } from "framer-motion";
import useMediaQuery from "../lib/useMediaQuery";

/** A living aurora behind the whole app: large blurred colour orbs that drift
 *  and breathe. Purely decorative, fixed and non-interactive. Reduced-motion
 *  users and small screens get the same orbs, just still — animating vw-sized
 *  blurs every frame is what makes phones stutter. */
export default function AuroraBackground() {
  const reduce = useReducedMotion();
  const small = useMediaQuery("(max-width: 767px)");
  const still = reduce || small;

  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden" aria-hidden="true">
      {/* violet — top left */}
      <m.div
        className="absolute -left-[10%] -top-[15%] size-[46vw] rounded-full opacity-70 blur-[48px] md:blur-[90px]"
        style={{ background: "radial-gradient(circle, var(--color-aurora-1), transparent 60%)" }}
        {...(still
          ? {}
          : {
              animate: { x: [0, 80, -20, 0], y: [0, 40, 90, 0], scale: [1, 1.15, 0.95, 1] },
              transition: { duration: 18, repeat: Infinity, ease: "easeInOut" },
            })}
      />
      {/* amber — right */}
      <m.div
        className="absolute right-[-8%] top-[8%] size-[38vw] rounded-full opacity-50 blur-[52px] md:blur-[100px]"
        style={{ background: "radial-gradient(circle, var(--color-aurora-2), transparent 62%)" }}
        {...(still
          ? {}
          : {
              animate: { x: [0, -60, 30, 0], y: [0, 70, 20, 0], scale: [1, 0.9, 1.1, 1] },
              transition: { duration: 22, repeat: Infinity, ease: "easeInOut" },
            })}
      />
      {/* indigo — bottom center */}
      <m.div
        className="absolute bottom-[-20%] left-[30%] size-[50vw] rounded-full opacity-60 blur-[56px] md:blur-[110px]"
        style={{ background: "radial-gradient(circle, var(--color-aurora-3), transparent 60%)" }}
        {...(still
          ? {}
          : {
              animate: { x: [0, 50, -40, 0], y: [0, -30, 30, 0], scale: [1, 1.2, 1, 1] },
              transition: { duration: 26, repeat: Infinity, ease: "easeInOut" },
            })}
      />
      {/* a faint grain/vignette to keep it premium, not garish */}
      <div className="absolute inset-0 bg-[radial-gradient(120%_100%_at_50%_0%,transparent_40%,rgba(14,16,32,0.55))]" />
    </div>
  );
}
