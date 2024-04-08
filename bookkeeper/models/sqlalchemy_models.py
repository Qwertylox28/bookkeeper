"""
Модуль описывающий модели SQLAlchemy
"""
# pylint: disable=too-few-public-methods
# pylint: disable=unnecessary-pass
# pylint: disable=not-callable

from datetime import datetime
from typing import Annotated, TypeVar

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import func, ForeignKey

pk = Annotated[int, mapped_column(primary_key=True)]
CreatedAt = Annotated[datetime, mapped_column(server_default=func.now())]
UpdatedAt = Annotated[datetime, mapped_column(onupdate=func.now(),
                                              server_default=func.now())]
Str200 = Annotated[str, 200]
Str50 = Annotated[str, 50]
Basetype = TypeVar('Basetype', bound='Base')


class Base(DeclarativeBase):
    """
    Базовый класс для моделей. Необходимо реализовать для моделей SQLAlchemy
    """
    pass


class CategoryTable(Base):
    """
    Модель категорий расходов
    Attributes:
    -----------
    id: pk
        Primary Key
    name: Str50
        Название категории
    parent: Union[int, None]
        Primary Key родительской категории, если нет родительской, то None
    """
    __tablename__ = "category_table"

    id: Mapped[pk]
    name: Mapped[Str50]
    parent: Mapped[int] = mapped_column(nullable=True)


class ExpenseTable(Base):
    """
    Модель расходов
    Attributes:
    ----------
    id: pk
        Primary Key
    expanse_date: datetime.datetime
        Дата покупки
    cat_id: int
        Primary Key таблицы категории расходов
    amount: float
        Сумма покупки
    added_at: UpdatedAt
        Дата добавления строки в БД
    updated_at: CreatedAt
        Дата обновления строки в БД
    """
    __tablename__ = "expense_table"

    id: Mapped[pk]
    expense_date: Mapped[datetime]
    cat_id: Mapped[int] = mapped_column(
        ForeignKey("category_table.id", ondelete="CASCADE")
    )

    amount: Mapped[float]
    comment: Mapped[Str200]
    added_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]


class BudgetTable(Base):
    """
    Модель бюджета. Содержит лимиты расходов за определённый период
    Attributes:
    ----------
    id: pk
        Primary Key
    period: Str50
        Период
    amount: float
        Лимит расходов за период
    """

    __tablename__ = "budget"

    id: Mapped[pk]
    period: Mapped[Str50]
    budget: Mapped[float]
    amount: Mapped[float]
