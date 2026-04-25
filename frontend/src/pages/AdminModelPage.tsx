import { useEffect, useState } from "react";

import { fetchCurrentModel } from "../api/models";
import type { MLModel } from "../types/model";

export function AdminModelPage() {
  const [model, setModel] = useState<MLModel | null>(null);

  useEffect(() => {
    void fetchCurrentModel().then(setModel);
  }, []);

  return (
    <div className="page-stack">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Admin</p>
          <h2>Текущая модель</h2>
        </div>
      </section>
      <section className="panel">
        {model ? (
          <>
            <div className="detail-row">
              <span>Имя</span>
              <strong>{model.name}</strong>
            </div>
            <div className="detail-row">
              <span>Версия</span>
              <strong>{model.version}</strong>
            </div>
            <div className="detail-row">
              <span>Target</span>
              <strong>{model.target_name}</strong>
            </div>
            <div className="detail-row">
              <span>Артефакт</span>
              <strong>{model.artifact_path}</strong>
            </div>
            <div className="chip-row">
              {model.features.map((feature) => (
                <span className="chip" key={feature}>
                  {feature}
                </span>
              ))}
            </div>
          </>
        ) : (
          <div className="page-state">Загрузка метаданных модели...</div>
        )}
      </section>
    </div>
  );
}
