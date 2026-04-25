import { apiClient } from "./client";
import type {
  PromoCodeCreateRequest,
  PromoCodeRedeemRequest,
  PromoCodeRedeemResponse,
  PromoCodeResponse,
} from "../types/promo";


export async function createPromoCode(
  payload: PromoCodeCreateRequest,
): Promise<PromoCodeResponse> {
  const response = await apiClient.post("/api/v1/promo-codes", payload);
  return response.data;
}

export async function redeemPromoCode(
  payload: PromoCodeRedeemRequest,
): Promise<PromoCodeRedeemResponse> {
  const response = await apiClient.post("/api/v1/promo-codes/redeem", payload);
  return response.data;
}
