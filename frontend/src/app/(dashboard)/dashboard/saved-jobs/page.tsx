"use client";

import { JobCard } from "@/components/dashboard/job-card";
import { PageTransition } from "@/components/ui/page-transition";
import { useAppState } from "@/components/providers/app-state-provider";

export default function SavedJobsPage() {
  const { savedJobIds, getJobById } = useAppState();
  const jobs = savedJobIds.map((id) => getJobById(id)).filter(Boolean);

  return (
    <PageTransition>
      <section>
        <h1 className="text-3xl font-semibold text-slate-100">Saved Jobs</h1>
        <p className="mt-1 text-slate-400">Quick access to opportunities you bookmarked.</p>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {jobs.length ? jobs.map((job) => <JobCard key={job!.id} job={job!} />) : <p className="text-slate-400">No saved jobs yet.</p>}
        </div>
      </section>
    </PageTransition>
  );
}
