import cv2
import os
import traceback
import qrcode
from PIL import Image

import sys
from PyQt5.QtWidgets import QLabel, QApplication, QTextEdit, QPlainTextEdit, QFileDialog, QPushButton, QWidget, QDialog, \
    QMainWindow
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtGui import QImage, QPixmap, QFont
from settings_to_make_qr import SETTINGS_QR
from settings_dialog import Ui_Dialog as settings_dialog

QR_TEXT = ''  # Константа для хранения текста QR-Кода


class App(QMainWindow):
    """Основной класс программы, с описанием логики"""

    def __init__(self):  # объявление конструктора
        super().__init__()  # наследование от базового класса
        self.setUp()  # первичная настройка

    def setUp(self):
        font = QFont()  # создание объекта шрифта
        font.setPointSize(14)
        font.setItalic(True)

        self.setWindowTitle("ZaCoder")  # первичная настройка основного окна проекта
        self.setObjectName("MainWindow")
        self.resize(1280, 830)
        self.setStyleSheet("background-color: #293133;")

        self.camera = QLabel(self)  # окно, для вывода изображения с камеры
        self.camera.setGeometry(QRect(280, 10, 720, 400))
        self.camera.setText("Пытаемся определить камеру,\n пожалуйста, подождите")
        self.camera.setFont(font)  # устновка шрифта для текста

        self.qr_text_field = QTextEdit(self)  # текстовое поле, для отображения текста qr-кода
        self.qr_text_field.setGeometry(QRect(50, 500, 300, 300))
        self.qr_text_field.setFont(font)  # устновка шрифта для текста
        self.qr_text_field.setStyleSheet("color: #FFFFFF")  # настройка цвета окна

        self.qr_image_field = QLabel(self)  # окно для вывода изображения qr-кода
        self.qr_image_field.setGeometry(QRect(930, 500, 300, 300))

        self.btn_to_make_qr_from_text = QPushButton(self)  # кнопка для генерации qr-кода из текста
        self.btn_to_make_qr_from_text.setGeometry(QRect(100, 450, 200, 30))
        self.btn_to_make_qr_from_text.setText("Создать QR-код")
        self.btn_to_make_qr_from_text.setFont(font)
        self.btn_to_make_qr_from_text.setStyleSheet("background-color: #FFA500")

        self.btn_to_select_file = QPushButton(self)  # кнопка для окрытия диалогового окна
        self.btn_to_select_file.setGeometry(QRect(970, 450, 230, 30))
        self.btn_to_select_file.setText("Загрузить изображение")
        self.btn_to_select_file.setFont(font)
        self.btn_to_select_file.setStyleSheet("background-color: #FFA500")

        self.btn_to_decode_qr_from_video = QPushButton(self)  # кнопка для декодирования qr-кода с видео
        self.btn_to_decode_qr_from_video.setGeometry(QRect(490, 520, 300, 30))
        self.btn_to_decode_qr_from_video.setText("Декодировать QR-код с видео")
        self.btn_to_decode_qr_from_video.setFont(font)
        self.btn_to_decode_qr_from_video.setStyleSheet("background-color: #FFA500")

        self.label_with_contact_information = QPlainTextEdit(self)  # окно с контактной информацией об авторе
        self.label_with_contact_information.setGeometry(550, 559, 180, 34)
        self.label_with_contact_information.insertPlainText('Github автора:')
        self.label_with_contact_information.setFont(font)
        self.label_with_contact_information.setStyleSheet("color: #FFA500; background-color: #293133")
        self.label_with_contact_information.setEnabled(False)

        self.label_for_author_git = QLabel(self)  # место для вывода qr-кода, ведущего на страницу автора на git hub
        self.label_for_author_git.setGeometry(QRect(540, 600, 200, 200))
        self.authors_git_image = QPixmap("media/git_qr_code.png")
        self.label_for_author_git.setPixmap(self.authors_git_image)

        self.btn_settings = QPushButton(self)  # кнопка для откртия диалогового окна настроек
        self.btn_settings.setGeometry(QRect(1245, 0, 35, 35))
        self.btn_settings.setText("⚙")
        s_font = QFont()
        s_font.setPointSize(20)
        s_font.setBold(True)
        s_font.setWeight(35)
        self.btn_settings.setFont(s_font)

        self.btn_to_make_qr_from_text.clicked.connect(self.getQR)  # поведение программы, при нажатии на кнопку
        self.btn_to_select_file.clicked.connect(self.getImage)  # поведение программы, при нажатии на кнопку
        self.btn_to_decode_qr_from_video.clicked.connect(self.decode_qr_text)  # поведение программы, при нажатии на кн
        self.btn_settings.clicked.connect(self.settings)  # поведение программы, при нажатии на кнопку

        th = Thread(self)  # экзмепляр класса для парралельной работы
        th.changePixmap.connect(self.setImage)  # установка изоюражения камеры
        th.start()  # начало работы класса

    @pyqtSlot(QImage)
    def setImage(self, image):
        """Установка изображения в специальное окно"""
        self.camera.setPixmap(QPixmap.fromImage(image))  # настройка

    def getImage(self):
        """Получение и сохранение изображения, выбранного пользователем"""
        global QR_TEXT
        fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '', 'PNG File (*png)')[0]  # получение имени файла
        img = cv2.imread(fname)  # чтение изоюражения
        detector = cv2.QRCodeDetector()  # экземпляр класса для декоддирования
        data, bbox, _ = detector.detectAndDecode(img)  # декодирование информации с изображения
        if data is not None:
            QR_TEXT = data  # сохранение информации с qr-кода в глобальную константу
            self.decode_qr_text()  # вызов функции для установки текста в спец поле

    def getQR(self):
        """Генерация QR-КОДА"""
        qr = qrcode.QRCode(version=SETTINGS_QR["version"], box_size=SETTINGS_QR["box_size"],
                           border=SETTINGS_QR["border"])  # создание экзмепляра класса QR кода
        qr.add_data(self.qr_text_field.toPlainText())  # добавление текста для шифрования
        qr.make()  # создание qr-кода
        img = qr.make_image(fill_color=SETTINGS_QR["fill_color"],
                            back_color=SETTINGS_QR["back_color"])  # завершающая настройка
        new_image = img.resize((300, 300))  # изменение размера изображения
        new_image.save("media/qr_code.png")  # сохранение картинки

        self.qr_image = QPixmap("media/qr_code.png")  # вывод изображения в спец место
        self.qr_image_field.setPixmap(self.qr_image)  # вывод изображения в спец место

    def decode_qr_text(self):
        """Установка текста в специальное место"""
        if QR_TEXT:
            self.qr_text_field.setText(QR_TEXT)
            self.getQR()

    def settings(self):
        """Функция для отображения окна настроек"""
        DialogSettings_inst = DialogSettings(self)
        DialogSettings_inst.show()
        DialogSettings_inst.exec()


