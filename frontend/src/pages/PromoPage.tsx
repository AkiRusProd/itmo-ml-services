import { useState } from "react";

import { redeemPromoCode } from "../api/promoCodes";

export function PromoPage() {
  const [code, setCode] = useState("WELCOME50");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);
    setError(null);

    try {
      const response = await redeemPromoCode({ code });
      setMessage(`${response.message}. Зачислено ${response.credited_amount} кр.`);
    } catch {
      setError("Не удалось активировать промокод.");
    }
  }

  return (
    <div className="page-stack">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Promo Codes</p>
          <h2>Активация промокодов</h2>
        </div>
      </section>
      <form className="panel compact-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Код</span>
          <input value={code} onChange={(event) => setCode(event.target.value)} type="text" />
        </label>
        <button className="primary-button" type="submit">
          Активировать
        </button>
        {message ? <div className="success-banner">{message}</div> : null}
        {error ? <div className="error-banner">{error}</div> : null}
      </form>
    </div>
  );
}
