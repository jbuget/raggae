import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  UpdateUserFullNameRequest,
  UpdateUserLocaleRequest,
  UpsertUserProjectDefaultsRequest,
  UserProjectDefaultsResponse,
  UserResponse,
} from "@/lib/types/api";
import { apiFetch } from "./client";

export function register(data: RegisterRequest): Promise<UserResponse> {
  return apiFetch<UserResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function login(data: LoginRequest): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getCurrentUser(token: string): Promise<UserResponse> {
  return apiFetch<UserResponse>("/auth/me", { token });
}

export function updateUserFullName(
  token: string,
  data: UpdateUserFullNameRequest,
): Promise<UserResponse> {
  return apiFetch<UserResponse>("/auth/me/full-name", {
    method: "PATCH",
    body: JSON.stringify(data),
    token,
  });
}

export function updateUserLocale(
  token: string,
  data: UpdateUserLocaleRequest,
): Promise<UserResponse> {
  return apiFetch<UserResponse>("/auth/me/locale", {
    method: "PATCH",
    body: JSON.stringify(data),
    token,
  });
}

export function getUserProjectDefaults(
  token: string,
): Promise<UserProjectDefaultsResponse | null> {
  return apiFetch<UserProjectDefaultsResponse | null>("/auth/me/project-defaults", { token });
}

export function upsertUserProjectDefaults(
  token: string,
  data: UpsertUserProjectDefaultsRequest,
): Promise<UserProjectDefaultsResponse> {
  return apiFetch<UserProjectDefaultsResponse>("/auth/me/project-defaults", {
    method: "PUT",
    body: JSON.stringify(data),
    token,
  });
}
