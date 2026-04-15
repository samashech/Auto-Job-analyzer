import { cn } from "@/lib/utils";

export function GlassCard({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-cyan-400/20 bg-slate-900/60 p-5 shadow-[0_0_0_1px_rgba(6,182,212,0.1),0_20px_60px_rgba(2,6,23,0.7)] backdrop-blur-xl",
        className,
      )}
    >
      {children}
    </div>
  );
}
