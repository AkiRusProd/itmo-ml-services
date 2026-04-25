import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";

const navigation = [
  { to: "/dashboard", label: "Сводка" },
  { to: "/predict", label: "Предсказание" },
  { to: "/predictions", label: "История" },
  { to: "/wallet", label: "Кошелек" },
  { to: "/promo", label: "Промокод" },
  { to: "/admin/promo-codes", label: "Админ: промокоды", adminOnly: true },
  { to: "/admin/model", label: "Админ: модель", adminOnly: true },
];

export function AppLayout() {
  const { logout, user } = useAuth();

  return (
    <div className="shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">Apartment Price Service</p>
          <h1>Операционная панель</h1>
          <p className="muted">
            Сервис предсказаний, биллинг на кредитах и контроль состояния модели в одном месте.
          </p>
        </div>

        <nav className="nav">
          {navigation
            .filter((item) => !item.adminOnly || user?.role === "admin")
            .map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
              >
                {item.label}
              </NavLink>
            ))}
        </nav>

        <div className="sidebar-card">
          <div>
            <div className="sidebar-label">Пользователь</div>
            <div className="sidebar-value">{user?.full_name}</div>
            <div className="muted">{user?.email}</div>
          </div>
          <button className="ghost-button" onClick={logout} type="button">
            Выйти
          </button>
        </div>
      </aside>

      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
