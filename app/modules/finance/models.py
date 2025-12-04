from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, DateTime, Numeric


class TransactionBase(SQLModel):
    amount: float = Field(sa_column=Column(Numeric(12, 2)))
    type: str = Field(index=True, description="INCOME or EXPENSE")
    category: str = Field(index=True)
    description: Optional[str] = None
    transaction_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class Transaction(TransactionBase, table=True):
    __tablename__ = "transactions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID = Field(foreign_key="business_profiles.id", index=True)
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class TransactionCreate(TransactionBase):
    pass


class TransactionRead(TransactionBase):
    id: UUID
    business_id: UUID
    created_at: datetime


class FinancialSummary(SQLModel):
    total_income: float
    total_expense: float
    net_profit: float
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
