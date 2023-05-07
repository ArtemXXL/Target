import sys
import csv
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QColorDialog, QSizePolicy
from window import Ui_MainWindow
from PyQt5.QtWidgets import QMenu
from datetime import datetime
import sqlite3
n = 0


class Task:
    def __init__(self, id, title, text, box, date, color, image):
        self.id = id
        self.title = title
        self.text = text
        self.date = date
        self.box = box
        self.color = color
        self.image = image

    def __str__(self):
        return self.title + " : " + self.text


class Target(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # инициализация меню
        menuBar = self.menuBar()
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        importMenu = fileMenu.addMenu("Import tasks as")
        importMenu.addAction(".TXT", self.import_as_txt)
        importMenu.addAction(".CSV", self.import_as_csv)
        exportMenu = fileMenu.addMenu("Export tasks as")
        exportMenu.addAction(".TXT", self.export_as_txt)
        exportMenu.addAction(".CSV", self.export_as_csv)

        # добавление функций взаимодействия с виджетами
        self.Set_Colour_Button.clicked.connect(self.set_color)
        self.Set_Image_Button.clicked.connect(self.set_image)
        self.check_button(self.Is_Data, [self.DateTimeEdit])
        self.check_button(self.Is_Level, [self.Level_Label, self.Level_Line_Edit])
        self.check_button(self.Is_Colour, [self.Set_Colour_Button])
        self.check_button(self.Is_Image, [self.Set_Image_Button, self.image])
        self.Add_Button.clicked.connect(self.add_task_button)
        self.Is_Data.stateChanged.connect(self.check_data_button)
        self.Is_Colour.stateChanged.connect(self.check_colour_button)
        self.Is_Level.stateChanged.connect(self.check_level_button)
        self.Is_Image.stateChanged.connect(self.check_image_button)

        self.DateTimeEdit.setDateTime(datetime.now())
        self.During_ID = 0
        self.IDs = []
        self.Tasks = []
        self.During_Checked_ID = 0
        self.Checked_IDs = []
        self.Checked_Tasks = []

        # Загрузка уже существующих задач из базы данных
        con = sqlite3.connect("tasks.db")
        cur = con.cursor()
        result = cur.execute("SELECT * FROM task").fetchall()
        con.close()
        for i in result:
            self.During_ID = i[0]
            pixmap = QPixmap(i[5])
            date = None
            if i[3] != None:
                date = datetime.strptime(i[3], "%Y-%m-%d %H:%M:%S.%f")
            self.add_task(str(i[1]), str(i[2]), date, i[4], pixmap, i[5], is_not_save=False)

        # Загрузка уже существующих выполненных задач из базы данных
        con = sqlite3.connect("tasks.db")
        cur = con.cursor()
        result = cur.execute("SELECT * FROM checked_task").fetchall()
        con.close()
        for i in result:
            self.During_Checked_ID_ID = i[0]
            pixmap = QPixmap(i[5])
            date = None
            if i[3] != None:
                date = datetime.strptime(i[3], "%Y-%m-%d %H:%M:%S.%f")
            self.add_check_task(str(i[1]), str(i[2]), date, i[4], pixmap, i[5], is_not_save=False)

    def set_image(self):
        self.fname = QFileDialog.getOpenFileName(
            self, 'Выбрать картинку', '',
            'Картинка (*.jpg);;Картинка (*.png);;Все файлы (*)')[0]         # вызов диалогового окна выбора файла
        self.pixmap = QPixmap(self.fname)
        self.image.setPixmap(self.pixmap.scaled(70, 70))

    def set_color(self):
        color = QColorDialog.getColor()     # вызов диалогового окна выбора цвета
        if color.isValid():
            self.color = color.name()
            self.Set_Colour_Button.setStyleSheet("background-color: {}".format(color.name()))

    def add_task_button(self):
        title = self.Name_Line_Edit.text()
        text = self.Text_Line_Edit.text()
        date = None
        color = None
        sprite = None
        sprite_path = None
        # проверка включена ли дата в задачу
        if self.Is_Data.checkState():
            date = self.DateTimeEdit.dateTime().toPyDateTime()
        # проверка включен ли цвет в задачу
        if self.Is_Colour.checkState():
            color = self.color
        # проверка включено ли изображение в задачу
        if self.Is_Image.checkState():
            sprite = self.pixmap
            sprite_path = self.fname
        self.add_task(title, text, date, color, sprite, sprite_path)

    def add_check_task(self, title, text, date=None, color=None, sprite=None, sprite_path=None, is_not_save=True):
        layout = self.Scroll_Area_Layout_Checked.layout()
        # инициализация центрального виджета
        centralwidget = QtWidgets.QWidget(self)
        centralwidget.setObjectName("centralwidget")
        # инициализация блока с задачей
        Task_Box = QtWidgets.QGroupBox(centralwidget)
        Task_Box.setGeometry(QtCore.QRect(30, 30, 371, 131))
        font = QtGui.QFont()
        font.setPointSize(15)
        Task_Box.setFont(font)
        Task_Box.setObjectName("Task_Box_" + str(self.During_Checked_ID))
        Task_Box.setTitle(title)
        # инициализация текста задачи
        Text_Content = QtWidgets.QLabel(Task_Box)
        font = QtGui.QFont()
        font.setPointSize(10)
        Text_Content.setFont(font)
        Text_Content.setObjectName("Text_Content")
        Text_Content.setWordWrap(True)
        Text_Content.setText(text)
        Text_Content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # инициализация кнопки возобновления задачи
        Return_Button = QtWidgets.QPushButton(Task_Box)
        font = QtGui.QFont()
        font.setPointSize(10)
        Return_Button.setFont(font)
        Return_Button.setObjectName("Return_Button")
        Return_Button.setText("Return")
        # инициализация кнопки удаления задачи
        Delete_Button = QtWidgets.QPushButton(Task_Box)
        font = QtGui.QFont()
        font.setPointSize(10)
        Delete_Button.setFont(font)
        Delete_Button.setObjectName("Delete_Button")
        Delete_Button.id = self.During_Checked_ID
        Delete_Button.setText("Delete")
        # инициализация слоя с кнопками
        Button_Layout = QtWidgets.QHBoxLayout()
        Button_Layout.setObjectName("Button_Layout")
        Button_Layout.addWidget(Return_Button)
        Button_Layout.addWidget(Delete_Button)
        # инициализация слоя содержания
        Content_Layout = QtWidgets.QVBoxLayout()
        Content_Layout.setObjectName("Content_Layout")
        # инициализация слоя текста
        Text_Layout = QtWidgets.QHBoxLayout()
        Text_Content.setObjectName("Text_Content")
        # добовление в базу данных
        if is_not_save:
            con = sqlite3.connect("tasks.db")
            cur = con.cursor()
            result = cur.execute(f"""INSERT INTO checked_task(id, title, text) VALUES({self.During_Checked_ID},
                                        {"'" + title + "'"}, {"'" + text + "'"})""").fetchall()
        if color != None:  # проверка на наличие цвета
            # обновление базы данных
            if is_not_save:
                result = cur.execute(f"""UPDATE checked_task
                                        SET color = {"'" + str(color) + "'"}
                                        WHERE id = {self.During_Checked_ID}""").fetchall()
            # установка цвета задачи
            Task_Box.setStyleSheet("""QGroupBox { background-color: %(color)s; margin-top:1em;}
                                        QGroupBox::title { subcontrol-origin: padding; subcontrol-position: left top; 
                                        background: transparent; margin-top: -2.5em;} """ % {"color": color})
        if sprite_path != None:  # проверка на наличие изображения
            # обновление базы данных
            if is_not_save:
                result = cur.execute(f"""UPDATE checked_task
                                        SET image = {"'" + sprite_path + "'"}
                                        WHERE id = {self.During_Checked_ID}""").fetchall()
            # инициализация изображения
            image = QtWidgets.QLabel(Task_Box)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(image.sizePolicy().hasHeightForWidth())
            image.setSizePolicy(sizePolicy)
            image.setObjectName("image")
            image.setPixmap(sprite.scaled(70, 70))
            Text_Layout.addWidget(image)
        Text_Layout.addWidget(Text_Content)
        Content_Layout.addLayout(Text_Layout)
        if date != None:  # проверка на наличие даты
            # обновление базы данных
            if is_not_save:
                result = cur.execute(f"""UPDATE checked_task
                                                    SET date = {"'" + str(date) + "'"}
                                                    WHERE id = {self.During_Checked_ID}""").fetchall()
            font = QtGui.QFont()
            font.setPointSize(10)
            Date_Label = QtWidgets.QLabel(Task_Box)
            Date_Label.setFont(font)
            Date_Label.setObjectName("Date_Label")
            Date_Label.setText("until " + date.strftime("%d.%m.%y %H.%M"))
            Content_Layout.addWidget(Date_Label)
        Content_Layout.addLayout(Button_Layout)
        # сохранение измененний в базу данных
        if is_not_save:
            con.commit()
            con.close()
        # инициализация содержания задачи
        horizontalLayout_2 = QtWidgets.QHBoxLayout(Task_Box)
        horizontalLayout_2.setObjectName("horizontalLayout_2")
        horizontalLayout_2.addLayout(Content_Layout)
        # добавление задачи
        self.Checked_Tasks.append(Task(self.During_Checked_ID, title, text, Task_Box, date, color, sprite_path))
        print(str(self.Checked_Tasks[-1]))
        self.During_Checked_ID += 1
        self.Checked_IDs.append(self.During_Checked_ID)
        layout.insertWidget(layout.count(), Task_Box)

    def add_task(self, title, text, date=None, color=None, sprite=None, sprite_path=None, is_not_save=True):
        layout = self.Scroll_Area_Layout.layout()
        # инициализация центрального виджета
        centralwidget = QtWidgets.QWidget(self)
        centralwidget.setObjectName("centralwidget")
        # инициализация блока с задачей
        Task_Box = QtWidgets.QGroupBox(centralwidget)
        Task_Box.setGeometry(QtCore.QRect(30, 30, 371, 131))
        font = QtGui.QFont()
        font.setPointSize(15)
        Task_Box.setFont(font)
        Task_Box.setObjectName("Task_Box_" + str(self.During_ID))
        Task_Box.setTitle(title)
        # инициализация текста задачи
        Text_Content = QtWidgets.QLabel(Task_Box)
        font = QtGui.QFont()
        font.setPointSize(10)
        Text_Content.setFont(font)
        Text_Content.setObjectName("Text_Content")
        Text_Content.setWordWrap(True)
        Text_Content.setText(text)
        Text_Content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # инициализация кнопки редактирования
        Edit_Button = QtWidgets.QPushButton(Task_Box)
        font = QtGui.QFont()
        font.setPointSize(10)
        Edit_Button.setFont(font)
        Edit_Button.setObjectName("Edit_Button")
        Edit_Button.setText("Edit")
        # инициализация кнопки выполнения задачи
        Check_Button = QtWidgets.QPushButton(Task_Box)
        font = QtGui.QFont()
        font.setPointSize(10)
        Check_Button.setFont(font)
        Check_Button.setObjectName("Check_Button")
        Check_Button.setText("Check")
        Check_Button.clicked.connect(self.check_task)
        Check_Button.id = self.During_ID
        # инициализация кнопки удаления задачи
        Delete_Button = QtWidgets.QPushButton(Task_Box)
        font = QtGui.QFont()
        font.setPointSize(10)
        Delete_Button.setFont(font)
        Delete_Button.setObjectName("Delete_Button")
        Delete_Button.id = self.During_ID
        Delete_Button.setText("Delete")
        Delete_Button.clicked.connect(self.delete)
        # инициализация слоя с кнопками
        Button_Layout = QtWidgets.QHBoxLayout()
        Button_Layout.setObjectName("Button_Layout")
        Button_Layout.addWidget(Edit_Button)
        Button_Layout.addWidget(Check_Button)
        Button_Layout.addWidget(Delete_Button)
        # инициализация слоя содержания
        Content_Layout = QtWidgets.QVBoxLayout()
        Content_Layout.setObjectName("Content_Layout")
        # инициализация слоя текста
        Text_Layout = QtWidgets.QHBoxLayout()
        Text_Content.setObjectName("Text_Content")
        # добовление в базу данных
        if is_not_save:
            con = sqlite3.connect("tasks.db")
            cur = con.cursor()
            result = cur.execute(f"""INSERT INTO task(id, title, text) VALUES({self.During_ID},
                                {"'" + title + "'"}, {"'" + text + "'"})""").fetchall()
        if color != None:     # проверка на наличие цвета
            # обновление базы данных
            if is_not_save:
                result = cur.execute(f"""UPDATE task
                    SET color = {"'" + str(color) + "'"}
                    WHERE id = {self.During_ID}""").fetchall()
            # установка цвета задачи
            Task_Box.setStyleSheet("""QGroupBox { background-color: %(color)s; margin-top:1em;}
                    QGroupBox::title { subcontrol-origin: padding; subcontrol-position: left top; 
                    background: transparent; margin-top: -2.5em;} """ % {"color": color})
        if sprite_path != None:    # проверка на наличие изображения
            # обновление базы данных
            if is_not_save:
                result = cur.execute(f"""UPDATE task
                                SET image = {"'" + sprite_path + "'"}
                                WHERE id = {self.During_ID}""").fetchall()
            # инициализация изображения
            image = QtWidgets.QLabel(Task_Box)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(image.sizePolicy().hasHeightForWidth())
            image.setSizePolicy(sizePolicy)
            image.setObjectName("image")
            image.setPixmap(sprite.scaled(70, 70))
            Text_Layout.addWidget(image)
        Text_Layout.addWidget(Text_Content)
        Content_Layout.addLayout(Text_Layout)
        if date != None:    # проверка на наличие даты
            # обновление базы данных
            if is_not_save:
                result = cur.execute(f"""UPDATE task
                                            SET date = {"'" + str(date) + "'"}
                                            WHERE id = {self.During_ID}""").fetchall()
            font = QtGui.QFont()
            font.setPointSize(10)
            Date_Label = QtWidgets.QLabel(Task_Box)
            Date_Label.setFont(font)
            Date_Label.setObjectName("Date_Label")
            Date_Label.setText("until " + date.strftime("%d.%m.%y %H.%M"))
            Content_Layout.addWidget(Date_Label)
        Content_Layout.addLayout(Button_Layout)
        # сохранение измененний в базу данных
        if is_not_save:
            con.commit()
            con.close()
        # инициализация содержания задачи
        horizontalLayout_2 = QtWidgets.QHBoxLayout(Task_Box)
        horizontalLayout_2.setObjectName("horizontalLayout_2")
        horizontalLayout_2.addLayout(Content_Layout)
        # добавление задачи
        self.Tasks.append(Task(self.During_ID, title, text, Task_Box, date, color, sprite_path))
        print(str(self.Tasks[-1]))
        self.IDs.append(self.During_ID)
        self.During_ID += 1
        layout.insertWidget(layout.count(), Task_Box)

    def delete(self):
        id = self.sender().id      # получение ID кнопки
        num = self.IDs.index(id)       # получение номера необходимой задачи
        item = self.Scroll_Area_Layout.itemAt(num)      # получение необходимой задачи
        self.IDs.pop(num)      # удаление ID необходимой задачи из списка
        widget = item.widget()
        widget.deleteLater()    # удаление необходимой задачи
        # удаление задачи из базы данных
        con = sqlite3.connect("tasks.db")
        cur = con.cursor()
        result = cur.execute(f"""DELETE from task
                where id = {id}""").fetchall()
        con.commit()
        con.close()

    def check_task(self):
        id = self.sender().id  # получение ID кнопки
        num = self.IDs.index(id)  # получение номера необходимой задачи
        item = self.Scroll_Area_Layout.itemAt(num)  # получение необходимой задачи
        self.IDs.pop(num)  # удаление ID необходимой задачи из списка
        widget = item.widget()
        widget.deleteLater()
        # удаление задачи из базы данных
        con = sqlite3.connect("tasks.db")
        cur = con.cursor()
        res = cur.execute(f"""SELECT * FROM task
                        where id = {id}""").fetchall()[0]
        result = cur.execute(f"""DELETE from task
                        where id = {id}""").fetchall()
        con.commit()
        con.close()
        print(res)
        pixmap = QPixmap(res[5])
        date = None
        if res[3] != None:
            date = datetime.strptime(res[3], "%Y-%m-%d %H:%M:%S.%f")
        self.add_check_task(str(res[1]), str(res[2]), date, res[4], pixmap, res[5], is_not_save=True)

    def export_as_txt(self):   # добавить поддержку разовидностей задач!!!
        # открытие файла
        name = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", 'untitled.txt', "Текст (*.txt *.text)")[0]
        if name == '':
            return
        file = open(name, 'w')
        data = []
        # подготовка текста
        for i in self.Tasks:
            data.append(str(i))
        text = "\n".join(data)
        # сохранение файла
        file.write(text)
        file.close()

    def import_as_txt(self):      # добавить поддержку разовидностей задач!!!
        name = QFileDialog.getOpenFileName(self, 'Import text file', '', 'Текст (*.txt);;Текст (*.text)')[0]
        if name == '':
            return
        file = open(name, "r")
        data = file.readlines()
        for i in data:
            dat = i.split(" : ")
            title, text = dat[0], dat[1]
            self.add_task(title, text)
        file.close()

    def export_as_csv(self):      # добавить поддержку разовидностей задач!!!
        # обработка данных
        data = []
        for i in self.Tasks:
            dat = {"title": str(i.title), "text": str(i.text)}
            data.append(dat)
        # открытие файла
        name = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", 'untitled.csv', 'csv (.csv)')[0]
        if name == '':
            return
        with open(name, 'w', newline='') as f:
            if data == []:
                return
            # заполнение файла
            writer = csv.DictWriter(
                f, fieldnames=list(data[0].keys()),
                delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            for d in data:
                writer.writerow(d)

    def import_as_csv(self):      # добавить поддержку разовидностей задач!!!
        name = QFileDialog.getOpenFileName(self, 'Import CSV file', '', 'CSV (*.csv)')[0]
        if name == '':
            return
        file = open(name, "r")
        data = file.readlines()
        for i in data[1::]:
            dat = i.split(";")
            title, text = dat[0], dat[1]
            self.add_task(title, text)
        file.close()

    def check_button(self, checkBox, data):
        if checkBox.isChecked():
            for i in data:
                i.show()
        else:
            for i in data:
                i.hide()

    def check_data_button(self):
        self.check_button(self.Is_Data, [self.DateTimeEdit])

    def check_level_button(self):
        self.check_button(self.Is_Level, [self.Level_Label, self.Level_Line_Edit])

    def check_colour_button(self):
        self.check_button(self.Is_Colour, [self.Set_Colour_Button])

    def check_image_button(self):
        self.check_button(self.Is_Image, [self.Set_Image_Button, self.image])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Target()
    ex.show()
    sys.exit(app.exec_())