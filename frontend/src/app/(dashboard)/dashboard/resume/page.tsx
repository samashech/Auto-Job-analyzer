"use client";

import { useState } from "react";
import { PageTransition } from "@/components/ui/page-transition";
import { useAppState } from "@/components/providers/app-state-provider";
import { Pencil, Save, X } from "lucide-react";

function Section({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <section className="border-t border-slate-700/70 pt-4">
      <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-300">{title}</h2>
      <ul className="mt-2 space-y-1 text-sm text-slate-200">
        {items.map((item, i) => (
          <li key={i}>• {item}</li>
        ))}
      </ul>
    </section>
  );
}

export default function ResumePage() {
  const { profile, updateProfile } = useAppState();
  const [isEditing, setIsEditing] = useState(false);
  const [editedProfile, setEditedProfile] = useState(profile);

  const handleSave = () => {
    updateProfile(editedProfile);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedProfile(profile);
    setIsEditing(false);
  };

  const handleArrayChange = (field: keyof typeof profile, value: string) => {
    setEditedProfile({ ...editedProfile, [field]: value.split('\n').filter(item => item.trim() !== '') });
  };

  return (
    <PageTransition>
      <section className="space-y-5 relative">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-semibold text-slate-100">Resume Builder</h1>
            <p className="mt-1 text-slate-400">ATS-friendly single-column resume generated from your profile data.</p>
          </div>
          {!isEditing ? (
            <button
              onClick={() => setIsEditing(true)}
              className="flex items-center gap-2 rounded-lg bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-400 transition hover:bg-cyan-500/20"
            >
              <Pencil className="h-4 w-4" /> Edit
            </button>
          ) : (
            <div className="flex gap-2">
              <button
                onClick={handleCancel}
                className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-slate-700"
              >
                <X className="h-4 w-4" /> Cancel
              </button>
              <button
                onClick={handleSave}
                className="flex items-center gap-2 rounded-lg bg-cyan-500 px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-cyan-400"
              >
                <Save className="h-4 w-4" /> Save
              </button>
            </div>
          )}
        </div>

        <article className="mx-auto w-full max-w-3xl rounded-2xl border border-slate-700/70 bg-slate-950/80 p-6 shadow-[0_20px_70px_rgba(2,6,23,0.6)]">
          {!isEditing ? (
            <>
              <header className="pb-4">
                <h2 className="text-2xl font-semibold text-slate-100">{profile.fullName}</h2>
                <p className="mt-1 text-sm text-slate-300">{profile.email} | {profile.phone}</p>
                <p className="mt-1 text-xs text-cyan-300">{profile.social.linkedIn} | {profile.social.github} | {profile.social.portfolio}</p>
              </header>

              <Section title="Education" items={profile.education} />
              <Section title="Technical Skills" items={profile.skills} />
              <Section title="Projects" items={profile.projects} />
              <Section title="Positions of Responsibility" items={profile.positionsOfResponsibility} />
              <Section title="Achievements & Certificates" items={[...profile.achievements, ...profile.certificates]} />
            </>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1 block text-sm text-slate-400">Full Name</label>
                  <input
                    className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200"
                    value={editedProfile.fullName}
                    onChange={(e) => setEditedProfile({ ...editedProfile, fullName: e.target.value })}
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm text-slate-400">Email</label>
                  <input
                    className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200"
                    value={editedProfile.email}
                    onChange={(e) => setEditedProfile({ ...editedProfile, email: e.target.value })}
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm text-slate-400">Phone</label>
                  <input
                    className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200"
                    value={editedProfile.phone}
                    onChange={(e) => setEditedProfile({ ...editedProfile, phone: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="mb-1 block text-sm text-slate-400">LinkedIn</label>
                  <input
                    className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200"
                    value={editedProfile.social.linkedIn}
                    onChange={(e) => setEditedProfile({ ...editedProfile, social: { ...editedProfile.social, linkedIn: e.target.value } })}
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm text-slate-400">GitHub</label>
                  <input
                    className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200"
                    value={editedProfile.social.github}
                    onChange={(e) => setEditedProfile({ ...editedProfile, social: { ...editedProfile.social, github: e.target.value } })}
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm text-slate-400">Portfolio</label>
                  <input
                    className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200"
                    value={editedProfile.social.portfolio}
                    onChange={(e) => setEditedProfile({ ...editedProfile, social: { ...editedProfile.social, portfolio: e.target.value } })}
                  />
                </div>
              </div>

              <div>
                <label className="mb-1 block text-sm text-slate-400">Education (one per line)</label>
                <textarea
                  className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200"
                  rows={3}
                  value={editedProfile.education.join('\n')}
                  onChange={(e) => handleArrayChange('education', e.target.value)}
                />
              </div>
              
              <div>
                <label className="mb-1 block text-sm text-slate-400">Skills (one per line)</label>
                <textarea
                  className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200"
                  rows={3}
                  value={editedProfile.skills.join('\n')}
                  onChange={(e) => handleArrayChange('skills', e.target.value)}
                />
              </div>

              <div>
                <label className="mb-1 block text-sm text-slate-400">Projects (one per line)</label>
                <textarea
                  className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200"
                  rows={3}
                  value={editedProfile.projects.join('\n')}
                  onChange={(e) => handleArrayChange('projects', e.target.value)}
                />
              </div>

              <div>
                <label className="mb-1 block text-sm text-slate-400">Positions of Responsibility (one per line)</label>
                <textarea
                  className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200"
                  rows={3}
                  value={editedProfile.positionsOfResponsibility.join('\n')}
                  onChange={(e) => handleArrayChange('positionsOfResponsibility', e.target.value)}
                />
              </div>

              <div>
                <label className="mb-1 block text-sm text-slate-400">Achievements & Certificates (one per line)</label>
                <textarea
                  className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200"
                  rows={3}
                  value={[...editedProfile.achievements, ...editedProfile.certificates].join('\n')}
                  onChange={(e) => {
                    const lines = e.target.value.split('\n').filter(item => item.trim() !== '');
                    setEditedProfile({ ...editedProfile, achievements: lines, certificates: [] });
                  }}
                />
              </div>
            </div>
          )}
        </article>
      </section>
    </PageTransition>
  );
}