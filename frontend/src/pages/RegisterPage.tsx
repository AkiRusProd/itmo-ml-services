import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [fullName, setFullName] = useState("Rustam User");
  const [email, setEmail] = useState("user@example.com");
  const [password, setPassword] = useState("strongpass123");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await register({
        full_name: fullName,
        email,
        password,
      });
      navigate("/dashboard");
    } catch {
      setError("Регистрация не удалась. Возможно, пользователь уже существует.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="auth-shell">
      <section className="auth-card hero-card">
        <p className="eyebrow">JWT + Billing + Predictions</p>
        <h1>Создай аккаунт и начни тестировать сервис</h1>
        <p className="muted">
          После регистрации пользователь сразу получает welcome-бонус в кредитах.
        </p>
      </section>

      <form className="auth-card" onSubmit={handleSubmit}>
        <h2>Регистрация</h2>
        <label className="field">
          <span>Полное имя</span>
          <input value={fullName} onChange={(event) => setFullName(event.target.value)} type="text" />
        </label>
        <label className="field">
          <span>Email</span>
          <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" />
        </label>
        <label className="field">
          <span>Пароль</span>
          <input
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            type="password"
          />
        </label>
        {error ? <div className="error-banner">{error}</div> : null}
        <button className="primary-button" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Создаем..." : "Зарегистрироваться"}
        </button>
        <div className="muted">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </div>
      </form>
    </div>
  );
}
