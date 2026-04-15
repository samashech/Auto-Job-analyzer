import { ProfileData } from "@/lib/types";

export const defaultProfile: ProfileData = {
  fullName: "Alex Carter",
  email: "alex.carter@align.dev",
  phone: "9876543210",
  about: "Frontend-focused engineer building high-performance web products with strong UX fundamentals.",
  skills: ["React", "Next.js", "TypeScript", "Tailwind", "Framer Motion"],
  projects: [
    "Built a multi-tenant analytics dashboard for 30k+ monthly users.",
    "Implemented a design system that cut UI development time by 35%.",
  ],
  achievements: [
    "Top 5 finalist in HackVerse 2025",
    "Published 12 technical articles on frontend performance",
  ],
  education: ["B.Tech in Computer Science, 2025"],
  positionsOfResponsibility: ["Frontend Lead, Developer Student Club"],
  certificates: ["AWS Cloud Practitioner", "Meta Front-End Developer"],
  social: {
    linkedIn: "https://www.linkedin.com",
    github: "https://github.com",
    portfolio: "https://portfolio.example.com",
  },
};

export const dashboardLinks = [
  { label: "Home", href: "/dashboard" },
  { label: "Profile", href: "/dashboard/profile" },
  { label: "My Jobs", href: "/dashboard/my-jobs" },
  { label: "Saved Jobs", href: "/dashboard/saved-jobs" },
  { label: "Applied Jobs", href: "/dashboard/applied-jobs" },
  { label: "Resume", href: "/dashboard/resume" },
  { label: "Settings", href: "/dashboard/settings" },
];
