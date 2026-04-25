import type { PredictionDetail, PredictionListItem } from "../../types/prediction";
import { StatusBadge } from "../ui/StatusBadge";

type PredictionTableProps = {
  items: PredictionListItem[];
  selectedPrediction: PredictionDetail | null;
  onSelect: (id: number) => Promise<void>;
};

export function PredictionTable({
  items,
  selectedPrediction,
  onSelect,
}: PredictionTableProps) {
  return (
    <div className="grid-two">
      <section className="panel">
        <div className="panel-header">
          <h2>История предсказаний</h2>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Статус</th>
                <th>Кредиты</th>
                <th>Результат</th>
                <th>Действие</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td>{item.id}</td>
                  <td>
                    <StatusBadge status={item.status} />
                  </td>
                  <td>{item.cost_credits}</td>
                  <td>{item.prediction ?? "..."}</td>
                  <td>
                    <button className="ghost-button" onClick={() => void onSelect(item.id)} type="button">
                      Открыть
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <h2>Детали запроса</h2>
        </div>
        {selectedPrediction ? (
          <div className="detail-stack">
            <div className="detail-row">
              <span>Статус</span>
              <StatusBadge status={selectedPrediction.status} />
            </div>
            <div className="detail-row">
              <span>Модель</span>
              <strong>{selectedPrediction.model_name ?? "n/a"}</strong>
            </div>
            <div className="detail-row">
              <span>Версия</span>
              <strong>{selectedPrediction.model_version ?? "n/a"}</strong>
            </div>
            <div className="detail-row">
              <span>Результат</span>
              <strong>{selectedPrediction.prediction ?? "ожидание"}</strong>
            </div>
            <pre className="payload-box">
              {JSON.stringify(selectedPrediction.input_payload, null, 2)}
            </pre>
          </div>
        ) : (
          <div className="empty-state">Выбери предсказание из списка, чтобы увидеть детали.</div>
        )}
      </section>
    </div>
  );
}
