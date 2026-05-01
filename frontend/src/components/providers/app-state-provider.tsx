"use client";

import { createContext, useContext, useState, useEffect } from "react";
import { defaultProfile } from "@/lib/constants";
import { ActivityItem, AuthUser, Job, ProfileData } from "@/lib/types";

type AppState = {
  users: AuthUser[];
  currentUser: AuthUser | null;
  profile: ProfileData;
  savedJobIds: string[];
  appliedJobIds: string[];
  activities: ActivityItem[];
  jobs: Job[];
  registerUser: (user: AuthUser) => Promise<{ ok: boolean; message: string }>;
  loginUser: (email: string, password: string) => Promise<{ ok: boolean; message: string; attempts: number }>;
  logoutUser: () => Promise<void>;
  updateProfile: (profileData: ProfileData) => Promise<void>;
  toggleSaveJob: (jobId: string) => Promise<void>;
  applyJob: (jobId: string) => Promise<void>;
  getJobById: (jobId: string) => Job | undefined;
  fetchJobs: (userId: string) => Promise<void>;
};

const AppStateContext = createContext<AppState | undefined>(undefined);

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

const STORAGE_KEYS = {
  activities: "align_activities",
  failedAttempts: "align_failed_attempts",
  userId: "align_user_id",
};

const parseJson = <T,>(value: string | null, fallback: T): T => {
  if (!value) return fallback;
  try {
    return JSON.parse(value) as T;
  } catch {
    return fallback;
  }
};

const readStorage = <T,>(key: string, fallback: T) => {
  if (typeof window === "undefined") return fallback;
  return parseJson<T>(window.localStorage.getItem(key), fallback);
};

