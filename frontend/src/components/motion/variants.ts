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

/** A poster "develops" like a darkroom print: heavy blur + monochrome resolving into
 *  full colour while it settles from a slight zoom. Runs once the image has loaded. */
export const photoDevelop: Variants = {
  hidden: { opacity: 0, scale: 1.06, filter: "blur(24px) grayscale(1) brightness(0.6)" },
  show: {
    opacity: 1,
    scale: 1,
    filter: "blur(0px) grayscale(0) brightness(1)",
    transition: { duration: 1.2, ease: [0.25, 0.6, 0.2, 1] },
  },
};

/** Quicker, subtler develop for the compact alternative cards. */
export const photoDevelopSoft: Variants = {
  hidden: { opacity: 0, filter: "blur(10px) grayscale(1) brightness(0.75)" },
  show: {
    opacity: 1,
    filter: "blur(0px) grayscale(0) brightness(1)",
    transition: { duration: 0.6, ease: [0.2, 0.7, 0.2, 1] },
  },
};

/** For posterless heroes: the aurora aperture blooms in instead of a photo developing. */
export const apertureBloom: Variants = {
  hidden: { opacity: 0, scale: 0.85 },
  show: { opacity: 1, scale: 1, transition: { duration: 0.9, ease: [0.2, 0.7, 0.2, 1] } },
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

/** Page-transition variants for route changes — a spatial fade with depth. */
export const pageTransition: Variants = {
  hidden: { opacity: 0, y: 12, scale: 0.98, filter: "blur(6px)" },
  show: {
    opacity: 1,
    y: 0,
    scale: 1,
    filter: "blur(0px)",
    transition: { duration: 0.36, ease: [0.2, 0.7, 0.2, 1] },
  },
  exit: { opacity: 0, y: -8, scale: 0.99, filter: "blur(4px)", transition: { duration: 0.2, ease: "easeIn" } },
};
