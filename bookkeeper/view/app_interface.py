"""
Модуль GUI
"""
# pylint: disable = no-name-in-module
# # pylint: disable=c-extension-no-member
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
from typing import Any, Union, List, Sequence
from PySide6.QtCore import QAbstractTableModel, Qt, QSize
from PySide6.QtCore import QModelIndex, QPersistentModelIndex
from PySide6.QtWidgets import QMainWindow, QTableView, QPushButton
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLineEdit
from PySide6.QtWidgets import QHBoxLayout, QLabel, QFrame
from PySide6.QtWidgets import QTabWidget, QHeaderView, QTextEdit, QComboBox
from sqlalchemy import Row

from models.sqlalchemy_models import CategoryTable


class ExpenseTableModel(QAbstractTableModel):
    """
    Модель таблицы расходов.
    Позволяет редактировать данные в ячейке таблицы напрямую(как в Excel).
    Необходимо обязательно реализовать 4 родительских метода:
        data
        rowCount
        columnCount
        setData
    Взято из:
    https://www.pythonguis.com/faq/editing-pyqt-tableview/
    """

    def __init__(self, repo: list[list[str]]) -> None:
        super().__init__()
        self._data = repo
        self.columns = ["pk", "expense_date", "amount", "category", "comment"]

    def data(self, index: Union[QModelIndex, QPersistentModelIndex],
             role: int = Qt.ItemDataRole.DisplayRole) -> str | None:
        """
        Данные таблицы
        Родительский метод, который необходимо реализовать
        """
        if index.isValid():
            if role in [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]:
                value = self._data[index.row()][index.column()]
                return str(value)
        return None

    def rowCount(self, parent: Any = QModelIndex) -> int:
        """
        Кол-во строк
        Родительский метод, который необходимо реализовать
        """
        return len(self._data)

    def columnCount(self, parent: Any = QModelIndex) -> int:
        """
        Кол-во колонок
        Родительский метод, который необходимо реализовать
        """
        return len(self._data[0])

    def setData(self,
                index: Union[QModelIndex, QPersistentModelIndex],
                value: Any,
                role: int = 0
                ) -> bool:
        """
        Записывает данные в таблицу
        Родительский метод, который необходимо реализовать
        """
        if role == Qt.ItemDataRole.EditRole:
            self._data[index.row()][index.column()] = value

            return True
        return False

    def flags(self, index: Union[QModelIndex, QPersistentModelIndex]) -> Qt.ItemFlag:
        """
         Родительский метод, который необходимо реализовать чтобы,
         можно было редактировать таблицу напрямую(как в Excel)
        """
        return Qt.ItemFlag.ItemIsSelectable \
            | Qt.ItemFlag.ItemIsEnabled \
            | Qt.ItemFlag.ItemIsEditable

    def headerData(self, section: int,
                   orient: Qt.Orientation,
                   role: int = 0
                   ) -> str | None:
        """
        Устанавливает заголовки таблицы
        Родительский метод
        """
        if orient == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.columns[section]
        if orient == Qt.Orientation.Vertical and role == Qt.ItemDataRole.DisplayRole:
            return f"{section + 1}"
        return None


class ExpenseWidget(QWidget):
    """
    Описывает графический интерфейс вкоадки Expense
    expense_table - таблица расходов
    line_date - поле для ввода даты расхода
    line_amount - поле для ввода суммы расхода
    line category - выбрать категорию из выпадающего списка
    add_button - кнопка добавления расхода в БД и в таблицу
    page_expense_layout - слой, в котором собраны все вижджеты
    """

    def __init__(self) -> None:
        super().__init__()
        self.expense_table = QTableView()
        self.line_date = QLineEdit()
        self.line_amount = QLineEdit()
        self.line_amount.setPlaceholderText('Input amount example: 999.99')
        self.line_category = QComboBox()
        self.line_comment = QLineEdit()

        self.add_button = QPushButton("Add expense")
        label_date = QLabel("edit date")
        label_amount = QLabel("edit amount")
        label_category = QLabel("edit category")
        label_comment = QLabel("edit comment")

        self.page_expense_layout = QVBoxLayout()
        adding_layout = QVBoxLayout()
        adding_row_layout = QHBoxLayout()
        label_layout = QVBoxLayout()
        line_layout = QVBoxLayout()

        line_layout.addWidget(self.line_date)
        line_layout.addWidget(self.line_amount)
        line_layout.addWidget(self.line_category)
        line_layout.addWidget(self.line_comment)

        label_layout.addWidget(label_date)
        label_layout.addWidget(label_amount)
        label_layout.addWidget(label_category)
        label_layout.addWidget(label_comment)

        adding_row_layout.addLayout(label_layout)
        adding_row_layout.addLayout(line_layout)

        adding_layout.addLayout(adding_row_layout)
        adding_layout.addWidget(self.add_button)

        self.page_expense_layout.addWidget(self.expense_table)
        self.page_expense_layout.addLayout(adding_layout)

        self.line_date.setInputMask("00-00-0000 00:00")


