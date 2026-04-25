export type Wallet = {
  id: number;
  user_id: number;
  balance: number;
  created_at: string;
  updated_at: string;
};

export type Transaction = {
  id: number;
  amount: number;
  transaction_type: string;
  description: string | null;
  created_at: string;
};

export type WalletTopUpRequest = {
  amount: number;
};

export type WalletTopUpResponse = {
  message: string;
  wallet_balance: number;
  credited_amount: number;
};
