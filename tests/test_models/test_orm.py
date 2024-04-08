from datetime import datetime, timedelta
from types import NoneType

from bookkeeper.config import DSN_TEST
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from bookkeeper.repository.my_orm import create_tables, drop_tables, insert_values, \
    get_all, get_by_pk, delete_by_pk, delete_all, update_by_pk, get_day_expenses, \
    get_week_expenses, get_month_expenses, get_day_expenses_by_cat, \
    get_month_expenses_by_cat, get_category_pk_by_name
from bookkeeper.models.sqlalchemy_models import ExpenseTable, CategoryTable, BudgetTable

engine = create_engine(DSN_TEST, echo=False)
session_factory = sessionmaker(engine)


def test_create_table():
    assert drop_tables(engine) is None
    assert create_tables(engine) is None


def test_insert_values():
    drop_tables(engine)
    create_tables(engine)

    assert insert_values(CategoryTable, {"name": "cat1"}, session_factory) is None
    assert insert_values(CategoryTable, {"name": "cat2"}, session_factory) is None
    assert insert_values(CategoryTable,
                         {"name": "cat3",
                          "parent": 2
                          }, session_factory) is None

    expense_values = {
        "expense_date": datetime.strptime("2024-03-06 19:54", "%Y-%m-%d %H:%M"),
        "cat_id": 3,
        "amount": 1000,
        "comment": "comment1"
    }
    assert insert_values(ExpenseTable, expense_values, session_factory) is None
    expense_values = {
        "expense_date": datetime.now(),
        "cat_id": 2,
        "amount": 2000,
        "comment": "comment2"
    }
    assert insert_values(ExpenseTable, expense_values, session_factory) is None
    expense_values = {
        "expense_date": datetime.now() - timedelta(days=5),
        "cat_id": 2,
        "amount": 3000,
        "comment": "comment3"
    }
    assert insert_values(ExpenseTable, expense_values, session_factory) is None
    expense_values = {
        "expense_date": datetime.now() - timedelta(days=15),
        "cat_id": 3,
        "amount": 4000,
        "comment": "comment4"
    }
    assert insert_values(ExpenseTable, expense_values, session_factory) is None

    expense_values = {
        "expense_date": datetime.now(),
        "cat_id": 3,
        "amount": 4000,
        "comment": "comment5"
    }
    assert insert_values(ExpenseTable, expense_values, session_factory) is None

    assert insert_values(BudgetTable,
                         {
                             "period": "day",
                             "amount": 1000,
                             "budget": 1000
                         }, session_factory) is None

    assert insert_values(BudgetTable,
                         {
                             "period": "week",
                             "amount": 7000,
                             "budget": 7000
                         }, session_factory) is None


def test_get_all():
    date = datetime.strptime("2024-03-06 19:54", "%Y-%m-%d %H:%M")
    res = get_all(ExpenseTable, session_factory)
    assert len(res) == 5
    row = res[0]
    assert type(row) == ExpenseTable
    assert row.cat_id == 3
    assert row.amount == 1000
    assert row.comment == "comment1"
    assert row.expense_date == date
    assert row.id == 1

    budget = get_all(BudgetTable, session_factory)
    assert len(budget) == 2
    assert type(budget[0]) == BudgetTable
    assert budget[0].period == "day"
    assert budget[0].amount == 1000
    assert budget[0].budget == 1000

    categories = get_all(CategoryTable, session_factory)
    assert len(categories) == 3
    assert(type(categories[0])) == CategoryTable


def test_get_by_pk():
    date = datetime.strptime("2024-03-06 19:54", "%Y-%m-%d %H:%M")
    row = get_by_pk(ExpenseTable, 1, session_factory)
    assert type(row) == ExpenseTable
    assert row.cat_id == 3
    assert row.amount == 1000
    assert row.comment == "comment1"
    assert row.expense_date == date
    assert row.id == 1

    budget = get_by_pk(BudgetTable, 1, session_factory)
    assert budget.period == "day"
    assert budget.amount == 1000
    assert budget.budget == 1000

    cat = get_by_pk(CategoryTable, 1, session_factory)
    assert cat.name == "cat1"
    assert cat.parent is None


def test_update_by_pk():
    new_date = datetime.strptime("2024-06-10 20:54", "%Y-%m-%d %H:%M")
    update_values = {
        "cat_id": 1,
        "amount": 2000,
        "comment": "new_comment",
        "expense_date": new_date
    }
    update_by_pk(ExpenseTable, 1, update_values, session_factory)
    res = get_by_pk(ExpenseTable, 1, session_factory)

    assert res.cat_id == 1
    assert res.amount == 2000
    assert res.comment == "new_comment"
    assert res.expense_date == new_date

    update_budget = {
        "amount": 2000,
        "budget": 3000,
    }
    update_by_pk(BudgetTable, 1, update_budget, session_factory)
    budget = get_by_pk(BudgetTable, 1, session_factory)

    assert budget.amount == 2000
    assert budget.budget == 3000


def test_get_day_expenses():
    res = get_day_expenses(session_factory)
    assert res == 6000


def test_get_week_expenses():
    res = get_week_expenses(session_factory)

    assert res == 9000


def test_get_month_expenses():
    res = get_month_expenses(session_factory)

    assert res == 13000


def test_get_day_expenses_by_cat():
    res = get_day_expenses_by_cat(session_factory)
    assert type(res) == list
    assert len(res) == 2

    assert res[0][0] == 'cat2'
    assert res[1][0] == 'cat3'

    assert res[0][1] == 2000
    assert res[1][1] == 4000


def test_get_month_expenses_by_cat():
    res = get_month_expenses_by_cat(session_factory)
    assert type(res) == list
    assert len(res) == 2

    assert res[0][0] == 'cat2'
    assert res[1][0] == 'cat3'

    assert res[0][1] == 5000
    assert res[1][1] == 8000


def test_get_category_pk_by_name():
    res = get_category_pk_by_name("cat1", session_factory)
    assert res == 1


def test_delete_by_pk():
    delete_by_pk(ExpenseTable, 1, session_factory)
    res = get_by_pk(ExpenseTable, 1, session_factory)
    assert type(res) is NoneType


def test_delete_all():
    delete_all(ExpenseTable, session_factory)
    delete_all(CategoryTable, session_factory)
    delete_all(BudgetTable, session_factory)

    res = get_all(ExpenseTable, session_factory)
    assert type(res) is list
    assert len(res) == 0

    res = get_all(BudgetTable, session_factory)
    assert type(res) is list
    assert len(res) == 0

    res = get_all(CategoryTable, session_factory)
    assert type(res) is list
    assert len(res) == 0