class BudgetModel(QAbstractTableModel):
    """
    Модель таблицы бюджета.
    Данные не редактируются на прямую!
    Необходимо обязательно реализовать 4 родительских метода:
        data
        rowCount
        columnCount
        setData
    """

    def __init__(self, repo: list[list[float]]) -> None:
        super().__init__()
        self._data = repo
        self.columns = ["Budget", "Expenses", "Delta"]
        self.rows = ["day", "week", "month"]

    def rowCount(self, parent: Any = QModelIndex) -> int:
        """
        Кол-во строк
        Родительский метод, который необходимо реализовать
        """
        return len(self._data)

    def columnCount(self, parent: Any = QModelIndex) -> int:
        """
        Кол-во колонок
        Родительский метод, который необходимо реализовать
        """
        return len(self._data[0])

    def data(self, index: Union[QModelIndex, QPersistentModelIndex],
             role: int = Qt.ItemDataRole.DisplayRole) -> float | None:
        """
        Родительский метод, который необходимо реализовать
        """
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        return None

    def headerData(self,
                   section: int,
                   orient: Qt.Orientation,
                   role: int = 0
                   ) -> str | None:
        """
        Устанавливает заголовки таблицы
        Родительский метод
        """
        if orient == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.columns[section]
        if orient == Qt.Orientation.Vertical and role == Qt.ItemDataRole.DisplayRole:
            return self.rows[section]
        return None


class BudgetWidget(QWidget):
    """
    Описывает интерфейс вкладки Budget:
    table_budget - таблица бюджета
    table_cat_expenses - таблица расходов за период по категориям
    cat_day_expense_button - выставляет период == день в таблице расходов по категориям
    month_day_expense_button - выставляет период == месяц в таблице расходов по категориям
    line_day_budget - поле ввода бюджета на день
    line_week_budget - поле ввода бюджета за неделю
    line_month_budget - поле ввода бюджета за месяц
    change_button - кнопка устанавливающая бюджет на периоды: день,неделя,месяц
    page_budget_layout - слой, в котором собраны все виджеты
    """

    def __init__(self) -> None:
        super().__init__()
        self.table_budget = QTableView()
        self.table_cat_expenses = QTableView()

        self.page_budget_layout = QVBoxLayout()

        adding_layout = QHBoxLayout()
        line_layout = QVBoxLayout()
        label_layout = QVBoxLayout()
        cat_expense_buttons_layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()

        label_buttons = QLabel("Expenses by categories in the period:")
        self.cat_day_expense_button = QPushButton("day")
        self.cat_day_expense_button.setCheckable(True)
        self.cat_month_expense_button = QPushButton("month")
        self.cat_month_expense_button.setCheckable(True)

        self.line_day_budget = QLineEdit()
        self.line_week_budget = QLineEdit()
        self.line_month_budget = QLineEdit()

        label_day_budget = QLabel("set day budget")
        label_week_budget = QLabel("set week budget")
        label_month_budget = QLabel("set month budget")

        self.change_button = QPushButton("change budget")

        cat_expense_buttons_layout.addWidget(label_buttons)
        cat_expense_buttons_layout.addLayout(buttons_layout)

        buttons_layout.addWidget(self.cat_day_expense_button)
        buttons_layout.addWidget(self.cat_month_expense_button)

        self.page_budget_layout.addWidget(self.table_budget)
        self.page_budget_layout.addLayout(cat_expense_buttons_layout)
        self.page_budget_layout.addWidget(self.table_cat_expenses)
        self.page_budget_layout.addLayout(adding_layout)

        adding_layout.addLayout(label_layout)
        adding_layout.addLayout(line_layout)
        adding_layout.addWidget(self.change_button)

        adding_layout.setStretchFactor(label_layout, 1)
        adding_layout.setStretchFactor(line_layout, 2)
        adding_layout.setStretchFactor(self.change_button, 1)

        label_layout.addWidget(label_day_budget)
        label_layout.addWidget(label_week_budget)
        label_layout.addWidget(label_month_budget)

        line_layout.addWidget(self.line_day_budget)
        line_layout.addWidget(self.line_week_budget)
        line_layout.addWidget(self.line_month_budget)


