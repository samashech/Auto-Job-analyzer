"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  BriefcaseBusiness,
  ClipboardCheck,
  House,
  LayoutDashboard,
  LogOut,
  Settings,
  Star,
  User,
  UserRoundSearch,
  FileText,
} from "lucide-react";
import { dashboardLinks } from "@/lib/constants";
import { cn } from "@/lib/utils";
import { BrandLogo } from "@/components/brand-logo";
import { useAppState } from "@/components/providers/app-state-provider";

const iconMap = {
  Home: House,
  Dashboard: LayoutDashboard,
  Profile: User,
  "My Jobs": UserRoundSearch,
  "Saved Jobs": Star,
  "Applied Jobs": ClipboardCheck,
  Resume: FileText,
  Settings,
} as const;

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { currentUser, logoutUser } = useAppState();

  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-72 border-r border-cyan-500/20 bg-slate-950/90 p-6 backdrop-blur-xl lg:flex lg:flex-col">
      <div className="mb-8">
        <BrandLogo />
      </div>

      <nav className="space-y-2">
        {dashboardLinks.map((item) => {
          const Icon = iconMap[item.label as keyof typeof iconMap] ?? BriefcaseBusiness;
          const active = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-300 transition",
                "hover:bg-cyan-400/10 hover:text-cyan-200",
                active && "bg-cyan-400/15 text-cyan-200 shadow-[inset_0_0_0_1px_rgba(34,211,238,0.3)]",
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto rounded-2xl border border-cyan-400/20 bg-slate-900/80 p-4">
        <div className="mb-3 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-full bg-cyan-500/20 text-cyan-300">
            <User className="h-5 w-5" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-100">{currentUser?.fullName ?? "Guest User"}</p>
            <p className="text-xs text-slate-400">{currentUser?.email ?? "guest@align.dev"}</p>
          </div>
        </div>

        <button
          type="button"
          onClick={() => {
            logoutUser();
            router.push("/login");
          }}
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-cyan-400/30 bg-cyan-500/10 px-3 py-2 text-sm font-medium text-cyan-200 transition hover:bg-cyan-500/20"
        >
          <LogOut className="h-4 w-4" />
          Logout
        </button>
      </div>
    </aside>
  );
}
