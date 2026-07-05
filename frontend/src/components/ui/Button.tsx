import { m, type HTMLMotionProps } from "framer-motion";
import { cn } from "../../lib/cn";
import { spring } from "../motion/variants";

type Variant = "primary" | "ghost";

interface Props extends HTMLMotionProps<"button"> {
  variant?: Variant;
  block?: boolean;
}

const base =
  "inline-flex items-center justify-center gap-2 rounded-xl font-semibold text-[0.95rem] " +
  "px-[18px] py-3 transition-[opacity] disabled:opacity-50 disabled:cursor-not-allowed " +
  "focus-visible:outline-2 focus-visible:outline-violet-soft focus-visible:outline-offset-2";

const variants: Record<Variant, string> = {
  primary: "text-[#14122b] bg-gradient-to-r from-violet-soft to-amber shadow-glow",
  ghost: "bg-raised text-ink border border-line-strong hover:border-violet",
};

/** The one button in the app. Tactile press via spring scale; reduced-motion
 *  users get no scale (handled globally by MotionConfig). */
export default function Button({
  variant = "primary",
  block,
  className,
  children,
  ...props
}: Props) {
  return (
    <m.button
      whileTap={{ scale: 0.97 }}
      transition={spring}
      className={cn(base, variants[variant], block && "w-full", className)}
      {...props}
    >
      {children}
    </m.button>
  );
}
