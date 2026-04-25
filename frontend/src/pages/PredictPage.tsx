import { useState } from "react";

import { createPrediction } from "../api/predictions";
import { PredictionForm } from "../components/prediction/PredictionForm";
import type { PredictionCreateResponse, PredictionPayload } from "../types/prediction";

export function PredictPage() {
  const [result, setResult] = useState<PredictionCreateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(payload: PredictionPayload) {
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await createPrediction(payload);
      setResult(response);
    } catch {
      setError("Не удалось создать prediction request. Проверь баланс и авторизацию.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="page-stack">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Prediction</p>
          <h2>Запуск нового предсказания</h2>
        </div>
      </section>
      <PredictionForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
      {error ? <div className="error-banner">{error}</div> : null}
      {result ? (
        <section className="panel">
          <div className="panel-header">
            <h2>Ответ API</h2>
          </div>
          <pre className="payload-box">{JSON.stringify(result, null, 2)}</pre>
        </section>
      ) : null}
    </div>
  );
}
