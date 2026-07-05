import { m } from "framer-motion";
import type { ReactNode } from "react";
import { pageTransition } from "./variants";

/** Wraps a route's content so it fades/slides in on navigation. Pair with an
 *  <AnimatePresence> keyed on the pathname in the layout. */
export default function PageTransition({ children }: { children: ReactNode }) {
  return (
    <m.div variants={pageTransition} initial="hidden" animate="show" exit="exit">
      {children}
    </m.div>
  );
}
