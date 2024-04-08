"""
Модуль точки входа. Запускает приложение
"""
# pylint: disable = no-name-in-module

import sys
import os

from PySide6.QtWidgets import QApplication
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bookkeeper.models.sqlalchemy_models import BudgetTable
from bookkeeper.presenter import Presenter
from bookkeeper.config import DSN
from bookkeeper.repository.my_orm import create_tables, insert_values

if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = create_engine(DSN)
    session_factory = sessionmaker(engine)
    if not os.path.exists("sqlalchemy_db.db"):
        create_tables(engine)
        insert_values(BudgetTable, {
            "period": "day",
            "amount": 0,
            "budget": 0
        }, session_factory)
        insert_values(BudgetTable, {
            "period": "week",
            "amount": 0,
            "budget": 0
        }, session_factory)
        insert_values(BudgetTable, {
            "period": "month",
            "amount": 0,
            "budget": 0
        }, session_factory)
    presenter: Presenter = Presenter(session_factory)
    presenter.main_window.show()
    app.exec()
else:
    pass
