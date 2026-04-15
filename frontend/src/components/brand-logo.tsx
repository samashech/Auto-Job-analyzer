export function BrandLogo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="inline-flex items-center gap-3">
      <div className="relative h-9 w-9">
        <div className="absolute left-1.5 top-1 h-7 w-[3px] -skew-x-[28deg] rounded-full bg-cyan-400 shadow-[0_0_14px_rgba(34,211,238,0.8)]" />
        <div className="absolute left-4 top-1 h-7 w-[3px] -skew-x-[28deg] rounded-full bg-cyan-300 shadow-[0_0_14px_rgba(103,232,249,0.9)]" />
        <div className="absolute left-6.5 top-1 h-7 w-[3px] -skew-x-[28deg] rounded-full bg-cyan-500 shadow-[0_0_16px_rgba(6,182,212,0.9)]" />
      </div>
      {!compact ? <span className="text-xl font-semibold tracking-tight text-slate-100">Align</span> : null}
    </div>
  );
}
