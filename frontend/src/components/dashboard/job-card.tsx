"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, ExternalLink, MapPin, Star } from "lucide-react";
import { Job } from "@/lib/types";
import { cn } from "@/lib/utils";
import { useAppState } from "@/components/providers/app-state-provider";

export function JobCard({ job }: { job: Job }) {
  const { savedJobIds, toggleSaveJob, applyJob } = useAppState();
  const [isExpanded, setIsExpanded] = useState(false);
  const saved = savedJobIds.includes(job.id);

  return (
    <article className="flex h-full flex-col rounded-2xl border border-cyan-400/20 bg-slate-900/70 p-5 shadow-[0_10px_40px_rgba(2,6,23,0.55)] backdrop-blur-xl transition-all hover:border-cyan-400/40">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-100">{job.title}</h3>
          <p className="mt-1 text-sm text-slate-400">{job.company}</p>
        </div>
        <button
          type="button"
          onClick={() => toggleSaveJob(job.id)}
          className={cn(
            "rounded-full border p-2 transition",
            saved
              ? "border-cyan-300 bg-cyan-400/20 text-cyan-300"
              : "border-slate-700 bg-slate-800/70 text-slate-400 hover:border-cyan-400/40 hover:text-cyan-300",
          )}
          aria-label="Save job"
        >
          <Star className={cn("h-4 w-4", saved && "fill-current")} />
        </button>
      </div>

      <div className="mt-4 flex-grow space-y-2 text-sm text-slate-300">
        <div className="flex items-center justify-between min-h-[1.5rem]">
          <p className={cn("font-medium", (!job.salary || job.salary === "Not specified") ? "text-slate-500 italic" : "text-cyan-300")}>
            {(!job.salary || job.salary === "Not specified") ? "Salary: Apply to confirm" : job.salary}
          </p>
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">{job.source}</p>
        </div>
        <p className="inline-flex items-center gap-1.5 text-slate-400">
          <MapPin className="h-4 w-4" />
          {job.location}
        </p>
        {job.job_function && job.job_function !== "Not specified" && (
          <p className="text-xs text-slate-400">
            <span className="font-semibold text-slate-500">Function:</span> {job.job_function}
          </p>
        )}
        <p className={cn("text-xs", (!job.expiry_date || job.expiry_date === "No deadline specified") ? "text-slate-500 italic" : "text-rose-400/80")}>
          <span className="font-semibold text-slate-500">Apply by:</span> {(!job.expiry_date || job.expiry_date === "No deadline specified") ? "Apply to confirm" : job.expiry_date}
        </p>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {job.skills.slice(0, 5).map((skill) => (
          <span key={skill} className="rounded-full border border-cyan-300/20 bg-cyan-500/10 px-2.5 py-1 text-xs text-cyan-200">
            {skill}
          </span>
        ))}
      </div>

      {job.description && (
        <div className="mt-4">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-1 text-xs font-medium text-slate-400 transition hover:text-cyan-300"
          >
            {isExpanded ? (
              <>
                <ChevronUp className="h-3 w-3" />
                Hide Details
              </>
            ) : (
              <>
                <ChevronDown className="h-3 w-3" />
                Show Details
              </>
            )}
          </button>

          {isExpanded && (
            <div className="mt-3 animate-in fade-in slide-in-from-top-2 duration-300">
              <div className="rounded-lg bg-slate-800/50 p-3 text-sm text-slate-300 leading-relaxed whitespace-pre-wrap border border-slate-700/50">
                {job.description}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="mt-5">
        <a
          href={job.sourceUrl}
          target="_blank"
          rel="noreferrer"
          onClick={() => applyJob(job.id)}
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-cyan-500 px-3.5 py-2 text-sm font-semibold text-slate-900 transition hover:bg-cyan-400 shadow-lg shadow-cyan-500/20"
        >
          Apply Now
          <ExternalLink className="h-4 w-4" />
        </a>
      </div>
    </article>
  );
}
