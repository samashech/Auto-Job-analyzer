"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { dashboardLinks } from "@/lib/constants";
import { BrandLogo } from "@/components/brand-logo";
import { cn } from "@/lib/utils";

export function MobileNav() {
  const pathname = usePathname();

  return (
    <div className="sticky top-0 z-30 border-b border-cyan-500/20 bg-slate-950/90 px-4 py-3 backdrop-blur-xl lg:hidden">
      <div className="mb-3 flex items-center justify-between">
        <BrandLogo compact />
      </div>
      <div className="flex gap-2 overflow-x-auto pb-1">
        {dashboardLinks.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "whitespace-nowrap rounded-lg border px-3 py-1.5 text-xs",
              pathname === item.href
                ? "border-cyan-300/50 bg-cyan-400/20 text-cyan-200"
                : "border-slate-700 bg-slate-900/70 text-slate-300",
            )}
          >
            {item.label}
          </Link>
        ))}
      </div>
    </div>
  );
}
