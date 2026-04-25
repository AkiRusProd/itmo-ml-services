export type PromoCodeCreateRequest = {
  code: string;
  credit_amount: number;
  max_activations: number;
  expires_at: string | null;
};

export type PromoCodeRedeemRequest = {
  code: string;
};

export type PromoCodeResponse = {
  id: number;
  code: string;
  credit_amount: number;
  is_active: boolean;
  max_activations: number;
  activation_count: number;
  expires_at: string | null;
  created_at: string;
};

export type PromoCodeRedeemResponse = {
  message: string;
  code: string;
  credited_amount: number;
  wallet_balance: number;
};
