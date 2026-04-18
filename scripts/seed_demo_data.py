#!/usr/bin/env python3
from __future__ import annotations

from sqlalchemy import select

from app.db.session import SessionLocal, init_db
from app.models.promo_code import PromoCode
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.schemas.promo_code import PromoCodeCreateRequest
from app.services.auth_service import AuthService
from app.services.promo_code_service import PromoCodeService


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        auth_service = AuthService(db)
        promo_service = PromoCodeService(db)

        admin = db.execute(
            select(User).where(User.email == "admin@example.com")
        ).scalar_one_or_none()
        if admin is None:
            admin = auth_service.register_user(
                RegisterRequest(
                    email="admin@example.com",
                    password="strongpass123",
                    full_name="Demo Admin",
                )
            )
            admin.role = "admin"
            db.commit()
            db.refresh(admin)

        promo = db.execute(
            select(PromoCode).where(PromoCode.code == "WELCOME50")
        ).scalar_one_or_none()
        if promo is None:
            promo = promo_service.create_promo_code(
                PromoCodeCreateRequest(
                    code="WELCOME50",
                    credit_amount=50,
                    max_activations=100,
                )
            )

        print("Demo data seeded successfully.")
        print("Admin email: admin@example.com")
        print("Admin password: strongpass123")
        print(f"Promo code: {promo.code}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
