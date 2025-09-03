from __future__ import annotations
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from . import models, schemas
from sqlalchemy import select, or_, func

def list_customers(
    db: Session,
    query: Optional[str] = None,
    phone: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[List[models.Customer], int]:
    # Build a reusable filtered SELECT (no limit/offset yet)
    base = select(models.Customer)

    if query:
        q = f"%{query.strip().lower()}%"
        base = base.where(
            or_(
                func.lower(models.Customer.full_name).like(q),
                func.lower(models.Customer.email).like(q),
            )
        )

    if phone:
        p = f"%{phone.strip()}%"
        base = base.where(models.Customer.phone.ilike(p))

    # 1) TOTAL via COUNT(*) over the filtered subquery
    count_stmt = select(func.count()).select_from(base.subquery())
    total = db.scalar(count_stmt) or 0

    # 2) PAGE via LIMIT/OFFSET (add deterministic ordering)
    items_stmt = base.order_by(models.Customer.id).limit(limit).offset(offset)
    items = db.execute(items_stmt).scalars().all()

    return items, total


def create_customer(db: Session, data: schemas.CustomerCreate) -> models.Customers:
    obj = models.Customer(
        full_name = data.full_name.strip(),
        email=str(data.email).lower(),
        phone=(data.phone.strip() if data.phone else None),
        address=(data.address.strip() if data.address else None),
        )
    
    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj


def get_customer(db:Session, customer_id: int) -> Optional[models.Customer]:
    return db.get(models.Customer, customer_id)

def get_by_email(db: Session, email: str)  -> Optional[models.Customer]:
    stmt = select(models.Customer).where(models.Customer.email == email.lower())
    return db.execute(stmt).scalars().first()

def get_by_phone(db: Session, phone: str) -> Optional[models.Customer]:
    stmt = select(models.Customer).where(models.Customer.phone == phone)
    return db.execute(stmt).scalars().first()


def update_customer(db: Session, customer: models.Customer, data: schemas.CustomerUpdate) -> models.Customer:
     if data.full_name is not None:
          customer.full_name = data.full_name.strip()
     if data.email is not None:
          customer.email = str(data.email).lower()
     if data.phone is not None:
          customer.phone = data.phone.strip()
     if data.address is not None:
          customer.address = data.address.strip()

     db.add(customer)
     db.commit()
     db.refresh(customer)
     return customer
    