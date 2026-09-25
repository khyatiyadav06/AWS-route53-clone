import type { DNSRecord, Page, User, Zone } from "../types";

const API = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api").replace(/\/$/, "");

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) { super(message); this.status = status; }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("route53_token") : null;
  const headers = new Headers(options?.headers);
  if (!headers.has("Content-Type") && options?.body) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API}${path}`, { ...options, headers, cache: "no-store" });
  const data = await res.json().catch(() => ({}));
  if (res.status === 401 && typeof window !== "undefined") {
    localStorage.removeItem("route53_token");
    localStorage.removeItem("route53_user");
    document.cookie = "route53_session=; Max-Age=0; Path=/; SameSite=Lax";
    if (!location.pathname.startsWith("/login")) location.assign(`/login?next=${encodeURIComponent(location.pathname)}`);
  }
  if (!res.ok) throw new ApiError(data.detail || "Request failed", res.status);
  return data as T;
}

export const api = {
  login: async (email: string, password: string) => {
    const data = await request<{ token: string; user: User }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
    if (typeof window !== "undefined") {
      localStorage.setItem("route53_token", data.token);
      localStorage.setItem("route53_user", JSON.stringify(data.user));
      document.cookie = `route53_session=${data.token}; Path=/; Max-Age=86400; SameSite=Lax`;
    }
    return data.user;
  },
  logout: async () => {
    try { await request<{ message: string }>("/auth/logout", { method: "POST" }); }
    finally {
      if (typeof window !== "undefined") {
        localStorage.removeItem("route53_token"); localStorage.removeItem("route53_user");
        document.cookie = "route53_session=; Max-Age=0; Path=/; SameSite=Lax";
      }
    }
  },
  session: () => request<User>("/auth/session"),
  zones: (page = 1, search = "") => request<Page<Zone>>(`/hosted-zones?page=${page}&page_size=10&search=${encodeURIComponent(search)}`),
  zone: (id: number) => request<Zone>(`/hosted-zones/${id}`),
  createZone: (body: Pick<Zone, "name" | "description" | "zone_type">) => request<Zone>("/hosted-zones", { method: "POST", body: JSON.stringify(body) }),
  updateZone: (id: number, body: Pick<Zone, "name" | "description" | "zone_type">) => request<Zone>(`/hosted-zones/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  deleteZone: (id: number) => request<{ message: string }>(`/hosted-zones/${id}`, { method: "DELETE" }),
  records: (zoneId: number, page = 1, search = "") => request<Page<DNSRecord>>(`/hosted-zones/${zoneId}/records?page=${page}&page_size=10&search=${encodeURIComponent(search)}`),
  createRecord: (zoneId: number, body: Omit<DNSRecord, "id" | "hosted_zone_id" | "created_at" | "updated_at">) => request<DNSRecord>(`/hosted-zones/${zoneId}/records`, { method: "POST", body: JSON.stringify(body) }),
  updateRecord: (id: number, body: Omit<DNSRecord, "id" | "hosted_zone_id" | "created_at" | "updated_at">) => request<DNSRecord>(`/records/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  deleteRecord: (id: number) => request<{ message: string }>(`/records/${id}`, { method: "DELETE" }),
};
