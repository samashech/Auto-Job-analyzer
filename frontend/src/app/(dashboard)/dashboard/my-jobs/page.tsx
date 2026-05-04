"use client";

import { useMemo, useState } from "react";
import { z } from "zod";
import { Controller, useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Filter, Upload, FileText, Loader2, CheckCircle, ArrowRight, Star } from "lucide-react";
import { countries, indianStates } from "@/lib/jobs-data";
import { JobType } from "@/lib/types";
import { JobCard } from "@/components/dashboard/job-card";
import { GlassCard } from "@/components/ui/glass-card";
import { PageTransition } from "@/components/ui/page-transition";
import { useAppState } from "@/components/providers/app-state-provider";

const types: JobType[] = ["Full Time", "Part Time", "Remote", "Internship", "Freelancing"];

const filterSchema = z.object({
  region: z.enum(["India", "International"]),
  stateOrContinent: z.string().min(1, "Please select a location."),
  selectedTypes: z.array(z.string()),
  skillsInput: z
    .string()
    .refine(
      (value) =>
        value
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean).length === 5,
      "Enter exactly top 5 skills, comma-separated.",
    ),
});

type FilterValues = {
  region: "India" | "International";
  stateOrContinent: string;
  selectedTypes: string[];
  skillsInput: string;
};

const extractRole = (title: string) => {
  return title
    .replace(/\s*-\s*Search\s+on\s+.*$/i, "")
    .replace(/\s*Jobs?\s+on\s+.*$/i, "")
    .replace(/\s*-\s*(LinkedIn|Naukri|Internshala|Glassdoor|Monster|Wellfound|Dice).*$/i, "")
    .trim();
};

