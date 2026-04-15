"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { AuthCard } from "@/components/auth/auth-card";
import { useAppState } from "@/components/providers/app-state-provider";
import { AuthLoginValues, ForgotPasswordValues, authLoginSchema, forgotPasswordSchema } from "@/lib/validation";

export default function LoginPage() {
  const router = useRouter();
  const { loginUser } = useAppState();
  const [error, setError] = useState<string>("");
  const [showForgot, setShowForgot] = useState(false);
  const [forgotMessage, setForgotMessage] = useState("");

  const loginForm = useForm<AuthLoginValues>({
    resolver: zodResolver(authLoginSchema),
    defaultValues: { email: "", password: "" },
  });

  const forgotForm = useForm<ForgotPasswordValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: "" },
  });

  const onLogin = async (values: AuthLoginValues) => {
    const result = await loginUser(values.email, values.password);
    if (!result.ok) {
      setError(result.message);
      if (result.attempts >= 3) setShowForgot(true);
      return;
    }
    router.push("/dashboard");
  };

  return (
    <main className="grid min-h-screen place-items-center px-4 py-8">
      <AuthCard
        title="Welcome back"
        subtitle="Sign in to continue your Align workflow"
        footerLabel="No account yet?"
        footerHref="/signup"
        footerAction="Create one"
      >
        {!showForgot ? (
          <form onSubmit={loginForm.handleSubmit(onLogin)} className="space-y-4">
            <label className="block space-y-1 text-sm text-slate-300">
              Email
              <input
                {...loginForm.register("email")}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
              />
              {loginForm.formState.errors.email ? (
                <span className="text-xs text-rose-400">{loginForm.formState.errors.email.message}</span>
              ) : null}
            </label>

            <label className="block space-y-1 text-sm text-slate-300">
              Password
              <input
                type="password"
                {...loginForm.register("password")}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
              />
              {loginForm.formState.errors.password ? (
                <span className="text-xs text-rose-400">{loginForm.formState.errors.password.message}</span>
              ) : null}
            </label>

            {error ? <p className="text-sm text-rose-400">{error}</p> : null}

            <button type="submit" className="w-full rounded-lg bg-cyan-500 px-3 py-2 font-semibold text-slate-900 hover:bg-cyan-400">
              Log In
            </button>

            <button
              type="button"
              onClick={() => setShowForgot(true)}
              className="w-full text-center text-sm text-cyan-300 transition hover:text-cyan-200"
            >
              Forgot Password?
            </button>
          </form>
        ) : (
          <form
            onSubmit={forgotForm.handleSubmit((values) => {
              setForgotMessage(`Password reset link sent to ${values.email}.`);
            })}
            className="space-y-4"
          >
            <p className="rounded-lg border border-amber-300/30 bg-amber-500/10 px-3 py-2 text-sm text-amber-200">
              Forgot Password mode was activated after 3 failed login attempts.
            </p>
            <label className="block space-y-1 text-sm text-slate-300">
              Registered Email
              <input
                {...forgotForm.register("email")}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
              />
              {forgotForm.formState.errors.email ? (
                <span className="text-xs text-rose-400">{forgotForm.formState.errors.email.message}</span>
              ) : null}
            </label>
            <button type="submit" className="w-full rounded-lg bg-cyan-500 px-3 py-2 font-semibold text-slate-900 hover:bg-cyan-400">
              Send Reset Link
            </button>
            {forgotMessage ? <p className="text-sm text-emerald-300">{forgotMessage}</p> : null}
            <Link href="/signup" className="block text-center text-sm text-cyan-300 hover:text-cyan-200">
              Need account? Sign Up
            </Link>
          </form>
        )}
      </AuthCard>
    </main>
  );
}
