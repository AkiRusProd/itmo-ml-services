import { useState } from "react";

import { createPromoCode } from "../api/promoCodes";

export function AdminPromoCodesPage() {
  const [code, setCode] = useState("SPRING100");
  const [creditAmount, setCreditAmount] = useState(100);
  const [maxActivations, setMaxActivations] = useState(10);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);
    setError(null);

    try {
      const response = await createPromoCode({
        code,
        credit_amount: creditAmount,
        max_activations: maxActivations,
        expires_at: null,
      });
      setMessage(`Промокод ${response.code} создан.`);
    } catch {
      setError("Не удалось создать промокод. Проверь роль admin.");
    }
  }

  return (
    <div className="page-stack">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Admin</p>
          <h2>Создание промокодов</h2>
        </div>
      </section>
      <form className="panel form-grid" onSubmit={handleSubmit}>
        <label className="field">
          <span>Код</span>
          <input value={code} onChange={(event) => setCode(event.target.value)} type="text" />
        </label>
        <label className="field">
          <span>Кредиты</span>
          <input
            type="number"
            value={creditAmount}
            onChange={(event) => setCreditAmount(Number(event.target.value))}
          />
        </label>
        <label className="field">
          <span>Макс. активаций</span>
          <input
            type="number"
            value={maxActivations}
            onChange={(event) => setMaxActivations(Number(event.target.value))}
          />
        </label>
        <button className="primary-button" type="submit">
          Создать
        </button>
        {message ? <div className="success-banner">{message}</div> : null}
        {error ? <div className="error-banner">{error}</div> : null}
      </form>
    </div>
  );
}
