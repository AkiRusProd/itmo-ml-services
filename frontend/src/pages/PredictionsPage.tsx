import { useEffect, useState } from "react";

import { fetchPrediction, fetchPredictions } from "../api/predictions";
import { PredictionTable } from "../components/prediction/PredictionTable";
import type { PredictionDetail, PredictionListItem } from "../types/prediction";

export function PredictionsPage() {
  const [items, setItems] = useState<PredictionListItem[]>([]);
  const [selectedPrediction, setSelectedPrediction] = useState<PredictionDetail | null>(null);

  useEffect(() => {
    void fetchPredictions().then(setItems);
  }, []);

  async function handleSelect(id: number) {
    const detail = await fetchPrediction(id);
    setSelectedPrediction(detail);
  }

  return (
    <div className="page-stack">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Prediction History</p>
          <h2>Очередь и результаты предсказаний</h2>
        </div>
      </section>
      <PredictionTable items={items} selectedPrediction={selectedPrediction} onSelect={handleSelect} />
    </div>
  );
}
