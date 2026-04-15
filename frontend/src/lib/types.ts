export type JobType = "Full Time" | "Part Time" | "Remote" | "Internship";

export type JobLocationMode = "India" | "International";

export type Job = {
  id: string;
  title: string;
  company: string;
  salary: string;
  location: string;
  source: "LinkedIn" | "Naukri" | "Indeed" | "Wellfound";
  sourceUrl: string;
  skills: string[];
  type: JobType[];
  region: JobLocationMode;
  stateOrContinent: string;
  relevance_score?: number; // Backend relevance score (0-100)
};

export type SocialLinks = {
  linkedIn: string;
  github: string;
  portfolio: string;
};

export type ProfileData = {
  fullName: string;
  email: string;
  phone: string;
  about: string;
  skills: string[];
  projects: string[];
  achievements: string[];
  education: string[];
  positionsOfResponsibility: string[];
  certificates: string[];
  photoDataUrl?: string;
  social: SocialLinks;
};

export type ActivityItem = {
  id: string;
  title: string;
  timestamp: string;
};

export type AuthUser = {
  fullName: string;
  email: string;
  password: string;
};