class CatExpenseModel(QAbstractTableModel):
    """
    Модель таблицы расходов по категориям за некоторый период
    Данные не редактируются на прямую!
    Необходимо обязательно реализовать 4 родительских метода:
        data
        rowCount
        columnCount
        setData
    """

    def __init__(self, repo: Union[Sequence[Row[Any]], List[List[str]]]) -> None:
        super().__init__()
        self._data = repo
        self.columns = ["Categories", "Expenses"]

    def rowCount(self, parent: Any = QModelIndex) -> int:
        """
        Кол-во строк
        Родительский метод, который необходимо реализовать
        """
        return len(self._data)

    def columnCount(self, parent: Any = QModelIndex) -> int:
        """
        Кол-во колонок
        Родительский метод, который необходимо реализовать
        """
        return len(self._data[0])

    def data(self, index: Union[QModelIndex, QPersistentModelIndex],
             role: int = Qt.ItemDataRole.DisplayRole) -> Union[str, float] | None:
        """
        Родительский метод, который необходимо реализовать
        """
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        return None

    def headerData(self, section: int,
                   orient: Qt.Orientation,
                   role: int = 0
                   ) -> str | None:
        """
        Устанавливает заголовки таблицы
        Родительский метод
        """
        if orient == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.columns[section]
        if orient == Qt.Orientation.Vertical and role == Qt.ItemDataRole.DisplayRole:
            return f"{section + 1}"
        return None


class CategoryWidget(QWidget):
    """
    Описывает интерфейс листа Category
    """

    def __init__(self) -> None:
        super().__init__()
        self.page_category_layout = QVBoxLayout()

        self.text_box = QTextEdit()
        self.text_box.resize(500, 400)

        self.edit_button = QPushButton("commit change")

        self.page_category_layout.addWidget(self.text_box)
        self.page_category_layout.addWidget(self.edit_button)


class MainWindow(QMainWindow):
    """
    Интерфейс приложения
    Входные параметры:
        repo_expense - данные для таблицы Expenses
        repo_budget - данные для таблицы Budget
    Атрибуты:
        expense - вкладка Expense
        budget - вкладка Budget
        category - вкладка Category
    """

    def __init__(self, repo_expense: list[list[str]], repo_budget: list[list[float]],
                 ) -> None:
        super().__init__()

        if repo_budget is None:
            repo_budget = ['', '', '']
        self.setWindowTitle("bookkeeper App")
        self.setFixedSize(QSize(500, 600))

        self.expense = ExpenseWidget()
        expense_model = ExpenseTableModel(repo_expense)
        self.expense.expense_table.setModel(expense_model)

        page_expense = QFrame()
        page_expense.setLayout(self.expense.page_expense_layout)
        pages = QTabWidget()
        pages.addTab(page_expense, "Expenses")

        self.expense.expense_table.horizontalHeader(). \
            setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.expense.expense_table.horizontalHeader(). \
            setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.expense.expense_table.horizontalHeader(). \
            setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.expense.expense_table.horizontalHeader(). \
            setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.expense.expense_table.setColumnHidden(0, True)
        self.expense.expense_table.verticalHeader().setVisible(False)

        self.budget = BudgetWidget()
        budget_model = BudgetModel(repo_budget)
        self.budget.table_budget.setModel(budget_model)

        page_budget = QFrame()
        page_budget.setLayout(self.budget.page_budget_layout)
        pages.addTab(page_budget, "Budget")

        self.budget.table_budget.horizontalHeader(). \
            setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.budget.table_budget.horizontalHeader(). \
            setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.budget.table_budget.horizontalHeader(). \
            setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.category = CategoryWidget()
        page_category = QFrame()
        page_category.setLayout(self.category.page_category_layout)
        pages.addTab(page_category, "Category list")

        self.setCentralWidget(pages)

    def set_line_category(self, category_data: list[CategoryTable]) -> None:
        """
        Заполняет выпадающий список категориями(вкладка Expenses)
        """
        not_stated = 'Not stated'
        self.expense.line_category.clear()
        for cat in category_data:
            if cat.name == not_stated:
                continue
            self.expense.line_category.addItem(cat.name)
