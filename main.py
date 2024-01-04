import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QStatusBar, QPlainTextEdit, QComboBox, \
    QPushButton, QFormLayout
import sqlite3


class CoffeeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.setWindowTitle("Эспрессо")
        self.setGeometry(100, 100, 800, 600)

        self.tableWidget.setGeometry(0, 0, 800, 600)
        self.addButton.clicked.connect(self.add)
        self.editButton.clicked.connect(self.edit)
        self.setup_table()

    def add(self):
        print('add')
        self.add_form = AddWidget(self)
        self.add_form.show()

    def edit(self):
        print('edit')
        self.selected_row = self.tableWidget.currentRow()
        if self.selected_row != -1:
            row = []
            for col in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(self.selected_row, col).text()
                row.append(item)
            # print(row)
            self.statusBar().showMessage('')
            self.edit_form = AddWidget(self, mode=self.selected_row, row=row)
            self.edit_form.show()

        else:
            self.statusBar().showMessage('Ничего не выбрано')

    def setup_table(self):
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(
            ["ID", "Сорт", "Степень обжарки", "Молотый/в зернах", "Описание вкуса", "Цена", "Объем упаковки"])

        self.load_data()

    def load_data(self):
        connection = sqlite3.connect("coffee.sqlite")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM coffee")
        data = cursor.fetchall()

        connection.close()

        self.populate_table(data)

    def populate_table(self, data):
        self.tableWidget.setRowCount(len(data))

        for row_index, row_data in enumerate(data):
            for col_index, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.tableWidget.setItem(row_index, col_index, item)


class AddWidget(QDialog):
    def __init__(self, parent=None, mode=-1, row=None):
        self.mode = mode
        self.row = row
        super().__init__(parent)
        self.setWindowTitle('Обновить')
        self.setFixedSize(300, 260)
        self.is_save = False
        if self.mode == -1:
            self.statusbar = QStatusBar()
            self.sort = QPlainTextEdit()
            self.pow = QPlainTextEdit()
            self.is_molotiy = QPlainTextEdit()
            self.taste_info = QPlainTextEdit()
            self.price = QPlainTextEdit()
            self.size = QPlainTextEdit()
        else:
            print(self.row)
            self.sort = QPlainTextEdit(self.row[1])
            self.pow = QPlainTextEdit(self.row[2])
            self.is_molotiy = QPlainTextEdit(self.row[3])
            self.taste_info = QPlainTextEdit(self.row[4])
            self.price = QPlainTextEdit(self.row[5])
            self.size = QPlainTextEdit(self.row[6])
            self.statusbar = QStatusBar()

        self.pushButton = QPushButton("Обновить")
        self.con = sqlite3.connect("coffee.sqlite")

        layout = QFormLayout()
        layout.addRow("Сорт:", self.sort)
        layout.addRow("Степень обжарки:", self.pow)
        layout.addRow("Молотый/в зернах:", self.is_molotiy)
        layout.addRow("Описание вкуса:", self.taste_info)
        layout.addRow("Цена:", self.price)
        layout.addRow("Объем упаковки:", self.size)
        layout.addRow(self.pushButton)
        layout.addRow(self.statusbar)

        self.pushButton.clicked.connect(self.save_record)

        self.setLayout(layout)

    def get_adding_verdict(self):
        return self.is_save

    def save_record(self):
        sort = self.sort.toPlainText()
        pow = self.pow.toPlainText()
        is_molotiy = self.is_molotiy.toPlainText()
        taste_info = self.taste_info.toPlainText()
        price = self.price.toPlainText()
        size = self.size.toPlainText()
        res = ''
        if self.mode == -1:
            res = (f"insert into coffee(sort, pow, is_molotiy, taste_info, price, size) values('{sort}', '{pow}',"
                   f" '{is_molotiy}', '{taste_info}', '{price}', '{size}')")
        else:
            res = (f"update coffee set sort='{sort}', pow={pow}, is_molotiy='{is_molotiy}', taste_info='{taste_info}',"
                   f" price={price}, size={size} where id = {self.row[0]}")

        if (all([sort, pow, is_molotiy, taste_info, price, size]) and pow.isdigit() and
                price.isdigit() and size.isdigit() and pow.isdigit()):
            self.is_save = True
            cur = self.con.cursor()
            cur.execute(res).fetchall()
            self.con.commit()
            self.parent().load_data()
            self.close()
        else:
            self.is_save = False
            self.statusbar.showMessage('Неверно заполнена форма')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec_())
