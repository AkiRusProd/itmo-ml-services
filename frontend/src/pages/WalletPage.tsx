import { useEffect, useState } from "react";

import { fetchTransactions, fetchWallet, topUpWallet } from "../api/wallet";
import type { Transaction, Wallet } from "../types/wallet";

export function WalletPage() {
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [amount, setAmount] = useState(25);
  const [message, setMessage] = useState<string | null>(null);

  async function reload() {
    const [walletResponse, transactionsResponse] = await Promise.all([
      fetchWallet(),
      fetchTransactions(),
    ]);
    setWallet(walletResponse);
    setTransactions(transactionsResponse);
  }

  useEffect(() => {
    void reload();
  }, []);

  async function handleTopUp(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const response = await topUpWallet({ amount });
    setMessage(`${response.message} Новый баланс: ${response.wallet_balance}`);
    await reload();
  }

  return (
    <div className="page-stack">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Wallet</p>
          <h2>Баланс и история операций</h2>
        </div>
      </section>

      <div className="grid-two">
        <section className="panel">
          <h2>Баланс</h2>
          <div className="big-number">{wallet?.balance ?? 0} кр.</div>
          <form className="inline-form" onSubmit={handleTopUp}>
            <input
              min={1}
              type="number"
              value={amount}
              onChange={(event) => setAmount(Number(event.target.value))}
            />
            <button className="primary-button" type="submit">
              Пополнить
            </button>
          </form>
          {message ? <div className="success-banner">{message}</div> : null}
        </section>

        <section className="panel">
          <h2>История транзакций</h2>
          <div className="list-stack">
            {transactions.map((item) => (
              <article className="list-item" key={item.id}>
                <div>
                  <strong>{item.transaction_type}</strong>
                  <div className="muted">{item.description ?? "Без описания"}</div>
                </div>
                <div>{item.amount} кр.</div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
