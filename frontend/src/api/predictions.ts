import { apiClient } from "./client";
import type {
  PredictionCreateResponse,
  PredictionDetail,
  PredictionListItem,
  PredictionPayload,
} from "../types/prediction";


export async function createPrediction(
  payload: PredictionPayload,
): Promise<PredictionCreateResponse> {
  const response = await apiClient.post("/api/v1/predictions", payload);
  return response.data;
}

export async function fetchPredictions(): Promise<PredictionListItem[]> {
  const response = await apiClient.get("/api/v1/predictions");
  return response.data;
}

export async function fetchPrediction(id: number): Promise<PredictionDetail> {
  const response = await apiClient.get(`/api/v1/predictions/${id}`);
  return response.data;
}
