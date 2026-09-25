import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedPrefixes = ["/dashboard", "/hosted-zones", "/traffic-policies", "/health-checks", "/resolver", "/profiles"];

export function middleware(req: NextRequest) {
  const path = req.nextUrl.pathname;
  const protectedRoute = protectedPrefixes.some((prefix) => path === prefix || path.startsWith(`${prefix}/`));
  const token = req.cookies.get("route53_session")?.value;

  if (protectedRoute && !token) {
    const login = new URL("/login", req.url);
    login.searchParams.set("next", path);
    return NextResponse.redirect(login);
  }

  if (path === "/login" && token) {
    return NextResponse.redirect(new URL("/hosted-zones", req.url));
  }

  return NextResponse.next();
}

export const config = { matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"] };
