"use client";

import { PageTransition } from "@/components/ui/page-transition";
import { useAppState } from "@/components/providers/app-state-provider";

function Section({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="border-t border-slate-700/70 pt-4">
      <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-300">{title}</h2>
      <ul className="mt-2 space-y-1 text-sm text-slate-200">
        {items.map((item) => (
          <li key={item}>• {item}</li>
        ))}
      </ul>
    </section>
  );
}

export default function ResumePage() {
  const { profile } = useAppState();

  return (
    <PageTransition>
      <section className="space-y-5">
        <div>
          <h1 className="text-3xl font-semibold text-slate-100">Resume Builder</h1>
          <p className="mt-1 text-slate-400">ATS-friendly single-column resume generated from your profile data.</p>
        </div>

        <article className="mx-auto w-full max-w-3xl rounded-2xl border border-slate-700/70 bg-slate-950/80 p-6 shadow-[0_20px_70px_rgba(2,6,23,0.6)]">
          <header className="pb-4">
            <h2 className="text-2xl font-semibold text-slate-100">{profile.fullName}</h2>
            <p className="mt-1 text-sm text-slate-300">{profile.email} | {profile.phone}</p>
            <p className="mt-1 text-xs text-cyan-300">{profile.social.linkedIn} | {profile.social.github} | {profile.social.portfolio}</p>
          </header>

          <Section title="Education" items={profile.education} />
          <Section title="Technical Skills" items={profile.skills} />
          <Section title="Projects" items={profile.projects} />
          <Section title="Positions of Responsibility" items={profile.positionsOfResponsibility} />
          <Section title="Achievements & Certificates" items={[...profile.achievements, ...profile.certificates]} />
        </article>
      </section>
    </PageTransition>
  );
}
