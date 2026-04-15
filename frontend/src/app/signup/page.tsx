"use client";

import Link from "next/link";
import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { AuthCard } from "@/components/auth/auth-card";
import { useAppState } from "@/components/providers/app-state-provider";
import { AuthSignupValues, authSignupSchema } from "@/lib/validation";

export default function SignupPage() {
  const { registerUser } = useAppState();
  const [status, setStatus] = useState<{ type: "success" | "error"; message: string } | null>(null);

  const form = useForm<AuthSignupValues>({
    resolver: zodResolver(authSignupSchema),
    defaultValues: {
      fullName: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  });

  return (
    <main className="grid min-h-screen place-items-center px-4 py-8">
      <AuthCard
        title="Create your Align account"
        subtitle="Use one unique email and a secure password"
        footerLabel="Already registered?"
        footerHref="/login"
        footerAction="Log in"
      >
        <form
          onSubmit={form.handleSubmit(async (values) => {
            const result = await registerUser({
              fullName: values.fullName,
              email: values.email,
              password: values.password,
            });
            setStatus({ type: result.ok ? "success" : "error", message: result.message });
            if (result.ok) form.reset();
          })}
          className="space-y-4"
        >
          <label className="block space-y-1 text-sm text-slate-300">
            Full Name
            <input {...form.register("fullName")} className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2" />
            {form.formState.errors.fullName ? <span className="text-xs text-rose-400">{form.formState.errors.fullName.message}</span> : null}
          </label>

          <label className="block space-y-1 text-sm text-slate-300">
            Email
            <input {...form.register("email")} className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2" />
            {form.formState.errors.email ? <span className="text-xs text-rose-400">{form.formState.errors.email.message}</span> : null}
          </label>

          <label className="block space-y-1 text-sm text-slate-300">
            Password
            <input
              type="password"
              {...form.register("password")}
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
            />
            {form.formState.errors.password ? <span className="text-xs text-rose-400">{form.formState.errors.password.message}</span> : null}
          </label>

          <label className="block space-y-1 text-sm text-slate-300">
            Confirm Password
            <input
              type="password"
              {...form.register("confirmPassword")}
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
            />
            {form.formState.errors.confirmPassword ? (
              <span className="text-xs text-rose-400">{form.formState.errors.confirmPassword.message}</span>
            ) : null}
          </label>

          {status ? (
            <p className={`text-sm ${status.type === "success" ? "text-emerald-300" : "text-rose-400"}`}>{status.message}</p>
          ) : null}

          <button type="submit" className="w-full rounded-lg bg-cyan-500 px-3 py-2 font-semibold text-slate-900 hover:bg-cyan-400">
            Sign Up
          </button>

          <Link href="/login" className="block text-center text-sm text-cyan-300 hover:text-cyan-200">
            Back to Login
          </Link>
        </form>
      </AuthCard>
    </main>
  );
}
