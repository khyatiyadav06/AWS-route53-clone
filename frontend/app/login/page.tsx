"use client";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";
import { LockKeyhole, UserRound } from "lucide-react";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("demo@route53.local"); const [password, setPassword] = useState("Route53Demo123"); const [error, setError] = useState(""); const [loading, setLoading] = useState(false);
  async function submit(e: FormEvent) { e.preventDefault(); setError(""); setLoading(true); try { await api.login(email, password); const next = typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("next") : null; router.replace(next && next.startsWith("/") ? next : "/hosted-zones"); } catch (err) { setError(err instanceof Error ? err.message : "Unable to sign in"); } finally { setLoading(false); } }
  return <main className="min-h-screen bg-[#eaeded] flex items-center justify-center p-6"><div className="w-full max-w-[460px]">
    <div className="flex justify-center mb-7"><div className="aws-wordmark"><span>aws</span><b> Management Console</b></div></div>
    <section className="bg-white border border-[#c6c6c6] shadow-sm rounded-sm p-8"><div className="mb-7"><h1 className="text-[28px] font-normal text-[#161e2d]">Sign in</h1><p className="text-sm text-gray-600 mt-2">Sign in to the Route 53 management console</p></div>
      {error && <div role="alert" className="mb-5 aws-alert-error">{error}</div>}
      <form onSubmit={submit} className="space-y-5"><label className="aws-label">Email address<div className="relative mt-1"><UserRound className="field-icon" size={17}/><input required type="email" autoComplete="email" className="aws-input pl-10" value={email} onChange={e=>setEmail(e.target.value)}/></div></label><label className="aws-label">Password<div className="relative mt-1"><LockKeyhole className="field-icon" size={17}/><input required type="password" autoComplete="current-password" className="aws-input pl-10" value={password} onChange={e=>setPassword(e.target.value)}/></div></label><button disabled={loading} className="btn btn-primary w-full py-2.5">{loading ? "Signing in…" : "Sign in"}</button></form>
      <div className="mt-6 pt-5 border-t text-xs text-gray-600"><strong>Demo account</strong><br/>demo@route53.local · Route53Demo123</div>
    </section><p className="text-center text-xs text-gray-500 mt-6">Route 53 Clone · Mock AWS console for evaluation purposes</p>
  </div></main>;
}
