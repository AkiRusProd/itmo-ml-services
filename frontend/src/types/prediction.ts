export type PredictionPayload = {
  MedInc: number;
  HouseAge: number;
  AveRooms: number;
  AveBedrms: number;
  Population: number;
  AveOccup: number;
  Latitude: number;
  Longitude: number;
  cost_credits: number;
};

export type PredictionCreateResponse = {
  id: number;
  status: string;
  task_id: string | null;
  cost_credits: number;
  prediction: number | null;
  target_name: string | null;
  model_name: string | null;
  model_version: string | null;
};

export type PredictionListItem = {
  id: number;
  status: string;
  task_id: string | null;
  cost_credits: number;
  created_at: string;
  prediction: number | null;
  model_name: string | null;
};

export type PredictionDetail = {
  id: number;
  status: string;
  task_id: string | null;
  cost_credits: number;
  input_payload: Record<string, number>;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  prediction: number | null;
  target_name: string | null;
  model_name: string | null;
  model_version: string | null;
};
