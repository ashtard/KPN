from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import get_db

router = APIRouter(prefix="/customers", tags=["customers"])


# ---------- LIST / SEARCH ----------
@router.get("/", response_model=List[schemas.CustomerRead])
def list_customers(
    query: Optional[str] = Query(None, description="Case-insensitive search over name and email"),
    phone: Optional[str] = Query(None, description="Exact or partial phone match"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    response: Response = None,
    db: Session = Depends(get_db),
):
    items, total = crud.list_customers(db, query=query, phone=phone, limit=limit, offset=offset)

    # Pagination headers
    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Limit"] = str(limit)
    response.headers["X-Offset"] = str(offset)

    return items


# ---------- RETRIEVE ----------
@router.get(
    "/{customer_id}",
    response_model=schemas.CustomerRead,
    responses={404: {"model": schemas.Error}},
)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    obj = crud.get_customer(db, customer_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return obj


# ---------- CREATE ----------
@router.post(
    "/",
    response_model=schemas.CustomerRead,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": schemas.Error}},
)
def create_customer(payload: schemas.CustomerCreate, db: Session = Depends(get_db)):
    # Uniqueness checks
    if crud.get_by_email(db, str(payload.email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    if payload.phone and crud.get_by_phone(db, str(payload.phone)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already exists")

    return crud.create_customer(db, payload)


# ---------- UPDATE (partial) ----------
@router.patch(
    "/{customer_id}",
    response_model=schemas.CustomerRead,
    responses={
        404: {"model": schemas.Error},
        409: {"model": schemas.Error},
    },
)
def update_customer(customer_id: int, payload: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    obj = crud.get_customer(db, customer_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    # Collision checks (independent)
    if payload.email is not None:
        existing = crud.get_by_email(db, str(payload.email))
        if existing and existing.id != customer_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    if payload.phone is not None and payload.phone != "":
        existing = crud.get_by_phone(db, payload.phone)
        if existing and existing.id != customer_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone number already exists")

    return crud.update_customer(db, obj, payload)


# ---------- DELETE ----------
@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": schemas.Error}},
)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    obj = crud.get_customer(db, customer_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    crud.delete_customer(db, obj)
    return None
