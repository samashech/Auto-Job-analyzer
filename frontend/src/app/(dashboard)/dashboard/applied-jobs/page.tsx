"use client";

import { JobCard } from "@/components/dashboard/job-card";
import { PageTransition } from "@/components/ui/page-transition";
import { useAppState } from "@/components/providers/app-state-provider";

export default function AppliedJobsPage() {
  const { appliedJobIds, getJobById } = useAppState();
  const jobs = appliedJobIds.map((id) => getJobById(id)).filter(Boolean);

  return (
    <PageTransition>
      <section>
        <h1 className="text-3xl font-semibold text-slate-100">Applied Jobs</h1>
        <p className="mt-1 text-slate-400">Track every application sent from your Align workflow.</p>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {jobs.length ? jobs.map((job) => <JobCard key={job!.id} job={job!} />) : <p className="text-slate-400">No applied jobs yet.</p>}
        </div>
      </section>
    </PageTransition>
  );
}
