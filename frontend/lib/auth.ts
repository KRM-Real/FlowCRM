import { apiFetch } from "@/lib/api-client";
import type { AuthUser, LoginInput, RegisterInput } from "@/types/auth";

type AuthEnvelope = {
  user: AuthUser;
};

type RegisterResponse = {
  message: string;
  user: AuthUser;
};

export async function login(values: LoginInput) {
  return apiFetch<AuthEnvelope>("/api/auth/login/", {
    method: "POST",
    body: JSON.stringify(values),
    skipAuthRefresh: true,
  });
}

export async function register(values: RegisterInput) {
  return apiFetch<RegisterResponse>("/api/auth/register/", {
    method: "POST",
    body: JSON.stringify(values),
    skipAuthRefresh: true,
  });
}

export async function getCurrentUser() {
  return apiFetch<AuthUser>("/api/auth/me/");
}

export async function logout() {
  return apiFetch<null>("/api/auth/logout/", {
    method: "POST",
    skipAuthRefresh: true,
  });
}