export function AppStateProvider({ children }: { children: React.ReactNode }) {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [profile, setProfile] = useState<ProfileData>(defaultProfile);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [savedJobIds, setSavedJobIds] = useState<string[]>([]);
  const [appliedJobIds, setAppliedJobIds] = useState<string[]>([]);
  
  const [activities, setActivities] = useState<ActivityItem[]>([]);

  useEffect(() => {
    setActivities(readStorage<ActivityItem[]>(STORAGE_KEYS.activities, []));
  }, []);

  const fetchJobs = async (userId: string) => {
    try {
      const res = await fetch(`${API_URL}/api/all-jobs/${userId}`);
      if (res.ok) {
        const data = await res.json();
        const formattedJobs: Job[] = (data.jobs || []).map((j: Record<string, any>) => ({
          id: String(j.id),
          title: j.title,
          company: j.company || "Unknown",
          salary: j.salary || "Not specified",
          location: j.location || "Remote",
          source: j.source || "LinkedIn",
          sourceUrl: j.url,
          description: j.description || "",
          job_function: j.job_function || "",
          expiry_date: j.expiry_date || "",
          skills: j.skills || [],
          // Normalize job type from backend (e.g., "Full-time" -> "Full Time")
          type: (j.type || [j.job_type || "Full Time"]).map((t: string) => {
            const lower = t.toLowerCase();
            if (lower.includes("full")) return "Full Time";
            if (lower.includes("part")) return "Part Time";
            if (lower.includes("remote")) return "Remote";
            if (lower.includes("intern")) return "Internship";
            return t as any;
          }),
          region: j.region || "India",
          stateOrContinent: j.stateOrContinent || "All",
          relevance_score: j.relevance_score || 0,
        }));
        setJobs(formattedJobs);

        // Populate saved jobs
        const savedIds = (data.jobs || []).filter((j: Record<string, any>) => j.saved).map((j: Record<string, any>) => String(j.id));
        setSavedJobIds(savedIds);
      }
    } catch (e) {
      console.error("Failed to fetch jobs:", e);
    }
  };

  const fetchApplications = async (userId: string) => {
    try {
      const res = await fetch(`${API_URL}/api/applications/${userId}`);
      if (res.ok) {
        const data = await res.json();
        const appliedIds = data.applications.map((a: Record<string, any>) => String(a.job_id));
        setAppliedJobIds(appliedIds);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    const checkSession = async () => {
      try {
        const res = await fetch(`${API_URL}/auth/check-session`, {
          credentials: "include",
        });
        const data = await res.json();
        if (data.logged_in && data.user) {
          setCurrentUser({
            fullName: data.user.name,
            email: data.user.email,
            password: "",
          });
          localStorage.setItem(STORAGE_KEYS.userId, String(data.user.id));
          fetchJobs(String(data.user.id));
          fetchApplications(String(data.user.id));
        }
      } catch (e) {
        console.warn("Session check failed (Backend might be offline or unreachable)");
      }
    };
    checkSession();
  }, []);

  const persist = {
    activities: (next: ActivityItem[]) => localStorage.setItem(STORAGE_KEYS.activities, JSON.stringify(next)),
  };

  const registerUser = async (user: AuthUser) => {
    try {
      const res = await fetch(`${API_URL}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: user.email, password: user.password, name: user.fullName }),
      });
      const data = await res.json();
      if (res.ok) {
        return { ok: true, message: data.message };
      }
      return { ok: false, message: data.error || "Failed to register" };
    } catch (e) {
      return { ok: false, message: "Network error" };
    }
  };

  const loginUser = async (email: string, password: string) => {
    const attempts = Number(localStorage.getItem(STORAGE_KEYS.failedAttempts) || "0");
    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem(STORAGE_KEYS.failedAttempts, "0");
        localStorage.setItem(STORAGE_KEYS.userId, String(data.user.id));
        setCurrentUser({ fullName: data.user.name, email: data.user.email, password: "" });
        setProfile({
          fullName: data.user.name,
          email: data.user.email,
          phone: data.user.phone || "",
          about: data.user.about || "",
          skills: data.user.skills ? data.user.skills.split(", ") : [],
          projects: data.user.projects ? data.user.projects.split(", ") : [],
          achievements: data.user.achievements ? data.user.achievements.split(", ") : [],
          education: data.user.education ? data.user.education.split(", ") : [],
          positionsOfResponsibility: data.user.positions_of_responsibility
            ? data.user.positions_of_responsibility.split(", ")
            : [],
          certificates: data.user.certificates ? data.user.certificates.split(", ") : [],
          photoDataUrl: data.user.photo_data_url || "",
          social: {
            linkedIn: data.user.social_linkedin || "",
            github: data.user.social_github || "",
            portfolio: data.user.social_portfolio || "",
          },
        });
        
        fetchJobs(String(data.user.id));
        fetchApplications(String(data.user.id));
        
        return { ok: true, message: "Login successful.", attempts: 0 };
      } else {
        const nextAttempts = attempts + 1;
        localStorage.setItem(STORAGE_KEYS.failedAttempts, String(nextAttempts));
        return { ok: false, message: data.error || "Login failed.", attempts: nextAttempts };
      }
    } catch (e) {
      const nextAttempts = attempts + 1;
      localStorage.setItem(STORAGE_KEYS.failedAttempts, String(nextAttempts));
      return { ok: false, message: "Network error", attempts: nextAttempts };
    }
  };

  const logoutUser = async () => {
    setCurrentUser(null);
    localStorage.removeItem(STORAGE_KEYS.userId);
    try {
      await fetch(`${API_URL}/auth/logout`, { method: "POST" });
    } catch (e) {
      console.error(e);
    }
  };

  const updateProfile = async (profileData: ProfileData) => {
    setProfile(profileData);
    const userId = localStorage.getItem(STORAGE_KEYS.userId);
    if (!userId) return;

    try {
      await fetch(`${API_URL}/api/update-profile-preferences`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          name: profileData.fullName,
          email: profileData.email,
          phone: profileData.phone,
          skills: profileData.skills.join(", "),
          about: profileData.about,
          projects: profileData.projects.join(", "),
          achievements: profileData.achievements.join(", "),
          education: profileData.education.join(", "),
          certificates: profileData.certificates.join(", "),
          positions_of_responsibility: profileData.positionsOfResponsibility.join(", "),
          photoDataUrl: profileData.photoDataUrl,
          social: {
            github: profileData.social.github,
            linkedIn: profileData.social.linkedIn,
            portfolio: profileData.social.portfolio,
          },
        }),
      });
    } catch (e) {
      console.error("Failed to update profile", e);
    }
  };

  const addActivity = (title: string) => {
    const activity: ActivityItem = {
      id: crypto.randomUUID(),
      title,
      timestamp: new Date().toLocaleString(),
    };
    setActivities((previous) => {
      const next = [activity, ...previous].slice(0, 12);
      persist.activities(next);
      return next;
    });
  };

  const toggleSaveJob = async (jobId: string) => {
    const userId = localStorage.getItem(STORAGE_KEYS.userId);
    if (!userId) return;

    const isSaved = savedJobIds.includes(jobId);
    
    // Optimistic update
    setSavedJobIds((previous) => {
      return isSaved ? previous.filter((id) => id !== jobId) : [...previous, jobId];
    });
    addActivity(isSaved ? "Removed a job from saved list" : "Saved a new job from recommendations");

    try {
      await fetch(`${API_URL}/api/toggle-save-job`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, job_id: jobId }),
      });
    } catch (e) {
      console.error("Failed to toggle save", e);
      // Revert on error
      setSavedJobIds((previous) => {
        return isSaved ? [...previous, jobId] : previous.filter((id) => id !== jobId);
      });
    }
  };

  const applyJob = async (jobId: string) => {
    if (appliedJobIds.includes(jobId)) return;
    const userId = localStorage.getItem(STORAGE_KEYS.userId);
    if (!userId) return;

    setAppliedJobIds((previous) => [...previous, jobId]);
    addActivity("Applied to a job from Align feed");

    try {
      await fetch(`${API_URL}/api/application`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, job_id: jobId, status: "Applied" }),
      });
    } catch (e) {
      console.error("Failed to apply", e);
    }
  };

  const getJobById = (jobId: string) => jobs.find((job) => job.id === jobId);

  const value = {
    users: [], // We don't have access to all users from backend
    currentUser,
    profile,
    savedJobIds,
    appliedJobIds,
    activities,
    jobs,
    registerUser,
    loginUser,
    logoutUser,
    updateProfile,
    toggleSaveJob,
    applyJob,
    getJobById,
    fetchJobs,
  };

  return <AppStateContext.Provider value={value}>{children}</AppStateContext.Provider>;
}

export const useAppState = () => {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error("useAppState must be used inside AppStateProvider");
  }
  return context;
};
