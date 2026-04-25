import { apiClient } from "./client";
import type { MLModel } from "../types/model";


export async function fetchCurrentModel(): Promise<MLModel> {
  const response = await apiClient.get("/api/v1/models/current");
  return response.data;
}
