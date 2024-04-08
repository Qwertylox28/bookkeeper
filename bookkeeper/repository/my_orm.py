"""
Модуль описывающий взаимодействие с БД
"""
from __future__ import annotations
from datetime import datetime, time, timedelta
from typing import Union, Sequence, Any, Optional, Mapping

from sqlalchemy import select, delete, update, insert
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.row import Row
from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept

from bookkeeper.models.sqlalchemy_models import CategoryTable, ExpenseTable,\
    Basetype, Base


def create_tables(engine: Engine) -> None:
    """
    Создать таблицы в базе данных
    Parameters:
    -----------
    engine: Engine
        Движок для работы с БД через sqlalchemy

    Returns:
    --------
        None
    """
    Base.metadata.create_all(engine)


def drop_tables(engine: Engine) -> None:
    """
    Удалить таблицы в базе данных
    Parameters:
    -----------
    engine: Engine
        Движок для работы с БД через sqlalchemy

    Returns:
    --------
        None
    """
    Base.metadata.drop_all(engine)


def delete_all(model_class: DeclarativeAttributeIntercept,
               session_factory:  sessionmaker[Session]) -> None:
    """
    Удалить все строчки в таблице
    Parameters:
    -----------
    model_class: DeclarativeAttributeIntercept
        Модель таблицы
    session_factory: sessionmaker[Session]
        Фабрика генерирующая сессию для подключения к БД через sqlalchemy

    Returns:
    --------
        None
    """
    with session_factory() as session:
        query = delete(model_class)
        session.execute(query)
        session.commit()


def get_by_pk(model_class: DeclarativeAttributeIntercept,
              pk: int,
              session_factory: sessionmaker[Session]
              ) -> Optional[DeclarativeAttributeIntercept]:
    """
    Получить запись из таблицы model_class по primary key (pk)
    Attributes:
    -----------
    model_class:  DeclarativeAttributeIntercept
        Модель таблицы
    pk: int
        id записи
    session_factory:  sessionmaker[Session]
        Фабрика генерирующая сессию для подключения к БД через sqlalchemy

    Returns:
    --------
        Optional[DeclarativeAttributeIntercept]:
    """
    with session_factory() as session:
        res = session.get(model_class, pk)
    return res


def get_all(model_class: DeclarativeAttributeIntercept,
            session_factory: sessionmaker[Session]) -> list[Basetype]:
    """
    Получить список всех записей в таблице model_class
    Parameters:
    -----------
    model_class: DeclarativeAttributeIntercept
        Модель таблицы
    session_factory: sessionmaker[Session]
        Фабрика генерирующая сессию для подключения к БД через sqlalchemy

    Returns:
    --------
        list[Basetype]
    """
    with session_factory() as session:
        query = select(model_class)
        res = session.execute(query).all()
    result = [row[0] for row in res]
    return result


def delete_by_pk(model_class: DeclarativeAttributeIntercept,
                 pk: int,
                 session_factory: sessionmaker[Session]) -> None:
    """
    Удалить запись в таблице model_class по Primary Key (pk)
    Attributes:
    -----------
    model_class:  DeclarativeAttributeIntercept
        Модель таблицы
    pk: int
        id записи
    session_factory:  sessionmaker[Session]
        Фабрика генерирующая сессию для подключения к БД через sqlalchemy

    Returns:
    --------
        None
    """
    with session_factory() as session:
        query = delete(model_class).where(model_class.id == pk)
        session.execute(query)
        session.commit()


def update_by_pk(model_class: DeclarativeAttributeIntercept,
                 pk: int,
                 new_values: Mapping[str, Union[float, int, str, None]],
                 session_factory: sessionmaker[Session]) -> None:
    """
    Обновить запись(new_values) в таблице model_class по Primary Key (pk)
    Attributes:
    -----------
    model_class:  DeclarativeAttributeIntercept
        Модель таблицы
    pk: int
        id записи
    new_values: Mapping[str, Union[float, int, str, None]]
        словарь содержащий новые значения.
            key - названия полей таблицы, которые нужно обновить
            values - новые значения
    session_factory:  sessionmaker[Session]
        Фабрика генерирующая сессию для подключения к БД через sqlalchemy

    Returns:
    --------
        None
    """
    with session_factory() as session:
        query = update(model_class).where(model_class.id == pk).values(**new_values)
        session.execute(query)
        session.commit()


def insert_values(model_class: DeclarativeAttributeIntercept,
                  values: dict[str, Any],
                  session_factory: sessionmaker[Session]) -> None:
    """
    Вставить новую запись (values) в таблицу model_class
    Attributes:
    -----------
    model_class: DeclarativeAttributeIntercept
        Модель таблицы
    values: dict[str, Any]
        Словарь, содержащий значения
            key - название поля таблицы
            value - значение
    session_factory:  sessionmaker[Session]
        Фабрика генерирующая сессию для подключения к БД через sqlalchemy

    Returns:
    --------
        None
    """
    with session_factory() as session:
        query = insert(model_class).values(**values)
        session.execute(query)
        session.commit()