class Thread(QThread, QMainWindow):
    changePixmap = pyqtSignal(QImage)
    detector = cv2.QRCodeDetector()

    def run(self):
        global QR_TEXT
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            data, bbox, _ = self.detector.detectAndDecode(frame)
            # проверяем, есть ли на изображении QR
            if bbox is not None:
                if data:
                    QR_TEXT = data
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(720, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)


class DialogSettings(QDialog, settings_dialog):
    def __init__(self, mainWindow):
        """Базовый конструктор класса"""
        QDialog.__init__(self)  # первичное наследование
        self.setupUi(self)  # первичная настройка
        self.mainWindow = mainWindow  # обозначение главного окна

        self.buttonBox.accepted.connect(self.accept_data)  # назначение действия для кнопки "OK"
        self.buttonBox.rejected.connect(self.reject_data)  # назначение действия для кнопки "Cancel"

    def accept_data(self):
        """Функция для обработки действия, при нажатии кнопки 'OK' """
        global SETTINGS_QR
        SETTINGS_QR = {
            "version": int(self.version_spinBox.value()),
            "fill_color": SETTINGS_QR["fill_color"],
            "back_color": SETTINGS_QR["back_color"],
            "box_size": int(self.box_size_spinBox.value()),
            "border": int(self.border_spinBox.value())
        }

    def reject_data(self):
        """Функция для обработки действия, при нажатии кнопки 'Cancel' """
        pass


def excepthook(exc_type, exc_value, exc_tb):
    """Функция для отлова ошибок"""
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("Oбнаружена ошибка !:", tb)


sys.excepthook = excepthook

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