export default function MyJobsPage() {
  const { jobs, fetchJobs } = useAppState();
  const [skills, setSkills] = useState<string[]>([]);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{ success: boolean; message: string; userId?: number } | null>(null);
  const [showDoneButton, setShowDoneButton] = useState(false);
  const [scrapingStarted, setScrapingStarted] = useState(false);
  const [selectedRole, setSelectedRole] = useState<string>("All");

  const uniqueRoles = useMemo(() => {
    const roleMap = new Map<string, string>();
    jobs.forEach((job) => {
      const role = extractRole(job.title);
      const lower = role.toLowerCase();
      if (!roleMap.has(lower) && lower.length > 0) {
        roleMap.set(lower, role);
      }
    });
    return Array.from(roleMap.values());
  }, [jobs]);

  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<FilterValues>({
    resolver: zodResolver(filterSchema),
    defaultValues: {
      region: "India",
      stateOrContinent: "All",
      selectedTypes: ["Full Time", "Remote"],
      skillsInput: "react, next.js, typescript, tailwind, testing",
    },
  });

  const region = useWatch({ control, name: "region" });
  const selectedTypes = useWatch({ control, name: "selectedTypes" });
  const stateOrContinent = useWatch({ control, name: "stateOrContinent" });

  const handleResumeUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.pdf') && 
        !file.name.toLowerCase().endsWith('.docx') &&
        !file.name.toLowerCase().endsWith('.doc')) {
      setUploadStatus({
        success: false,
        message: "Please upload a PDF or DOCX resume"
      });
      return;
    }

    setUploading(true);
    setUploadStatus(null);
    setResumeFile(file);

    try {
      const userId = localStorage.getItem('align_user_id');
      if (!userId) {
        setUploadStatus({
          success: false,
          message: "Please login first to upload resume"
        });
        return;
      }

      const formData = new FormData();
      formData.append('resume', file);
      formData.append('user_id', userId);
      formData.append('job_type', selectedTypes.length > 0 ? selectedTypes[0] : 'Full Time');

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        // Update user_id in case backend created new user
        if (data.user_id) {
          localStorage.setItem('align_user_id', String(data.user_id));
        }
        
        setUploadStatus({
          success: true,
          message: `✅ Resume uploaded! Found ${data.skills?.length || 0} skills`,
          userId: data.user_id
        });
        
        // Show Done button
        setShowDoneButton(true);
      } else {
        setUploadStatus({
          success: false,
          message: data.error || "Failed to upload resume"
        });
      }
    } catch {
      setUploadStatus({
        success: false,
        message: "Network error during upload"
      });
    } finally {
      setUploading(false);
    }
  };

  const handleDoneClick = async () => {
    if (!uploadStatus?.userId) {
      setUploadStatus({
        success: false,
        message: "Please upload resume first"
      });
      return;
    }

    setScrapingStarted(true);
    setUploading(true);
    
    setUploadStatus({
      success: true,
      message: "🚀 Scraping started! Finding jobs across multiple platforms..."
    });

    try {
      const startRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}/start-scraping`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_id: uploadStatus.userId, 
          job_type: selectedTypes.length > 0 ? selectedTypes[0] : 'Full Time',
          preferred_location: stateOrContinent === "All" ? region : (region === "India" ? `${stateOrContinent}, India` : stateOrContinent)
        })
      });
      
      if (!startRes.ok) {
        throw new Error('Failed to start scraping');
      }
    } catch {
      setUploading(false);
      setScrapingStarted(false);
      setUploadStatus({
        success: false,
        message: "Could not connect to the scraping server. Please try again."
      });
      return;
    }

    // Wait for scraping to complete (check every 5 seconds)
    const checkScraping = async () => {
      for (let i = 0; i < 120; i++) { // Check for up to 10 minutes
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}/debug-jobs/${uploadStatus.userId}`);
          const data = await response.json();
          
          if (data.jobs_in_db > 0) {
            // Trigger jobs reload via Context dynamically as jobs arrive
            await fetchJobs(String(uploadStatus.userId));
            setScrapingStarted(false);
            setUploading(false);
            setShowDoneButton(false);
            setUploadStatus({
              success: true,
              message: `✅ Scraping active! Found ${data.jobs_in_db} jobs so far. Scroll down to view.`
            });
            // We can break or continue polling for a bit, let's break for simplicity and assume jobs are loaded
            return;
          } else if (data.finished) {
            setUploading(false);
            setUploadStatus({
              success: true,
              message: `✅ Finished! Found ${data.jobs_in_db} jobs! Scroll down to view.`
            });
            await fetchJobs(String(uploadStatus.userId));
            setScrapingStarted(false);
            setShowDoneButton(false);
            return;
          } else {
             // Inform user that it's still working without fetching jobs yet
             const elapsedMin = Math.floor((i * 5) / 60);
             const elapsedSec = (i * 5) % 60;
             const timeStr = `${elapsedMin}:${elapsedSec.toString().padStart(2, '0')}`;
             setUploadStatus({
               success: true,
               message: `🚀 Scraping in progress (${timeStr} elapsed). This process searches 10+ job boards and can take 2-5 minutes. Please don't refresh...`
             });
          }
        } catch (error) {
          console.error('Error checking scraping status:', error);
        }
      }
      
      // Timeout
      setUploading(false);
      setUploadStatus({
        success: false,
        message: "Scraping timed out or is taking too long. Jobs will appear when ready."
      });
    };

    checkScraping();
  };

  const onSubmit = (values: FilterValues) => {
    const parsed = filterSchema.parse(values);
      setSkills(
        parsed.skillsInput
          .split(",")
          .map((s) => s.trim().toLowerCase())
          .filter(Boolean),
      );
  };

  const filteredJobs = useMemo(() => {
    const scored = jobs
      .filter((job) => {
        const byRegion = job.region === region;
        const byLocation = stateOrContinent === "All" || job.stateOrContinent === stateOrContinent;
        const byType =
          !selectedTypes.length || selectedTypes.some((selected) => 
            job.type.some(t => t.replace('-', ' ').toLowerCase() === selected.toLowerCase())
          );
        let role = extractRole(job.title);
        if (job.source && job.source.toLowerCase() === "unstop") {
          role = "Hackathons";
        }
        const byRole = selectedRole === "All" || role.toLowerCase() === selectedRole.toLowerCase();
        return byRegion && byLocation && byType && byRole;
      })
      .map((job) => {
        // Only score by skills if user has submitted the filter form
        const score = skills.length
          ? skills.reduce((acc, skill) => (job.skills.map((j) => j.toLowerCase()).includes(skill) ? acc + 1 : acc), 0)
          : job.relevance_score || 0; // Use backend relevance score if no manual filter
        return { job, score };
      })
      .sort((a, b) => b.score - a.score);

    return scored.map((item) => item.job);
  }, [region, selectedTypes, stateOrContinent, skills, jobs, selectedRole]);

  return (
    <PageTransition>
      <section className="space-y-6">
        <div>
          <h1 className="text-3xl font-semibold text-slate-100">My Jobs</h1>
          <p className="mt-1 text-slate-400">Tune filters and align every result to your top skills.</p>
        </div>

        <GlassCard>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid gap-4 lg:grid-cols-2">
              <label className="space-y-2 text-sm text-slate-300">
                Location Mode <span className="text-rose-500">*</span>
                <select {...register("region")} required className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100">
                  <option value="India">India</option>
                  <option value="International">International</option>
                </select>
              </label>

              <label className="space-y-2 text-sm text-slate-300">
                State / Country <span className="text-rose-500">*</span>
                <select
                  {...register("stateOrContinent")}
                  required
                  className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100"
                >
                  {(region === "India" ? indianStates : countries).map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div>
              <p className="mb-2 text-sm text-slate-300">Job Type</p>
              <Controller
                control={control}
                name="selectedTypes"
                render={({ field }) => (
                  <div className="flex flex-wrap gap-3">
                    {types.map((type) => {
                      const active = field.value?.includes(type);
                      return (
                        <label
                          key={type}
                          className="inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm"
                        >
                          <input
                            type="checkbox"
                            checked={active}
                            onChange={(event) => {
                              const checked = event.target.checked;
                              const next = checked
                                ? [...(field.value || []), type]
                                : (field.value || []).filter((value) => value !== type);
                              field.onChange(next);
                            }}
                            className="accent-cyan-400"
                          />
                          {type}
                        </label>
                      );
                    })}
                  </div>
                )}
              />
            </div>

            <label className="block space-y-2 text-sm text-slate-300">
              Top 5 Skills (comma-separated)
              <input
                {...register("skillsInput")}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100"
                placeholder="react, next.js, typescript, tailwind, testing"
              />
            </label>
            {errors.skillsInput ? <p className="text-sm text-rose-400">{errors.skillsInput.message as string}</p> : null}

            {/* Resume Upload Section */}
            <div className="rounded-lg border border-cyan-400/30 bg-cyan-500/5 p-4 space-y-3">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-cyan-400" />
                <p className="text-sm font-medium text-slate-100">Upload Your Resume</p>
              </div>
              <p className="text-xs text-slate-400">
                Upload your resume to automatically extract skills and find matching jobs
              </p>
              <div className="flex items-center gap-3">
                <label className="flex-1 cursor-pointer rounded-lg border-2 border-dashed border-slate-700 bg-slate-900/60 px-4 py-3 text-sm text-slate-300 transition hover:border-cyan-400/50 hover:text-cyan-300">
                  <div className="flex items-center gap-2">
                    <Upload className="h-4 w-4" />
                    <span>{resumeFile ? resumeFile.name : "Choose resume (PDF/DOCX)"}</span>
                  </div>
                  <input
                    type="file"
                    accept=".pdf,.docx,.doc"
                    onChange={handleResumeUpload}
                    disabled={uploading}
                    className="hidden"
                  />
                </label>
                {uploading && (
                  <div className="flex items-center gap-2 text-sm text-cyan-400">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Processing...</span>
                  </div>
                )}
              </div>
              {uploadStatus && (
                <p className={`text-xs ${uploadStatus.success ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {uploadStatus.message}
                </p>
              )}
            </div>

            {/* Done Button - appears after resume upload */}
            {showDoneButton && (
              <button
                type="button"
                onClick={handleDoneClick}
                disabled={uploading || scrapingStarted}
                className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 px-6 py-3 text-sm font-semibold text-white transition hover:from-cyan-400 hover:to-blue-400 shadow-lg shadow-cyan-500/25"
              >
                {scrapingStarted ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Scraping Jobs...
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-5 w-5" />
                    Done - Start Scraping
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>
            )}

            {/* Scraping In Progress Indicator */}
            {scrapingStarted && uploading && (
              <div className="rounded-lg border border-cyan-400/30 bg-cyan-500/10 p-4">
                <div className="flex items-center gap-3">
                  <Loader2 className="h-5 w-5 animate-spin text-cyan-400" />
                  <div>
                    <p className="text-sm font-medium text-cyan-300">Scraping in Progress...</p>
                    <p className="text-xs text-slate-400">Finding jobs across multiple platforms</p>
                  </div>
                </div>
              </div>
            )}

            <button
              type="submit"
              className="inline-flex items-center gap-2 rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-cyan-400"
            >
              <Filter className="h-4 w-4" />
              Apply Filters
            </button>
          </form>
        </GlassCard>

        {/* Job Roles Filter (Shows after scraping / when jobs exist) */}
        {jobs.length > 0 && (
          <div className="mb-2 mt-4 overflow-x-auto pb-2">
            <div className="flex w-max gap-2 border-b border-slate-800 pb-2">
              <button
                onClick={() => setSelectedRole("All")}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  selectedRole === "All"
                    ? "border-b-2 border-cyan-400 text-cyan-400"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                All Roles
              </button>
              {uniqueRoles.map((role) => (
                <button
                  key={role}
                  onClick={() => setSelectedRole(role)}
                  className={`px-4 py-2 text-sm font-medium transition-colors whitespace-nowrap ${
                    selectedRole === role
                      ? "border-b-2 border-cyan-400 text-cyan-400"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {role}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="space-y-8">
          {filteredJobs.length > 0 ? (
            <>
              {/* Best Match Section */}
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Star className="h-5 w-5 text-yellow-400 fill-yellow-400" />
                  <h2 className="text-xl font-semibold text-yellow-400">Best Match Found</h2>
                </div>
                <div className="relative rounded-2xl p-[2px] bg-gradient-to-r from-yellow-400 via-cyan-400 to-yellow-400 animate-pulse-slow shadow-[0_0_20px_rgba(250,204,21,0.3)]">
                  <div className="rounded-[14px] bg-slate-950">
                    <JobCard key={`best-${filteredJobs[0].id}`} job={filteredJobs[0]} />
                  </div>
                </div>
              </div>

              {/* Other Jobs Grid */}
              {filteredJobs.length > 1 && (
                <div className="space-y-4">
                  <h2 className="text-xl font-semibold text-slate-200">Other Opportunities</h2>
                  <div className="grid gap-4 md:grid-cols-2">
                    {filteredJobs.slice(1).map((job) => (
                      <JobCard key={job.id} job={job} />
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="col-span-full text-center py-12">
              <p className="text-lg text-slate-400">No jobs found. Upload your resume or apply filters to discover opportunities.</p>
            </div>
          )}
        </div>
      </section>
    </PageTransition>
  );
}
