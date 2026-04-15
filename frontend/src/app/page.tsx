"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ShieldCheck, Sparkles, Workflow } from "lucide-react";
import { BrandLogo } from "@/components/brand-logo";

const navItems = [
  { href: "#about", label: "About" },
  { href: "#how", label: "How It Works" },
  { href: "#features", label: "Features" },
  { href: "#security", label: "Security" },
  { href: "#faq", label: "FAQs" },
];

const faqs = [
  {
    q: "How does Align personalize job results?",
    a: "Align scores jobs against your top five skills, location preferences, and selected job types.",
  },
  {
    q: "Is the platform secure for profile data?",
    a: "All input fields are client-side validated with strict rules before any action is accepted.",
  },
  {
    q: "Can I track saved and applied jobs?",
    a: "Yes. Saved and Applied lists are separated and visible across dedicated dashboard sections.",
  },
];

export default function Home() {
  return (
    <div className="text-slate-100">
      <header className="sticky top-0 z-40 border-b border-cyan-400/10 bg-slate-950/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <BrandLogo />
          <nav className="hidden items-center gap-6 md:flex">
            {navItems.map((item) => (
              <a key={item.href} href={item.href} className="text-sm text-slate-300 transition hover:text-cyan-300">
                {item.label}
              </a>
            ))}
          </nav>
          <div className="flex items-center gap-3">
            <Link href="/login" className="rounded-lg border border-cyan-300/30 px-4 py-2 text-sm text-cyan-200 hover:bg-cyan-400/10">
              Log In
            </Link>
            <Link href="/signup" className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-cyan-400">
              Sign Up
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-20 px-6 py-14">
        <section className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
          <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
            <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Professional Job Discovery Platform</p>
            <h1 className="mt-4 text-4xl font-semibold leading-tight md:text-6xl">
              Align your skillset with the right opportunities, faster.
            </h1>
            <p className="mt-5 max-w-xl text-slate-300">
              Align is a sleek job scraping and tracking workspace designed for focused developers and professionals.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/signup" className="rounded-lg bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-900 hover:bg-cyan-400">
                Launch Dashboard
              </Link>
              <a href="#how" className="rounded-lg border border-slate-700 px-5 py-3 text-sm text-slate-200 hover:border-cyan-300/40">
                See Workflow
              </a>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="rounded-2xl border border-cyan-400/20 bg-slate-900/60 p-6 shadow-[0_20px_80px_rgba(2,6,23,0.7)] backdrop-blur-xl"
          >
            <div className="grid gap-4 sm:grid-cols-2">
              {[
                ["Active Listings", "2,340+"],
                ["Match Accuracy", "92%"],
                ["Applications Sent", "18,900+"],
                ["Average Response", "2.1 days"],
              ].map(([label, value]) => (
                <div key={label} className="rounded-xl border border-slate-700/70 bg-slate-950/60 p-4">
                  <p className="text-xs text-slate-400">{label}</p>
                  <p className="mt-1 text-2xl font-semibold text-cyan-300">{value}</p>
                </div>
              ))}
            </div>
          </motion.div>
        </section>

        <section id="about" className="rounded-2xl border border-cyan-400/20 bg-slate-900/40 p-8">
          <h2 className="text-2xl font-semibold">About Align</h2>
          <p className="mt-3 max-w-3xl text-slate-300">
            Align centralizes opportunity discovery, sorting, and action into one performance-focused interface for modern candidates.
          </p>
        </section>

        <section id="how" className="grid gap-4 md:grid-cols-3">
          {[
            { icon: Workflow, title: "Configure", copy: "Set location, job type, and your top five technical skills." },
            { icon: Sparkles, title: "Rank", copy: "Align ranks incoming jobs based on match relevance and preference settings." },
            { icon: ShieldCheck, title: "Track", copy: "Save, apply, and monitor progress with secure profile-driven workflows." },
          ].map((item) => (
            <div key={item.title} className="rounded-2xl border border-cyan-400/20 bg-slate-900/55 p-5">
              <item.icon className="h-6 w-6 text-cyan-300" />
              <h3 className="mt-3 text-lg font-semibold">{item.title}</h3>
              <p className="mt-2 text-sm text-slate-300">{item.copy}</p>
            </div>
          ))}
        </section>

        <section id="features" className="space-y-4">
          <h2 className="text-2xl font-semibold">Features</h2>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {[
              "Role-based dashboard with persistent navigation",
              "Advanced location and job type filtering",
              "Skill-prioritized job feed",
              "Saved and applied pipelines",
              "Profile view/edit modes with strict validation",
              "ATS-friendly resume generation from profile data",
            ].map((feature) => (
              <div key={feature} className="rounded-xl border border-slate-700/60 bg-slate-950/60 p-4 text-sm text-slate-200">
                {feature}
              </div>
            ))}
          </div>
        </section>

        <section id="security" className="rounded-2xl border border-cyan-400/20 bg-slate-900/45 p-8">
          <h2 className="text-2xl font-semibold">Security Protocols</h2>
          <ul className="mt-3 space-y-2 text-sm text-slate-300">
            <li>Strict regex-based input validation for names, phone, email, and URLs.</li>
            <li>Authentication mock flow with unique email constraints and lock-triggered forgot password state.</li>
            <li>Strong client-side guardrails using React Hook Form and Zod schema enforcement.</li>
          </ul>
        </section>

        <section id="faq" className="space-y-3 pb-10">
          <h2 className="text-2xl font-semibold">FAQs</h2>
          {faqs.map((item) => (
            <details key={item.q} className="rounded-xl border border-slate-700/60 bg-slate-950/60 p-4">
              <summary className="cursor-pointer font-medium text-slate-100">{item.q}</summary>
              <p className="mt-2 text-sm text-slate-300">{item.a}</p>
            </details>
          ))}
        </section>
      </main>
    </div>
  );
}
