"""
Модуль реализующий Presenter
"""
from __future__ import annotations
# pylint: disable = no-name-in-module

from typing import List, Union, Any, Sequence
from datetime import datetime

from PySide6.QtWidgets import QMenu, QMessageBox, QHeaderView
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QCursor
from sqlalchemy import Row
from sqlalchemy.orm import sessionmaker, Session

from bookkeeper.view.app_interface import MainWindow, ExpenseTableModel
from bookkeeper.view.app_interface import BudgetModel, CatExpenseModel
from bookkeeper.utils import read_tree, budget_data_transform
from bookkeeper.config import NOT_STATED_NAME

from bookkeeper.repository.my_orm import delete_all, get_all, get_by_pk,\
    get_category_pk_by_name, get_week_expenses, get_month_expenses,\
    get_month_expenses_by_cat, get_day_expenses_by_cat, get_day_expenses,\
    get_expenses_data, insert_values, update_by_pk, delete_by_pk
from bookkeeper.models.sqlalchemy_models import ExpenseTable, BudgetTable, CategoryTable


class Presenter:
    """
    Реализация Presenter
    Parameters:
    ----------

    Attributes:
    ----------
    expense_data:
        данные в таблице на листе Expenses.
        Сюда записываются отредактированные пользователем ячейки
        Затем строки расходов сохранятся в репозиторий
        Реализован только для возможности редактирования таблицы как в Excel
    main_window:
        окно приложения
    session_factory:
        !!!!!
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        """
        Инициализация

        Attributes:
        -----------
        session_factory:
            Фабрика генерирующая сессию для подключения к БД через sqlalchemy

        Returns:
        --------
            None
        """
        self.session_factory = session_factory
        self.expense_data = self.expense_data_init()
        budget_data = self.budget_data_init()
        data = budget_data_transform(budget_data)
        self.main_window = MainWindow(self.expense_data, data)
        self.main_window.category.text_box.setText(
            read_categories(self.category_data_init())
        )

        self.main_window.set_line_category(self.category_data_init())
        self.day_expense_by_cat()
        self.main_window.budget.table_cat_expenses.horizontalHeader(). \
            setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        self.main_window.budget.table_cat_expenses.horizontalHeader(). \
            setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.main_window.budget.table_cat_expenses.verticalHeader().setVisible(False)

        self.main_window.category.edit_button. \
            clicked.connect(self.commit_categories)
        self.main_window.expense.add_button. \
            clicked.connect(self.add_expense_row)
        self.main_window.budget.change_button. \
            clicked.connect(self.change_budget)

        self.main_window.expense.expense_table. \
            setContextMenuPolicy(Qt.CustomContextMenu)

        self.main_window.expense.expense_table. \
            customContextMenuRequested. \
            connect(self.table_menu)

        self.main_window.budget.cat_day_expense_button. \
            clicked.connect(self.day_expense_by_cat)
        self.main_window.budget.cat_month_expense_button. \
            clicked.connect(self.month_expense_by_cat)

    def expense_data_init(self) -> list[list[str]]:
        """
        Метод для инициализации данных таблицы расходов(вкладка Expenses)

        Returns:
        --------
            list[list[str]]
        """
        data = get_expenses_data(self.session_factory)
        data_to_expense_table = [[row.id, row.expense_date.strftime("%d-%m-%Y %H:%M"),
                                  row.amount, row.name, row.comment] for row in data]

        if len(data_to_expense_table) == 0:
            now = datetime.now().strftime('%d-%m-%Y %H:%M')
            data_to_expense_table = [
                ['0', now, '1500', 'food', 'Example!!']
            ]
        return data_to_expense_table

    def budget_data_init(self) -> List[BudgetTable]:
        """
        Метод для инициализации данных таблицы бюджета (вкладка Budget)
        Обновляет поле amount

        Returns:
        --------
            List[BudgetTable]
        """
        day_expenses_new = get_day_expenses(self.session_factory)
        update_by_pk(BudgetTable, 1, {"amount": day_expenses_new}, self.session_factory)

        week_expenses_new = get_week_expenses(self.session_factory)
        update_by_pk(BudgetTable, 2, {"amount": week_expenses_new}, self.session_factory)

        month_expenses_new = get_month_expenses(self.session_factory)
        update_by_pk(BudgetTable, 3, {"amount": month_expenses_new}, self.session_factory)

        day_budget_new = get_by_pk(BudgetTable, 1, self.session_factory)
        week_budget_new = get_by_pk(BudgetTable, 2, self.session_factory)
        month_budget_new = get_by_pk(BudgetTable, 3, self.session_factory)
        return [day_budget_new, week_budget_new, month_budget_new]

    def category_data_init(self) -> list[CategoryTable]:
        """
        Метод для инициализации списка категорий

        Returns:
        --------
            list[CategoryTable]
        """
        res: list[CategoryTable] = get_all(CategoryTable, self.session_factory)
        return res

    def day_expense_by_cat(self) -> None:
        """
        Передача данных о расходах за день в таблицу расходы по категориям(вкладка Budget)
        Активируется при запуске приложения, изменении таблицы расходов и
        при нажатии кнопки day во вкладке(Budget)

        Returns:
        --------
            None
        """
        data: Union[Sequence[Row[Any]], List[List[str]]] = get_day_expenses_by_cat(
            self.session_factory
        )

        if len(data) == 0:
            data = [
                ['No expenses today ', '0']
            ]
        model = CatExpenseModel(data)
        self.main_window.budget.table_cat_expenses.setModel(model)

        self.main_window.budget.cat_day_expense_button.setStyleSheet(
            'QPushButton {background-color: darkGray; color: black;}'
        )
        self.main_window.budget.cat_month_expense_button.setStyleSheet(
            'QPushButton {background-color: white; color: black;}'
        )

    def month_expense_by_cat(self) -> None:
        """
        Передача данных о расходах за день в таблицу расходы по категориям(вкладка Budget)
        Активируется при нажатии кнопки month во вкладке Budget

        Returns:
        --------
            None
        """
        data: Union[Sequence[Row[Any]], List[List[str]]] = get_month_expenses_by_cat(
            self.session_factory
        )

        if len(data) == 0:
            data = [
                ['No expenses ', '0']
            ]
        model = CatExpenseModel(data)
        self.main_window.budget.table_cat_expenses.setModel(model)

        self.main_window.budget.cat_month_expense_button.setStyleSheet(
            'QPushButton {background-color: darkGray; color: black;}'
        )
        self.main_window.budget.cat_day_expense_button.setStyleSheet(
            'QPushButton {background-color white: green; color: black;}'
        )

    def change_budget(self) -> None:
        """
        Меняет бюджет при нажатии кнопки "chage budget" во вкладке Budget
        Записывает данные о бюджете в БД

        Returns:
        --------
            None
        """
        day_budget = self.main_window.budget.line_day_budget.text()
        if not amount_right_input(self.main_window, day_budget):
            return None
        week_budget = self.main_window.budget.line_week_budget.text()
        if not amount_right_input(self.main_window, week_budget):
            return None
        month_budget = self.main_window.budget.line_month_budget.text()
        if not amount_right_input(self.main_window, month_budget):
            return None
        day_budget_update = {
            "period": "day",
            "budget": day_budget
        }
        week_budget_update = {
            "period": "week",
            "budget": week_budget
        }
        month_budget_update = {
            "period": "month",
            "budget": month_budget
        }
        update_by_pk(BudgetTable, 1, day_budget_update, self.session_factory)
        update_by_pk(BudgetTable, 2, week_budget_update, self.session_factory)
        update_by_pk(BudgetTable, 3, month_budget_update, self.session_factory)

        budget_data = self.budget_data_init()
        data = budget_data_transform(budget_data)
        budget_model = BudgetModel(data)
        self.main_window.budget.table_budget.setModel(budget_model)
        return None

    def update_expense_cat(self, update_cat: dict[int, int],
                           update_none: list[int]) -> None:
        """
        Обновляет id категории в репозитории расходов:
        У всех расходов с cat_id == old_cat_pk, category меняется на new_cat_pk

        на вход словарь с заменами {old_cat_id: new_cat_id}
        создаём словарь {old_cat_id: [id]} строчки, которые нужно заменить

        Attributes:
        -----------
            update_cat: dict[int, int] - словарь с заменами
            update_none: list[int] - список категорий, котрые будут None

        Returns:
        --------
            None
        """
        data: list[ExpenseTable] = get_all(ExpenseTable, self.session_factory)
        for none_id in update_none:
            for row in data:
                if row.cat_id == none_id:
                    values = {
                        "cat_id": 1
                    }
                    update_by_pk(ExpenseTable, row.id, values, self.session_factory)

        update_expense_row: dict[int, Any] = {}
        for key in update_cat:
            update_expense_row[key] = []
            for row in get_all(ExpenseTable, self.session_factory):
                if row.cat_id == key:
                    update_expense_row[key].append(row.id)

        for key in update_cat:
            for expense_id in update_expense_row[key]:
                values = {
                    "cat_id": update_cat[key]
                }
                update_by_pk(ExpenseTable, expense_id, values, self.session_factory)

    def commit_categories(self) -> None:
        """
        Меняет список категорий:
        Активируется при нажатии кнопки "commit changes" во вкладке Category list

        Returns:
        --------
            None
        """
        cat_text = self.main_window.category.text_box.toPlainText()
        data = cat_text.splitlines()

        have_same_categories = same_categories_check(self.main_window, data)
        if not have_same_categories:
            self.main_window.category.text_box.setText(
                read_categories(self.category_data_init())
            )
            return None

        old_data = self.category_data_init()
        delete_all(CategoryTable, self.session_factory)
        insert_values(CategoryTable, {"name": NOT_STATED_NAME, "parent": None},
                      self.session_factory,
                      )

        for row in read_tree(data):
            if row[1] is None:
                insert_values(CategoryTable, {"name": row[0]}, self.session_factory)
            else:
                parent_pk = get_category_pk_by_name(row[1],
                                                    self.session_factory)
                values = {
                    "name": row[0],
                    "parent": parent_pk
                }
                insert_values(CategoryTable, values, self.session_factory)
        update_data: list[CategoryTable] = get_all(CategoryTable, self.session_factory)

        updated_cat_id = {}
        update_to_none = []
        for old_cat_row in old_data:
            has_same = False
            for new_cat_row in update_data:
                if new_cat_row.name == 'Not stated':
                    continue
                if old_cat_row.name == new_cat_row.name:
                    has_same = True
                    updated_cat_id[old_cat_row.id] = new_cat_row.id
            if not has_same:
                update_to_none.append(old_cat_row.id)

        self.update_expense_cat(updated_cat_id, update_to_none)
        self.main_window.set_line_category(self.category_data_init())

        self.expense_data = self.expense_data_init()
        expense_model = ExpenseTableModel(self.expense_data)
        self.main_window.expense.expense_table.setModel(expense_model)

        self.day_expense_by_cat()
        return None

    def table_menu(self) -> None:
        """
        Меню Delete row|Update cell строки расходов.
        Срабатывает при нажатии правой кнопки мыши в ячейке/ах таблицы расходов
        вкладка(Expenses)

        Returns:
        --------
            None
        """
        selected = self.main_window.expense.expense_table.selectedIndexes()
        if not selected:
            return
        menu = QMenu()
        delete_act = menu.addAction('Delete row')
        update_table_act = menu.addAction('Update cell')
        delete_act.triggered.connect(
            lambda: self.remove_row(selected))
        update_table_act.triggered.connect(
            lambda: self.update_cell(selected))
        menu.exec_(QCursor.pos())

    def remove_row(self,
                   indexes: List[QModelIndex]
                   ) -> None:
        """
        Удаление сроки таблицы расходов.
        Срабатывае при нажатии кнопки "Delete row". См table_menu

        Attributes:
        -----------
        indexes: List[QModelIndex]
            Список индексов из таблицы, которые нужно удалить
        """
        rows = set(index.row() for index in indexes)
        for row in rows:
            del_pk = int(self.expense_data[row][0])
            delete_by_pk(ExpenseTable, del_pk, self.session_factory)

        self.expense_data = self.expense_data_init()
        expense_model = ExpenseTableModel(self.expense_data)
        self.main_window.expense.expense_table.setModel(expense_model)

        budget_data = self.budget_data_init()
        data = budget_data_transform(budget_data)
        budget_model = BudgetModel(data)
        self.main_window.budget.table_budget.setModel(budget_model)

        self.day_expense_by_cat()

    def update_cell(self,
                    indexes: list[QModelIndex]
                    ) -> None:
        """
        Обновление выделенных ячеек.
        Срабатывае при нажатии кнопки "Update cell". См table_menu
        """
        mapper = {1: "expense_date",
                  2: "amount",
                  3: "cat_id",
                  4: "comment"}
        rows = list(index.row() for index in indexes)
        columns = list(index.column() for index in indexes)
        for row, col in zip(rows, columns):
            update_values: dict[str, Any] = {}
            if check_correct_update(
                    self.main_window,
                    row, col,
                    self.expense_data,
                    self.category_data_init()
            ):
                update_values[mapper[col]] = self.expense_data[row][col]
                if col == 1:
                    update_values[mapper[col]] = datetime.strptime(
                        self.expense_data[row][col], "%d-%m-%Y %H:%M"
                    )
                if col == 3:
                    update_values["cat_id"] = int(get_category_pk_by_name(
                        update_values["cat_id"], self.session_factory))
                update_pk = int(self.expense_data[row][0])
                update_by_pk(ExpenseTable, update_pk, update_values, self.session_factory)

        self.expense_data = self.expense_data_init()
        expense_model = ExpenseTableModel(self.expense_data)
        self.main_window.expense.expense_table.setModel(expense_model)

        budget_data = self.budget_data_init()
        data = budget_data_transform(budget_data)
        budget_model = BudgetModel(data)
        self.main_window.budget.table_budget.setModel(budget_model)

        self.day_expense_by_cat()

    def add_expense_row(self) -> None:
        """
        Добавляет в репозиторий новую запись, обновляет таблицу во вкладке(Expense)
        Активируется при нажатии кнопки "Add expense" во вкладке Expenses
        """
        text_date = self.main_window.expense.line_date.text()
        amount = self.main_window.expense.line_amount.text()
        category = self.main_window.expense.line_category.currentText()
        comment = self.main_window.expense.line_comment.text()
        if not amount_right_input(self.main_window, amount):
            return None
        if not date_right_input(self.main_window, text_date):
            return None
        date = datetime.strptime(text_date, '%d-%m-%Y %H:%M')
        cat_id = get_category_pk_by_name(category, self.session_factory)

        values = {
            "cat_id": cat_id,
            "amount": amount,
            "comment": comment,
            "expense_date": date,
        }
        insert_values(ExpenseTable, values, self.session_factory)

        self.expense_data = self.expense_data_init()

        expense_model = ExpenseTableModel(self.expense_data)
        self.main_window.expense.expense_table.setModel(expense_model)

        budget_data = self.budget_data_init()
        data = budget_data_transform(budget_data)
        budget_model = BudgetModel(data)
        self.main_window.budget.table_budget.setModel(budget_model)
        self.day_expense_by_cat()

        return None


def get_subcategories(cat: CategoryTable, category_data: list[CategoryTable]
                      ) -> list[CategoryTable]:
    """
    Получить список подкатегорий
    """
    sub_cat_pk = [data.id for data in category_data if cat.id == data.parent]
    sub_cat = [x for x in category_data if x.id in sub_cat_pk]
    return sub_cat


def print_sub_cat(sub_cat: CategoryTable,
                  space_num: int,
                  category_data: list[CategoryTable]) -> str:
    """
    формирует строку в виде дерева из подкатегорий
    """
    cat_string = space_num * '\t' + f'{sub_cat.name} \n'
    sub_sub_cat = get_subcategories(sub_cat, category_data)
    for sub in sub_sub_cat:
        cat_string += print_sub_cat(sub, space_num + 1, category_data)
    return cat_string


def read_categories(category_data: list[CategoryTable]) -> str:
    """
    Формирует строку в виде дерева из списка категорий
    """
    cat_string = ''
    not_stated = 'Not stated'
    for cat in category_data:
        if cat.name == not_stated:
            continue
        if cat.parent is None:
            cat_string += f'{cat.name} \n'
            space_num = 1
            for sub_cat in get_subcategories(cat, category_data):
                cat_string += print_sub_cat(sub_cat, space_num, category_data)
        else:
            continue
    return cat_string


def date_right_input(main_window: MainWindow, date: str) -> bool:
    """
    Проверка на правильное заполнение поля %date
    date приводится к виду %d-%m-%Y %H:%M
    """
    try:
        datetime.strptime(date, '%d-%m-%Y %H:%M')
        return True
    except ValueError:
        QMessageBox.critical(main_window, 'Error', f"Date {date} is incorrect")
        return False


def amount_right_input(main_window: MainWindow, amount: str) -> bool:
    """
    Проверка на оправилньное заполнение поля amount:
        type(amount) is float
        amount >= 0
    """
    try:
        float(amount)
    except ValueError:
        error_message = f"Amount {amount} should be a number"
        QMessageBox.critical(main_window, 'Error', error_message)
        return False
    if float(amount) < 0:
        error_message = f"Amount {amount} should be positive"
        QMessageBox.critical(main_window, 'Error', error_message)
        return False
    return True


def same_categories_check(main_window: MainWindow, categories: list[str]) -> bool:
    """
    Проверка на одиновые категории
    """
    new_categories = []
    for i, cat in enumerate(categories):
        cat = cat.strip()
        cat = cat.lstrip()
        if not cat == '':
            new_categories.append(cat)
    same_categories = [x for i, x in enumerate(new_categories)
                       if i != new_categories.index(x)]
    if len(same_categories) != 0:
        QMessageBox.critical(main_window, 'Error', "SameCategories")
        return False
    return True


def category_right_input(
        main_window: MainWindow,
        new_cat_name: str,
        category_data: list[CategoryTable]) -> bool:
    """
    Проверка на правильное заполнение списка категорий
    """
    cat_data = [category.name for category in category_data]
    if new_cat_name in cat_data:
        return True
    error_message = f"Category {new_cat_name} is not in category list"
    QMessageBox.critical(main_window, 'Error', error_message)
    return False


def check_correct_update(main_window: MainWindow,
                         row: int, col: int,
                         expense_data: list[list[str]],
                         category_data: list[CategoryTable]) -> bool:
    """
    Проверка на правильное обновление ячеек в таблице расходов:
        правильное заполнение поля date,
        првильное заполнение amount,
        правильное заполнение category
    """
    if expense_data[row][0] == '0':
        error_message = "It is an example! Try App by yourself :)"
        QMessageBox.critical(main_window, 'Error', error_message)
        return False
    new_data_cell = expense_data[row][col]
    if col == 1:
        return date_right_input(main_window, new_data_cell)
    if col == 2:
        if not amount_right_input(main_window, new_data_cell):
            return False
    if col == 3:
        return category_right_input(main_window, new_data_cell, category_data)
    return True
