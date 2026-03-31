import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { ACCESS_COOKIE_NAME } from "@/lib/env";

const protectedPaths = ["/dashboard"];
const authPaths = ["/login", "/register"];

export function proxy(request: NextRequest) {
  const accessCookie = request.cookies.get(ACCESS_COOKIE_NAME);
  const { pathname } = request.nextUrl;

  const isProtectedPath = protectedPaths.some((path) =>
    pathname.startsWith(path),
  );
  const isAuthPath = authPaths.some((path) => pathname.startsWith(path));

  if (isProtectedPath && !accessCookie) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (isAuthPath && accessCookie) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/login", "/register"],
};
