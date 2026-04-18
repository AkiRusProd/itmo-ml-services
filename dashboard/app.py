from __future__ import annotations

import os
from datetime import datetime, timezone

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text


st.set_page_config(
    page_title="Apartment Price Analytics",
    page_icon="house",
    layout="wide",
)

st.markdown(
    """
    <style>
      .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
      }
      .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 55%, #38bdf8 100%);
        color: white;
        padding: 1.25rem 1.5rem;
        border-radius: 18px;
        margin-bottom: 1.5rem;
        box-shadow: 0 14px 40px rgba(15, 23, 42, 0.18);
      }
      .hero h1 {
        margin: 0;
        font-size: 2rem;
      }
      .hero p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.92;
      }
      .metric-note {
        color: #475569;
        font-size: 0.9rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")


@st.cache_resource
def get_engine():
    connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    return create_engine(DATABASE_URL, future=True, connect_args=connect_args)


@st.cache_data(ttl=15)
def load_summary():
    engine = get_engine()
    with engine.begin() as connection:
        users_count = connection.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
        predictions_count = connection.execute(
            text("SELECT COUNT(*) FROM prediction_requests")
        ).scalar() or 0
        completed_predictions = connection.execute(
            text("SELECT COUNT(*) FROM prediction_requests WHERE status = 'completed'")
        ).scalar() or 0
        failed_predictions = connection.execute(
            text("SELECT COUNT(*) FROM prediction_requests WHERE status = 'failed'")
        ).scalar() or 0
        credits_charged = connection.execute(
            text(
                "SELECT COALESCE(ABS(SUM(amount)), 0) "
                "FROM transactions WHERE transaction_type = 'prediction_charge'"
            )
        ).scalar() or 0
        promo_credits = connection.execute(
            text(
                "SELECT COALESCE(SUM(amount), 0) "
                "FROM transactions WHERE transaction_type = 'promo_code'"
            )
        ).scalar() or 0
        topup_credits = connection.execute(
            text(
                "SELECT COALESCE(SUM(amount), 0) "
                "FROM transactions WHERE transaction_type = 'top_up'"
            )
        ).scalar() or 0
    return {
        "users_count": users_count,
        "predictions_count": predictions_count,
        "completed_predictions": completed_predictions,
        "failed_predictions": failed_predictions,
        "credits_charged": credits_charged,
        "promo_credits": promo_credits,
        "topup_credits": topup_credits,
    }


@st.cache_data(ttl=15)
def load_predictions_by_day() -> pd.DataFrame:
    query = text(
        """
        SELECT DATE(created_at) AS day, COUNT(*) AS predictions
        FROM prediction_requests
        GROUP BY DATE(created_at)
        ORDER BY day
        """
    )
    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=15)
def load_credits_by_day() -> pd.DataFrame:
    query = text(
        """
        SELECT DATE(created_at) AS day,
               SUM(CASE WHEN transaction_type = 'prediction_charge' THEN ABS(amount) ELSE 0 END) AS charged_credits,
               SUM(CASE WHEN transaction_type IN ('top_up', 'promo_code', 'bonus') THEN amount ELSE 0 END) AS added_credits
        FROM transactions
        GROUP BY DATE(created_at)
        ORDER BY day
        """
    )
    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=15)
def load_prediction_statuses() -> pd.DataFrame:
    query = text(
        """
        SELECT status, COUNT(*) AS total
        FROM prediction_requests
        GROUP BY status
        ORDER BY total DESC
        """
    )
    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=15)
def load_recent_predictions() -> pd.DataFrame:
    query = text(
        """
        SELECT pr.id,
               pr.status,
               pr.cost_credits,
               pr.task_id,
               pr.created_at,
               res.prediction_value,
               res.model_name
        FROM prediction_requests pr
        LEFT JOIN prediction_results res
          ON res.prediction_request_id = pr.id
        ORDER BY pr.created_at DESC
        LIMIT 10
        """
    )
    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=15)
def load_recent_transactions() -> pd.DataFrame:
    query = text(
        """
        SELECT t.id,
               t.transaction_type,
               t.amount,
               t.description,
               t.created_at,
               w.user_id
        FROM transactions t
        JOIN wallets w
          ON w.id = t.wallet_id
        ORDER BY t.created_at DESC, t.id DESC
        LIMIT 10
        """
    )
    return pd.read_sql(query, get_engine())


st.markdown(
    f"""
    <div class="hero">
      <h1>Apartment Price Service Analytics</h1>
      <p>Операционная сводка по пользователям, предсказаниям и внутренним кредитам.
      Последнее обновление: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

refresh_col, note_col = st.columns([1, 4])
with refresh_col:
    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with note_col:
    st.markdown(
        "<p class='metric-note'>Дашборд читает данные напрямую из основной базы сервиса.</p>",
        unsafe_allow_html=True,
    )

try:
    summary = load_summary()
    predictions_by_day = load_predictions_by_day()
    credits_by_day = load_credits_by_day()
    statuses = load_prediction_statuses()
    recent_predictions = load_recent_predictions()
    recent_transactions = load_recent_transactions()
except Exception as exc:
    st.error(f"Dashboard failed to load data from the database: {exc}")
    st.stop()

metric_cols = st.columns(5)
metric_cols[0].metric("Users", summary["users_count"])
metric_cols[1].metric("Predictions", summary["predictions_count"])
metric_cols[2].metric("Completed", summary["completed_predictions"])
metric_cols[3].metric("Failed", summary["failed_predictions"])
metric_cols[4].metric("Credits Charged", int(summary["credits_charged"]))

metric_cols_bottom = st.columns(3)
metric_cols_bottom[0].metric("Top-up Credits", int(summary["topup_credits"]))
metric_cols_bottom[1].metric("Promo Credits", int(summary["promo_credits"]))
success_rate = (
    (summary["completed_predictions"] / summary["predictions_count"]) * 100
    if summary["predictions_count"]
    else 0
)
metric_cols_bottom[2].metric("Success Rate", f"{success_rate:.1f}%")

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Predictions by Day")
    if predictions_by_day.empty:
        st.info("No prediction data yet.")
    else:
        predictions_chart = predictions_by_day.set_index("day")
        st.line_chart(predictions_chart)

    st.subheader("Recent Predictions")
    if recent_predictions.empty:
        st.info("No prediction requests yet.")
    else:
        st.dataframe(recent_predictions, use_container_width=True, hide_index=True)

with right_col:
    st.subheader("Credits Flow by Day")
    if credits_by_day.empty:
        st.info("No transaction data yet.")
    else:
        credits_chart = credits_by_day.set_index("day")
        st.bar_chart(credits_chart)

    st.subheader("Prediction Status Distribution")
    if statuses.empty:
        st.info("No status data yet.")
    else:
        st.dataframe(statuses, use_container_width=True, hide_index=True)

st.subheader("Recent Transactions")
if recent_transactions.empty:
    st.info("No wallet transactions yet.")
else:
    st.dataframe(recent_transactions, use_container_width=True, hide_index=True)