def get_day_expenses(session_factory: sessionmaker[Session]) -> Union[int, float]:
    """
    Получить сумму расходов за текущий день
    Attributes:
    -----------
    session_factory:  sessionmaker[Session]
        Фабрика генерирующая сессию для подключения к БД через sqlalchemy

    Returns:
    --------
        Union[int, float]
    """
    start_of_day = datetime.combine(datetime.now(), time.min)
    end_of_day = datetime.combine(datetime.now(), time.max)
    with session_factory() as session:
        query = (select(func.sum(ExpenseTable.amount).label("day_expenses"))
                 .filter(ExpenseTable.expense_date.between(start_of_day, end_of_day)))
        res: Union[int, float] = session.execute(query).scalar()
        if res is None:
            res = 0
    return res


def get_week_expenses(session_factory: sessionmaker[Session]) -> Union[int, float]:
    """
    Получить сумму расходов за последнюю неделю
    Attributes:
    -----------
    session_factory:  sessionmaker[Session]
        Фабрика генерирующая сессию для подключения к БД через sqlalchemy

    Returns:
    --------
        Union[int, float]
    """
    now = datetime.now()
    end = now
    start = end - timedelta(days=7)
    with session_factory() as session:
        query = (select(func.sum(ExpenseTable.amount).label("week_expenses"))
                 .filter(ExpenseTable.expense_date.between(start, end)))
        res: Union[int, float] = session.execute(query).scalar()
        if res is None:
            res = 0
    return res


def get_month_expenses(session_factory: sessionmaker[Session]) -> Union[int, float]:
    """
    Получить сумму расходов за последний месяц
    Attributes:
    -----------
    session_factory:  sessionmaker[Session]
        Фабрика генерирующая сессию для подключения к БД через sqlalchemy

    Returns:
    --------
        Union[int, float]
    """
    end = datetime.now()
    start = end - timedelta(days=30)
    with session_factory() as session:
        query = (select(func.sum(ExpenseTable.amount).label("month_expenses"))
                 .filter(ExpenseTable.expense_date.between(start, end)))
        res: Union[int, float] = session.execute(query).scalar()
        if res is None:
            res = 0
    return res


def get_expenses_data(session_factory: sessionmaker[Session]) -> Sequence[Row[Any]]:
    """
    Получить данные из БД для отображения в приложении
    Attributes:
    -----------
    session_factory:  sessionmaker[Session]
        Фабрика генерирующая сессию для подключения к БД через sqlalchemy

    Returns:
    --------
        Sequence[Row[Any]]
    """
    with session_factory() as session:
        query = select(ExpenseTable.id, ExpenseTable.expense_date, ExpenseTable.amount,
                       CategoryTable.name, ExpenseTable.comment).join(CategoryTable)
        res: Sequence[Row[Any]] = session.execute(query).all()
    return res


def get_day_expenses_by_cat(session_factory: sessionmaker[Session]
                            ) -> Sequence[Row[Any]]:
    """
    Получить расходы по категориям за текущий день
    Attributes:
    -----------
    session_factory:  sessionmaker[Session]
        Фабрика генерирующая сессию для подключения к БД через sqlalchemy

    Returns:
    --------
        Sequence[Row[Any]]
    """

    start = datetime.combine(datetime.now(), time.min)
    end = datetime.combine(datetime.now(), time.max)

    with session_factory() as session:
        query = (select(CategoryTable.name, func.sum(ExpenseTable.amount))
                 .join(CategoryTable)
                 .where(ExpenseTable.expense_date.between(start, end))
                 .group_by(CategoryTable.name))
        res: Sequence[Row[Any]] = session.execute(query).all()
    return res


def get_month_expenses_by_cat(session_factory: sessionmaker[Session]
                              ) -> Sequence[Row[Any]]:
    """
    Получить расходы по категориям за текущий месяц
    Attributes:
    -----------
    session_factory:  sessionmaker[Session]
        Фабрика генерирующая сессию для подключения к БД через sqlalchemy

    Returns:
    --------
        Sequence[Row[Any]]
    """
    end = datetime.now()
    start = end - timedelta(days=30)

    with session_factory() as session:
        query = (select(CategoryTable.name, func.sum(ExpenseTable.amount))
                 .join(CategoryTable)
                 .where(ExpenseTable.expense_date.between(start, end))
                 .group_by(CategoryTable.name))
        res: Sequence[Row[Any]] = session.execute(query).all()

    return res


def get_category_pk_by_name(name: str, session_factory: sessionmaker[Session]) -> int:
    """
    Получить id категории по её названию
    Attributes:
    -----------
    name: str
        Название категории
    session_factory:  sessionmaker[Session]
        Фабрика генерирующая сессию для подключения к БД через sqlalchemy

    Returns:
    --------
        int
    """
    with session_factory() as session:
        query = select(CategoryTable.id).where(CategoryTable.name == name)
        res: Row[Any] = session.execute(query).first()
    result_pk: int = res[0]
    return result_pk
