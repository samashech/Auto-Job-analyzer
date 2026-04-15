# Align Frontend

Align is a dark, premium, high-performance job scraping platform frontend built with Next.js App Router.

## Stack

- Next.js 16 (App Router)
- TypeScript
- Tailwind CSS
- Framer Motion
- React Hook Form + Zod
- Lucide React

## Features

- Scrollable landing page with: Hero, About, How It Works, Features, Security, FAQs
- Authentication UI with strict validation and forgot-password state after 3 failed attempts
- Persistent dashboard shell with fixed desktop sidebar and responsive mobile navigation
- Dashboard analytics widgets and recent activity feed
- My Jobs filtering engine:
	- India vs International toggle
	- State/Continent filtering
	- Job type filters
	- Top 5 skills matching and ranking
- Saved Jobs and Applied Jobs tracking views
- Profile page with View/Edit modes, strict input validation, and photo upload
- ATS-friendly resume builder generated from profile data

## Validation Rules

- Name: alphabetic characters and spaces only
- Phone: digits only, 10-14 length
- Email: valid email format
- URLs: valid URL format

## Run Locally

```bash
npm install
npm run dev
```

Open http://localhost:3000

## Quality Checks

```bash
npm run lint
npm run build
```

## Route Map

- /
- /login
- /signup
- /dashboard
- /dashboard/profile
- /dashboard/my-jobs
- /dashboard/saved-jobs
- /dashboard/applied-jobs
- /dashboard/resume
- /dashboard/settings
