import { Navigate, createBrowserRouter } from "react-router-dom";

import { AppLayout } from "../components/layout/AppLayout";
import { ProtectedRoute } from "../components/layout/ProtectedRoute";
import { AdminModelPage } from "../pages/AdminModelPage";
import { AdminPromoCodesPage } from "../pages/AdminPromoCodesPage";
import { DashboardPage } from "../pages/DashboardPage";
import { LoginPage } from "../pages/LoginPage";
import { PredictPage } from "../pages/PredictPage";
import { PredictionsPage } from "../pages/PredictionsPage";
import { PromoPage } from "../pages/PromoPage";
import { RegisterPage } from "../pages/RegisterPage";
import { WalletPage } from "../pages/WalletPage";

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/register",
    element: <RegisterPage />,
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { index: true, element: <Navigate to="/dashboard" replace /> },
          { path: "/dashboard", element: <DashboardPage /> },
          { path: "/predict", element: <PredictPage /> },
          { path: "/predictions", element: <PredictionsPage /> },
          { path: "/wallet", element: <WalletPage /> },
          { path: "/promo", element: <PromoPage /> },
        ],
      },
    ],
  },
  {
    element: <ProtectedRoute requireAdmin />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: "/admin/promo-codes", element: <AdminPromoCodesPage /> },
          { path: "/admin/model", element: <AdminModelPage /> },
        ],
      },
    ],
  },
]);
