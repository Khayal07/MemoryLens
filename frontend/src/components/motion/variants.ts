import type { Variants, Transition } from "framer-motion";

/** Shared spring — the "develop into focus" feel: quick, lightly damped. */
export const spring: Transition = { type: "spring", stiffness: 320, damping: 30 };
export const softSpring: Transition = { type: "spring", stiffness: 180, damping: 26 };

/** A fragment blurs in from below, as if a memory coming into focus. */
export const developIn: Variants = {
  hidden: { opacity: 0, y: 12, filter: "blur(10px)" },
  show: {
    opacity: 1,
    y: 0,
    filter: "blur(0px)",
    transition: { duration: 0.5, ease: [0.2, 0.7, 0.2, 1] },
  },
};

/** Simpler fade+rise for elements where blur is too heavy. */
export const fadeUp: Variants = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.2, 0.7, 0.2, 1] } },
};

/** Parent container that reveals children one after another. */
export const stagger = (gap = 0.07, delay = 0): Variants => ({
  hidden: {},
  show: { transition: { staggerChildren: gap, delayChildren: delay } },
});

/** Page-transition variants for route changes. */
export const pageTransition: Variants = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0, transition: { duration: 0.32, ease: [0.2, 0.7, 0.2, 1] } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.2, ease: "easeIn" } },
};
