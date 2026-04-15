"use client";

import { useState } from "react";
import { GlassCard } from "@/components/ui/glass-card";
import { PageTransition } from "@/components/ui/page-transition";

export default function SettingsPage() {
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [weeklyDigest, setWeeklyDigest] = useState(true);
  const [profileVisibility, setProfileVisibility] = useState("Recruiters");

  return (
    <PageTransition>
      <section className="space-y-4">
        <h1 className="text-3xl font-semibold text-slate-100">Settings</h1>
        <GlassCard>
          <div className="space-y-5">
            <div>
              <h2 className="text-lg font-semibold text-slate-100">Notification Preferences</h2>
              <p className="text-sm text-slate-400">Control how Align notifies you about new opportunities.</p>
            </div>

            <label className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-900/70 px-4 py-3">
              <span className="text-sm text-slate-200">Email alerts for matching jobs</span>
              <input
                type="checkbox"
                checked={emailAlerts}
                onChange={(event) => setEmailAlerts(event.target.checked)}
                className="h-4 w-4 accent-cyan-400"
              />
            </label>

            <label className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-900/70 px-4 py-3">
              <span className="text-sm text-slate-200">Weekly summary digest</span>
              <input
                type="checkbox"
                checked={weeklyDigest}
                onChange={(event) => setWeeklyDigest(event.target.checked)}
                className="h-4 w-4 accent-cyan-400"
              />
            </label>

            <label className="block space-y-2 text-sm text-slate-300">
              Profile Visibility
              <select
                value={profileVisibility}
                onChange={(event) => setProfileVisibility(event.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100"
              >
                <option>Recruiters</option>
                <option>Only me</option>
                <option>Public</option>
              </select>
            </label>

            <button
              type="button"
              className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-cyan-400"
            >
              Save Preferences
            </button>
          </div>
        </GlassCard>
      </section>
    </PageTransition>
  );
}
