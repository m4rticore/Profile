#CUDA подключить + разобраться с результатом выполнения




import cv2
import onnxruntime as ort
import numpy as np

# Загрузите YOLO
session = ort.InferenceSession("AiModules/grana.onnx")

# Загрузите изображение
img_path = 'Images/2.jpg'
frame = cv2.imread(img_path)

# Выполните предсказание
outputs = session.run(['None.jpg'], {img_path})

# Преобразуйте результат для отображения в OpenCV
for result in results:
    boxes = result.boxes.xyxy.cpu().numpy()  # Получаем координаты боксов (в формате x1, y1, x2, y2)
    confidences = result.boxes.conf.cpu().numpy()  # Получаем уверенность для каждого бокса
    class_ids = result.boxes.cls.cpu().numpy().astype(int)  # Индексы классов объектов

    # Используем стандартные классы COCO или ваш собственный список классов
    classes = model.names  # или свой список меток, если они отличаются

    # Рисуем каждый бокс на изображении
    for i, (box, confidence, class_id) in enumerate(zip(boxes, confidences, class_ids)):
        x1, y1, x2, y2 = map(int, box)
        label = f"{classes[class_id]} {confidence:.2f}"

        # Рисуем прямоугольник и добавляем текст
        color = (0, 255, 0)  # Зеленый цвет для боксов
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
        #cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

# Покажем изображение через OpenCV
while True:
    cv2.imshow("YOLO Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()