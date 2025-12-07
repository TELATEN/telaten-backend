from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, DateTime, Numeric


class TransactionCategoryBase(SQLModel):
    name: str = Field(index=True)
    type: str = Field(index=True, description="INCOME or EXPENSE")
    icon: Optional[str] = None


class TransactionCategory(TransactionCategoryBase, table=True):
    __tablename__ = "transaction_categories"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    business_id: Optional[UUID] = Field(
        default=None, foreign_key="business_profiles.id", index=True
    )  # Nullable for system default categories

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class TransactionCategoryRead(TransactionCategoryBase):
    id: UUID


class TransactionCategoryCreate(TransactionCategoryBase):
    pass


class TransactionBase(SQLModel):
    amount: float = Field(sa_column=Column(Numeric(12, 2)))
    type: str = Field(index=True, description="INCOME or EXPENSE")
    category_id: UUID = Field(foreign_key="transaction_categories.id")
    category_name: str = Field(index=True)

    payment_method: str = Field(
        default="CASH", index=True, description="CASH, TRANSFER, QRIS, ETC"
    )
    description: Optional[str] = None
    transaction_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class Transaction(TransactionBase, table=True):
    __tablename__ = "transactions"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID = Field(foreign_key="business_profiles.id", index=True)
    category: Optional["TransactionCategory"] = Relationship()

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class TransactionRead(TransactionBase):
    id: UUID
    business_id: UUID
    created_at: datetime


class TransactionPagination(SQLModel):
    items: list[TransactionRead]
    total: int
    page: int
    size: int
    pages: int


class TransactionCreate(SQLModel):
    amount: float
    type: str
    category_id: UUID
    category_name: str

    payment_method: str = "CASH"
    description: Optional[str] = None
    transaction_date: Optional[datetime] = None


class CategoryBreakdown(SQLModel):
    category: str
    amount: float
    percentage: float


class FinancialSummary(SQLModel):
    total_income: float
    total_expense: float
    net_profit: float
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    income_breakdown: list[CategoryBreakdown] = []
    expense_breakdown: list[CategoryBreakdown] = []
