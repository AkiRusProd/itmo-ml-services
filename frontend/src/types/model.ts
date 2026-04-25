export type MLModel = {
  id: number;
  name: string;
  version: string;
  artifact_path: string;
  target_name: string;
  features: string[];
  is_active: boolean;
  created_at: string;
};
