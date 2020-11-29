from PyQt5.QtSql import *
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QMenu, QAction, QFileDialog, QHeaderView, QAbstractScrollArea


class Viewing_db(QMainWindow):
    def __init__(self, parent=None):
        super(Viewing_db, self).__init__(parent)
        self.resize(1000, 600)
        self.setWindowTitle("Просмотр базы данных v2.1")
        # создаем виджеты
        self.main_widget    = QtWidgets.QWidget(self)
        self.labelsearch    = QtWidgets.QLabel(self.main_widget)
        self.line_search    = QtWidgets.QLineEdit(self.main_widget)
        self.combo_field    = QtWidgets.QComboBox(self.main_widget)
        self.tview_dbase    = QtWidgets.QTableView(self.main_widget)
        self.label_table    = QtWidgets.QLabel(self.main_widget)
        self.combo_dbase    = QtWidgets.QComboBox(self.main_widget)
        self.pushB_dbase    = QtWidgets.QPushButton(self.main_widget)
        # задаем расположение
        self.gridLayout = QtWidgets.QGridLayout(self.main_widget)
        # минимальная ширина
        self.gridLayout.setColumnMinimumWidth(1, 150)
        self.gridLayout.setColumnMinimumWidth(2, 100)
        self.gridLayout.setColumnMinimumWidth(4, 100)
        # коффициенты растяжения
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 5)
        self.gridLayout.setColumnStretch(2, 2)
        self.gridLayout.setColumnStretch(3, 1)
        self.gridLayout.setColumnStretch(4, 2)
        self.gridLayout.setColumnStretch(5, 1)
        # расположение на сетке
        self.gridLayout.addWidget(self.labelsearch, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.line_search, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.combo_field, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.label_table, 0, 3, 1, 1)
        self.gridLayout.addWidget(self.combo_dbase, 0, 4, 1, 1)
        self.gridLayout.addWidget(self.pushB_dbase, 0, 5, 1, 1)
        self.gridLayout.addWidget(self.tview_dbase, 1, 0, 1, 6)
        self.setCentralWidget(self.main_widget)
        # подписи
        self.labelsearch.setText("Фильтр: столбец содержит  ")
        self.label_table.setText("  Выбор таблицы в базе данных  ")
        self.pushB_dbase.setText("  Выбор базы данных  ")
        self.statusBar().showMessage('Выберите базу данных!')
        # задаем события (сигналы)
        self.pushB_dbase.clicked.connect(self.pushB_dbase_clicked)
        self.combo_dbase.currentIndexChanged.connect(self.combo_dbase_currentIndexChanged)
        self.horizontalHeader = self.tview_dbase.horizontalHeader()
        self.horizontalHeader.sectionClicked.connect(self.tview_dbase_horizontalHeader_sectionClicked)
        self.line_search.textChanged.connect(self.line_search_textChanged)
        self.combo_field.currentIndexChanged.connect(self.combo_field_currentIndexChanged)

    # выбор файла базы данных SQLite
    def pushB_dbase_clicked(self):
        fileName, filetype = QFileDialog.getOpenFileName(self,
                            "Выбор файла базы данных SQLite",
                            "",
                            "SQLite (*.sqlite);;DataBase (*.db);;DataBase3 (*.db3)")
        if fileName:
            self.db = QSqlDatabase.addDatabase('QSQLITE')
            self.db.setDatabaseName(fileName)
            self.db.open()
            # заполняем QComboBox списком таблиц
            lst_tables = self.db.tables()
            self.combo_dbase.blockSignals(True)
            self.combo_dbase.clear()
            self.combo_dbase.blockSignals(False)
            for table in lst_tables:
                self.combo_dbase.addItem(table)
                self.setWindowTitle("Просмотр базы данных: " + fileName)

    # выбор таблицы по значению QComboBox
    def combo_dbase_currentIndexChanged(self, Index):
        # задаем и выводим в QTableView модель выбранной таблицы
        self.model = QSqlTableModel(self, self.db)
        self.model.setTable(self.combo_dbase.currentText())
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit )
        self.model.select()

        self.proxy = QtCore.QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)

        self.tview_dbase.setModel(self.proxy)
        # заполняем QComboBox списком заголовков столбцов модели
        self.combo_field.blockSignals(True)
        self.combo_field.clear()
        self.combo_field.blockSignals(False)
        for col in range(self.model.columnCount()):
            self.combo_field.addItem(str(self.model.headerData(col, QtCore.Qt.Horizontal, 0)))
            #self.tview_dbase.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self.line_search.setText('')

    # создание QMenu с уникальными значениями по клику на заголовке столбца QTableView
    def tview_dbase_horizontalHeader_sectionClicked(self, logicalIndex):
        self.logicalIndex   = logicalIndex
        self.menu_values    = QMenu(self)
        self.signalMapper   = QtCore.QSignalMapper(self)
        # значение QComboBox и столбца фильтрации заменим на выбранный столбец
        self.combo_field.blockSignals(True)
        self.combo_field.setCurrentIndex(self.logicalIndex)
        self.combo_field.blockSignals(False)
        self.proxy.setFilterKeyColumn(self.logicalIndex)
        # создадим список уникальных значений (используем модель, а не представление)
        # модель выводит не больше 256. Грузить оставшиеся?
        self.model.select()
        values_unique = [   self.model.index(row, self.logicalIndex).data()
                            for row in range(self.model.rowCount())
                            ]
        # первый пункт меню для сброса фильтра
        action_all = QAction("Все", self)
        action_all.triggered.connect(self.action_all_triggered)
        self.menu_values.addAction(action_all)
        self.menu_values.addSeparator()
        # формирование пунктов меню на основе уникальных значений
        for action_num, action_name in enumerate(sorted(list(set(values_unique)))):
            action = QAction(str(action_name), self) # наименование, число -> строка
            self.signalMapper.setMapping(action, action_num)
            action.triggered.connect(self.signalMapper.map)
            self.menu_values.addAction(action)

        self.signalMapper.mapped.connect(self.signalMapper_mapped)
        # позиция для отображения QMenu
        header_pos = self.tview_dbase.mapToGlobal(self.horizontalHeader.pos())
        pos_y = header_pos.y() + self.horizontalHeader.height()
        pos_x = header_pos.x() + self.horizontalHeader.sectionViewportPosition(self.logicalIndex)
        #posX = headerPos.x() + self.horizontalHeader.sectionPosition(self.logicalIndex)
        #print(self.horizontalHeader.sectionPosition(self.logicalIndex))
        #print(self.horizontalHeader.sectionViewportPosition (self.logicalIndex))
        self.menu_values.exec_(QtCore.QPoint(pos_x, pos_y))

    # выбор QAction в QMenu для вывода всех записей
    def action_all_triggered(self):
        self.line_search.setText('')

    # выбор записей содержащих наименовние QAction из QMenu
    def signalMapper_mapped(self, i):
        name_action = self.signalMapper.mapping(i).text()
        self.line_search.setText(str(name_action))

    # выбор записей при изменении текста в QLineEdit
    def line_search_textChanged(self, text):
        # если combo_db пуст, то не добавлена база или нет таблиц в базе т.е. фильтр - ошибка
        if self.combo_dbase.currentIndex() < 0:
            self.line_search.setText('')
            self.statusBar().showMessage('Не выбрана база данных или отсутсвуют таблицы!')
        else:
            self.model.select()
            search = QtCore.QRegExp(    text,
                                        QtCore.Qt.CaseInsensitive,
                                        QtCore.QRegExp.RegExp
                                        )
            self.proxy.setFilterRegExp(search)
            self.rowCount_in_statusBar()

    # выбор столбца для применения фильтрации
    def combo_field_currentIndexChanged(self, index):
        self.proxy.setFilterKeyColumn(index)
        self.rowCount_in_statusBar()

    # подсчет и вывод количества запсей
    def rowCount_in_statusBar(self):
        while self.model.canFetchMore():
            self.model.fetchMore()
        self.statusBar().showMessage('Найдено записей: ' + str(self.proxy.rowCount()))


if __name__ == "__main__":
    import sys
    app  = QApplication(sys.argv)
    main = Viewing_db()
    main.show()
    sys.exit(app.exec_())