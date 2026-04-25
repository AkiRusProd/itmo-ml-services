import { useEffect, useState } from "react";

import { fetchCurrentModel } from "../api/models";
import { fetchPredictions } from "../api/predictions";
import { fetchTransactions, fetchWallet } from "../api/wallet";
import { useAuth } from "../hooks/useAuth";
import type { MLModel } from "../types/model";
import type { PredictionListItem } from "../types/prediction";
import type { Transaction, Wallet } from "../types/wallet";
import { StatCard } from "../components/ui/StatCard";

export function DashboardPage() {
  const { user, refreshUser } = useAuth();
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [predictions, setPredictions] = useState<PredictionListItem[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [model, setModel] = useState<MLModel | null>(null);

  useEffect(() => {
    void refreshUser();
    void Promise.all([
      fetchWallet().then(setWallet),
      fetchPredictions().then(setPredictions),
      fetchTransactions().then(setTransactions),
      fetchCurrentModel().then(setModel),
    ]);
  }, [refreshUser]);

  return (
    <div className="page-stack">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Сводка</p>
          <h2>Текущая картина по аккаунту и модели</h2>
        </div>
      </section>

      <div className="stats-grid">
        <StatCard label="Баланс" value={`${wallet?.balance ?? user?.wallet_balance ?? 0} кр.`} />
        <StatCard label="Всего предсказаний" value={String(predictions.length)} />
        <StatCard
          label="Последняя модель"
          value={model ? `${model.name} ${model.version}` : "Загрузка"}
          hint={model?.target_name}
        />
        <StatCard
          label="Последняя транзакция"
          value={transactions[0] ? `${transactions[0].amount} кр.` : "Нет данных"}
          hint={transactions[0]?.transaction_type}
        />
      </div>

      <div className="grid-two">
        <section className="panel">
          <div className="panel-header">
            <h2>Последние предсказания</h2>
          </div>
          <div className="list-stack">
            {predictions.slice(0, 5).map((item) => (
              <article className="list-item" key={item.id}>
                <div>
                  <strong>Запрос #{item.id}</strong>
                  <div className="muted">{item.status}</div>
                </div>
                <div>{item.prediction ?? "..."}</div>
              </article>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>Последние транзакции</h2>
          </div>
          <div className="list-stack">
            {transactions.slice(0, 5).map((item) => (
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
