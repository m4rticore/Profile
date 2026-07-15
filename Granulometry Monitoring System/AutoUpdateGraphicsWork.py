import sys
import time
import cv2
import numpy as np
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QThread, pyqtSignal
import pyqtgraph as pg
from pyqtgraph import PlotWidget, BarGraphItem
from ultralytics import YOLO





# Коэффициент преобразования пикселей в миллиметры
PIXEL_TO_MM_RATIO = 0.1


class YOLOAnalysisThread(QThread):
    # Сигнал для передачи данных о размерах гранул и путей изображений в главный поток
    new_granule_sizes = pyqtSignal(list)  # Передаём только размеры объектов

    def __init__(self, model_path, image_paths):
        super().__init__()
        self.model = YOLO(model_path)  # Загрузка модели YOLO
        self.image_paths = image_paths
        self.running = True

    def run(self):
        while self.running:
            for image_path in self.image_paths:
                if not self.running:
                    break

                # Загружаем изображение и выполняем предсказание
                frame = cv2.imread(image_path)
                results = self.model.predict(frame, line_width=2, max_det=3000,
                                             imgsz=1440, show_labels=True, show_conf=True, show_boxes=False, stream=False,)
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
                time.sleep(5)  # Задержка в 5 секунд между обработкой изображений

    def stop(self):
        self.running = False
        self.wait()


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Настройка окна
        self.setWindowTitle("Анализ размеров гранул в реальном времени")
        self.setGeometry(0, 0, 2000, 2000)  # Размер окна 700 на 1200 пикселей
        self.setFixedSize(1000,1000)
        self.layout = QtWidgets.QVBoxLayout(self)

        # График
        self.graph_widget = PlotWidget(title="Размеры гранул")
        self.graph_widget.setLabel('left', 'Количество')
        self.graph_widget.setLabel('bottom', 'Размер гранулы (мм)')
        self.graph_widget.setYRange(0, 3000)  # Максимальное значение по Y
        self.graph_widget.setXRange(0, 10)  # Максимальный размер гранул (предположительно до 10 мм)
        self.graph_widget.setMouseEnabled(x=False, y=False)
        self.graph_widget.setAutoVisible(x=False, y=False)
        #self.graph_widget.enableAutoRange(False, None,None,None)

        self.layout.addWidget(self.graph_widget)

        # Инициализация пустого графика
        self.bar_graph_item = BarGraphItem(x=[], height=[], width=0.4, brush="b")
        self.graph_widget.addItem(self.bar_graph_item)

        # Метка статуса
        self.label = QtWidgets.QLabel("Обработка изображений...")
        self.layout.addWidget(self.label)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Убрать отступы
        # Массив изображений
        self.image_paths = ["Cam_IMG/1.bmp", "Cam_IMG/2.bmp", "Cam_IMG/3.bmp", "Cam_IMG/4.bmp", "Cam_IMG/5.bmp", "Cam_IMG/6.bmp"]

        # Запуск потока обработки
        self.thread = YOLOAnalysisThread("AiModules/grana.pt", self.image_paths)
        self.thread.new_granule_sizes.connect(self.update_ui)
        self.thread.start()

    def update_ui(self, granule_sizes):
        counts, bins = np.histogram(granule_sizes, bins=np.arange(0, 10, 0.5))  # Бины по 0.5 мм
        x_values = (bins[:-1] + bins[1:]) / 2  # Центры столбцов
        self.bar_graph_item.setOpts(x=x_values, height=counts)


        # Обновляем текстовый статус
        self.label.setText(f"Обновлены размеры объектов: {granule_sizes}")
        print(f"Обновлены размеры объектов: {granule_sizes}")

    def closeEvent(self, event):
        # Завершаем поток при закрытии приложения
        self.thread.stop()
        event.accept()



app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())