"use client";

import Link from "next/link";
import { BrandLogo } from "@/components/brand-logo";

export function AuthCard({
  title,
  subtitle,
  children,
  footerLabel,
  footerHref,
  footerAction,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  footerLabel: string;
  footerHref: string;
  footerAction: string;
}) {
  return (
    <div className="w-full max-w-md rounded-2xl border border-cyan-400/20 bg-slate-950/80 p-6 shadow-[0_20px_80px_rgba(2,6,23,0.7)] backdrop-blur-xl">
      <BrandLogo />
      <h1 className="mt-6 text-2xl font-semibold text-slate-100">{title}</h1>
      <p className="mt-1 text-sm text-slate-400">{subtitle}</p>
      <div className="mt-6">{children}</div>
      <p className="mt-6 text-sm text-slate-400">
        {footerLabel}{" "}
        <Link href={footerHref} className="font-medium text-cyan-300 hover:text-cyan-200">
          {footerAction}
        </Link>
      </p>
    </div>
  );
}
