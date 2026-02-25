import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  UpdateUserFullNameRequest,
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
