import { apiClient } from "./client";
import type {
  Transaction,
  Wallet,
  WalletTopUpRequest,
  WalletTopUpResponse,
} from "../types/wallet";


export async function fetchWallet(): Promise<Wallet> {
  const response = await apiClient.get("/api/v1/wallet");
  return response.data;
}

export async function fetchTransactions(): Promise<Transaction[]> {
  const response = await apiClient.get("/api/v1/wallet/transactions");
  return response.data;
}

export async function topUpWallet(payload: WalletTopUpRequest): Promise<WalletTopUpResponse> {
  const response = await apiClient.post("/api/v1/wallet/top-up", payload);
  return response.data;
}
