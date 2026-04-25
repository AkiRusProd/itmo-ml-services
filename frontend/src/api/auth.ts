import { apiClient } from "./client";
import type { CurrentUser, LoginRequest, RegisterRequest, TokenResponse } from "../types/auth";


export async function registerUser(payload: RegisterRequest): Promise<CurrentUser> {
  const response = await apiClient.post("/api/v1/auth/register", payload);
  return response.data;
}

export async function loginUser(payload: LoginRequest): Promise<TokenResponse> {
  const response = await apiClient.post("/api/v1/auth/login", payload);
  return response.data;
}

export async function fetchCurrentUser(): Promise<CurrentUser> {
  const response = await apiClient.get("/api/v1/users/me");
  return response.data;
}
