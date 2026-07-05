import { m } from "framer-motion";
import type { ReactNode } from "react";
import { developIn, fadeUp } from "./variants";

interface Props {
  children: ReactNode;
  /** "develop" blurs in (default); "fade" is a lighter rise. */
  variant?: "develop" | "fade";
  className?: string;
  delay?: number;
}

/** Reveals its child on mount. Reduced-motion is handled globally by
 *  MotionConfig reducedMotion="user", so no branching needed here. */
export default function Reveal({ children, variant = "develop", className, delay = 0 }: Props) {
  const variants = variant === "develop" ? developIn : fadeUp;
  return (
    <m.div
      className={className}
      variants={variants}
      initial="hidden"
      animate="show"
      transition={{ delay }}
    >
      {children}
    </m.div>
  );
}
