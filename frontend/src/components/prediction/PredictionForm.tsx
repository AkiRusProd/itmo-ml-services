import { useState } from "react";

import type { PredictionPayload } from "../../types/prediction";

type PredictionFormProps = {
  onSubmit: (payload: PredictionPayload) => Promise<void>;
  isSubmitting: boolean;
};

const initialState: PredictionPayload = {
  MedInc: 8.3252,
  HouseAge: 41,
  AveRooms: 6.9841,
  AveBedrms: 1.0238,
  Population: 322,
  AveOccup: 2.5556,
  Latitude: 37.88,
  Longitude: -122.23,
  cost_credits: 10,
};

export function PredictionForm({ onSubmit, isSubmitting }: PredictionFormProps) {
  const [form, setForm] = useState<PredictionPayload>(initialState);

  function updateField<K extends keyof PredictionPayload>(field: K, value: number) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit(form);
  }

  return (
    <form className="panel form-grid" onSubmit={handleSubmit}>
      {Object.entries(form).map(([key, value]) => (
        <label key={key} className="field">
          <span>{key}</span>
          <input
            type="number"
            step="any"
            value={value}
            onChange={(event) => updateField(key as keyof PredictionPayload, Number(event.target.value))}
          />
        </label>
      ))}
      <button className="primary-button" type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Отправка..." : "Запустить предсказание"}
      </button>
    </form>
  );
}
