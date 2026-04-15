"use client";

import { motion } from "framer-motion";
import { Eye, Send, Star } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { PageTransition } from "@/components/ui/page-transition";
import { useAppState } from "@/components/providers/app-state-provider";

function ProgressRing({ value }: { value: number }) {
  const radius = 52;
  const stroke = 9;
  const normalized = 2 * Math.PI * radius;
  const offset = normalized - (value / 100) * normalized;

  return (
    <div className="relative h-36 w-36">
      <svg viewBox="0 0 128 128" className="h-full w-full -rotate-90">
        <circle cx="64" cy="64" r={radius} strokeWidth={stroke} className="fill-none stroke-slate-700/70" />
        <circle
          cx="64"
          cy="64"
          r={radius}
          strokeWidth={stroke}
          strokeDasharray={normalized}
          strokeDashoffset={offset}
          className="fill-none stroke-cyan-400 drop-shadow-[0_0_10px_rgba(34,211,238,0.6)] transition-all duration-700"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <p className="text-3xl font-semibold text-cyan-300">{value}%</p>
        <p className="text-xs text-slate-400">Profile Strength</p>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { savedJobIds, appliedJobIds, activities } = useAppState();

  const stats = [
    {
      label: "Jobs Applied",
      value: appliedJobIds.length,
      icon: Send,
    },
    {
      label: "Saved Jobs",
      value: savedJobIds.length,
      icon: Star,
    },
    {
      label: "Profile Views",
      value: 124,
      icon: Eye,
    },
  ];

  const profileScore = Math.min(100, 55 + savedJobIds.length * 3 + appliedJobIds.length * 5);

  return (
    <PageTransition>
      <section className="space-y-6">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-100">Welcome back</h1>
          <p className="mt-1 text-slate-400">Track performance, manage jobs, and keep your profile recruiter-ready.</p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {stats.map((stat, idx) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.08 }}
            >
              <GlassCard>
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{stat.label}</p>
                    <p className="mt-2 text-3xl font-semibold text-cyan-300">{stat.value}</p>
                  </div>
                  <div className="rounded-lg border border-cyan-400/30 bg-cyan-500/10 p-2 text-cyan-300">
                    <stat.icon className="h-5 w-5" />
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>

        <div className="grid gap-4 xl:grid-cols-[300px_1fr]">
          <GlassCard className="flex items-center justify-center">
            <ProgressRing value={profileScore} />
          </GlassCard>

          <GlassCard>
            <h2 className="text-lg font-semibold text-slate-100">Recent Activity</h2>
            <div className="mt-4 space-y-3">
              {(activities.length ? activities : [{ id: "seed", title: "No activity yet. Start by saving jobs.", timestamp: "Now" }]).map(
                (item) => (
                  <div key={item.id} className="rounded-xl border border-slate-700/70 bg-slate-900/70 px-4 py-3">
                    <p className="text-sm text-slate-100">{item.title}</p>
                    <p className="mt-1 text-xs text-slate-400">{item.timestamp}</p>
                  </div>
                ),
              )}
            </div>
          </GlassCard>
        </div>
      </section>
    </PageTransition>
  );
}
