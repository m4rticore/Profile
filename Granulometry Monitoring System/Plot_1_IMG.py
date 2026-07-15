import sys
import cv2
import numpy as np
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QThread, pyqtSignal
from pyqtgraph import PlotWidget, BarGraphItem
from ultralytics import YOLO
import pyqtgraph as pg
import random

# Коэффициент преобразования пикселей в миллиметры
PIXEL_TO_MM_RATIO = 0.1


class YOLOAnalysisThread(QThread):
    # Сигнал для передачи данных о размерах гранул в главный поток
    new_granule_sizes = pyqtSignal(list)

    def __init__(self, model_path, image_path):
        super().__init__()
        self.model = YOLO(model_path)
        self.image_path = image_path

    def run(self):
        # Загружаем изображение и выполняем предсказание
        frame = cv2.imread(self.image_path)
        results = self.model.predict(frame, line_width=2, max_det=3000,
                                     imgsz=1440, show_labels=True, show_conf=True, show_boxes=True, stream=False, )

        granule_sizes_mm = []

        # Обработка результатов
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()  # Координаты боксов (x1, y1, x2, y2)
            # Расчет размера гранул и перевод их в мм
            for box in boxes:
                x1, y1, x2, y2 = box
                width_px = x2 - x1  # Ширина в пикселях
                height_px = y2 - y1  # Высота в пикселях
                size_px = (width_px + height_px) / 2  # Средний размер в пикселях

                size_mm = size_px * PIXEL_TO_MM_RATIO  # Преобразование в миллиметры
                granule_sizes_mm.append(size_mm)  # Добавление размера гранулы в мм

        # Отправка данных в основной поток
        self.new_granule_sizes.emit(granule_sizes_mm)


class HistogramWidget(PlotWidget):
    def __init__(self):
        super().__init__()

        # Настройка гистограммы
        self.setWindowTitle("Распределение размеров гранул")
        self.setLabel("left", "Количество")
        self.setLabel("bottom", "Размер гранулы (мм)")
        self.setYRange(0, 600)  # Максимальное значение по Y
        self.setXRange(0, 10)  # Максимальный размер гранул (предположительно до 10 мм)
        self.setMouseEnabled(x=False, y=False)  # Отключаем перемещение мышью
        self.enableAutoRange(True, True,True,True)
        # Инициализация BarGraphItem для гистограммы
        self.bars = None

    def update_histogram(self, sizes):
        # Построение гистограммы с разбивкой на интервалы
        counts, bins = np.histogram(sizes, bins=np.arange(0, 10, 0.5))  # Бины по 0.5 мм
        x_values = (bins[:-1] + bins[1:]) / 2  # Центры столбцов
        # Если график уже создан, обновляем его, иначе создаем новый
        if self.bars:
            self.bars.setOpts(x=x_values, height=counts)
        else:
            self.bars = BarGraphItem(x=x_values, height=counts, width=0.4, brush='b')
            self.addItem(self.bars)



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Настройка основного окна
        self.setWindowTitle("Анализ размеров гранул в реальном времени")
        self.setGeometry(100, 100, 1200, 700)  # Размер окна 700 на 1200 пикселей

        # Создаем и добавляем виджет гистограммы
        self.histogram_widget = HistogramWidget()
        self.setCentralWidget(self.histogram_widget)

        # Создаем поток для анализа изображения с YOLO
        model_path = "AiModules/grana.pt"
        image_path = "Cam_IMG/Pic_2024_11_22_115609_2.bmp"
        self.analysis_thread = YOLOAnalysisThread(model_path, image_path)

        # Подключаем сигнал для обновления гистограммы
        self.analysis_thread.new_granule_sizes.connect(self.histogram_widget.update_histogram)
        # Запускаем поток анализа
        self.analysis_thread.start()

    def closeEvent(self, event):
        # Остановка потока при закрытии приложения
        self.analysis_thread.terminate()
        event.accept()


# Запуск приложения
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())