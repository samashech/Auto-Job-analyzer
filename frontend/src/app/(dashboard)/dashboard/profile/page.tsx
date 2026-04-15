"use client";

import { useMemo, useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Save, UploadCloud } from "lucide-react";
import { useAppState } from "@/components/providers/app-state-provider";
import { GlassCard } from "@/components/ui/glass-card";
import { PageTransition } from "@/components/ui/page-transition";
import { ProfileFormValues, profileSchema } from "@/lib/validation";

const toCsv = (items: string[]) => items.join(", ");
const fromCsv = (value: string) => value.split(",").map((item) => item.trim()).filter(Boolean);

export default function ProfilePage() {
  const [mode, setMode] = useState<"view" | "edit">("view");
  const { profile, updateProfile } = useAppState();

  const defaultValues = useMemo<ProfileFormValues>(
    () => ({
      fullName: profile.fullName,
      email: profile.email,
      phone: profile.phone,
      about: profile.about,
      skills: toCsv(profile.skills),
      projects: toCsv(profile.projects),
      achievements: toCsv(profile.achievements),
      education: toCsv(profile.education),
      positionsOfResponsibility: toCsv(profile.positionsOfResponsibility),
      certificates: toCsv(profile.certificates),
      linkedIn: profile.social.linkedIn,
      github: profile.social.github,
      portfolio: profile.social.portfolio,
    }),
    [profile],
  );

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    values: defaultValues,
  });

  const onSubmit = (values: ProfileFormValues) => {
    updateProfile({
      ...profile,
      fullName: values.fullName,
      email: values.email,
      phone: values.phone,
      about: values.about,
      skills: fromCsv(values.skills),
      projects: fromCsv(values.projects),
      achievements: fromCsv(values.achievements),
      education: fromCsv(values.education),
      positionsOfResponsibility: fromCsv(values.positionsOfResponsibility),
      certificates: fromCsv(values.certificates),
      social: {
        linkedIn: values.linkedIn,
        github: values.github,
        portfolio: values.portfolio,
      },
    });
    setMode("view");
  };

  const uploadPhoto = (file?: File) => {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      updateProfile({ ...profile, photoDataUrl: String(reader.result || "") });
    };
    reader.readAsDataURL(file);
  };

  return (
    <PageTransition>
      <section className="space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-3xl font-semibold text-slate-100">Profile</h1>
            <p className="mt-1 text-slate-400">Switch between view and edit mode to keep your profile current.</p>
          </div>
          <div className="inline-flex rounded-lg border border-slate-700 p-1">
            <button
              type="button"
              onClick={() => setMode("view")}
              className={`rounded-md px-4 py-2 text-sm ${mode === "view" ? "bg-cyan-500 text-slate-900" : "text-slate-300"}`}
            >
              View
            </button>
            <button
              type="button"
              onClick={() => setMode("edit")}
              className={`rounded-md px-4 py-2 text-sm ${mode === "edit" ? "bg-cyan-500 text-slate-900" : "text-slate-300"}`}
            >
              Edit
            </button>
          </div>
        </div>

        {mode === "view" ? (
          <GlassCard>
            <div className="flex flex-col gap-4 md:flex-row md:items-start">
              <div className="h-20 w-20 overflow-hidden rounded-full border border-cyan-400/40 bg-slate-800">
                {profile.photoDataUrl ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={profile.photoDataUrl} alt="Profile" className="h-full w-full object-cover" />
                ) : null}
              </div>
              <div className="grid gap-3">
                <p className="text-xl font-semibold text-slate-100">{profile.fullName}</p>
                <p className="text-sm text-slate-400">{profile.email}</p>
                <p className="text-sm text-slate-400">{profile.phone}</p>
                <p className="max-w-2xl text-sm text-slate-300">{profile.about}</p>
              </div>
            </div>
          </GlassCard>
        ) : (
          <GlassCard>
            <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4">
              <div className="grid gap-4 md:grid-cols-2">
                <label className="space-y-1 text-sm text-slate-300">
                  Full Name
                  <input {...register("fullName")} className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2" />
                  {errors.fullName ? <span className="text-xs text-rose-400">{errors.fullName.message}</span> : null}
                </label>
                <label className="space-y-1 text-sm text-slate-300">
                  Email
                  <input {...register("email")} className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2" />
                  {errors.email ? <span className="text-xs text-rose-400">{errors.email.message}</span> : null}
                </label>
                <label className="space-y-1 text-sm text-slate-300">
                  Phone
                  <input {...register("phone")} className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2" />
                  {errors.phone ? <span className="text-xs text-rose-400">{errors.phone.message}</span> : null}
                </label>
                <label className="space-y-1 text-sm text-slate-300">
                  Profile Photo Upload
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(event) => uploadPhoto(event.target.files?.[0])}
                    className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
                  />
                </label>
              </div>

              <label className="space-y-1 text-sm text-slate-300">
                About Me
                <textarea {...register("about")} rows={3} className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2" />
                {errors.about ? <span className="text-xs text-rose-400">{errors.about.message}</span> : null}
              </label>

              <div className="grid gap-4 md:grid-cols-2">
                {[
                  "skills",
                  "projects",
                  "achievements",
                  "education",
                  "positionsOfResponsibility",
                  "certificates",
                ].map((field) => (
                  <label key={field} className="space-y-1 text-sm capitalize text-slate-300">
                    {field.replace(/([A-Z])/g, " $1")}
                    <input
                      {...register(field as keyof ProfileFormValues)}
                      className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
                    />
                    {errors[field as keyof ProfileFormValues] ? (
                      <span className="text-xs text-rose-400">{String(errors[field as keyof ProfileFormValues]?.message || "")}</span>
                    ) : null}
                  </label>
                ))}
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <label className="space-y-1 text-sm text-slate-300">
                  LinkedIn
                  <input {...register("linkedIn")} className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2" />
                </label>
                <label className="space-y-1 text-sm text-slate-300">
                  GitHub
                  <input {...register("github")} className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2" />
                </label>
                <label className="space-y-1 text-sm text-slate-300">
                  Portfolio
                  <input {...register("portfolio")} className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2" />
                </label>
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  className="inline-flex items-center gap-2 rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-cyan-400"
                >
                  <Save className="h-4 w-4" />
                  Save Profile
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setValue("fullName", profile.fullName);
                    setMode("view");
                  }}
                  className="inline-flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300"
                >
                  <UploadCloud className="h-4 w-4" />
                  Cancel
                </button>
              </div>
            </form>
          </GlassCard>
        )}
      </section>
    </PageTransition>
  );
}
