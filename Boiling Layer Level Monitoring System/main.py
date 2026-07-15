import PySimpleGUI as sg
import cv2
import numpy as np
import time
import pandas as pd
from threading import Thread
from pygame import mixer

def main():
    # Входные переменные
    Archive = r"lvl.xlsx"
    static_back = None
    font = cv2.FONT_HERSHEY_SIMPLEX
    x = 0
    y = 0
    list_time = []
    list_level = []
    labels_bar = cv2.imread('bar.png')
    st = int(time.time())
    alarm = False
    pos_y = 165

    # Графический интерфейс
    sg.theme('DarkBlue')

    layout = [[sg.Text('Уровнемер (v0.3.0)', size=(40, 1), justification='center', font='Helvetica 20')],
              [sg.Image(filename='', key='image1'), sg.Image(filename='', key='image2'),
               sg.Slider((80,90),89,orientation='v', key='-SLIDER-')],
              [sg.Button('Разность', size=(10, 1), font='Any 14'),
               sg.Button('Архив', size=(10, 1), font='Any 14'),
               sg.Button('Обновить', size=(10, 1), font='Any 14'),
               sg.Button('СТОП', size=(10, 1), font='Any 14')],
               [sg.Button('Выход', size=(10, 1), font='Helvetica 14'), ]]

    window = sg.Window('Уровнемер (v0.3.0)', layout, location=(800, 400))

    cap = cv2.VideoCapture(0)
    recording_cam = True
    recording_diff = False
    recording_bar = True
    mixer.init()
    sound = mixer.Sound("beep.mp3")

    while True:
        # Инициализация камеры
        ret, frame = cap.read()
        event, values = window.read(timeout=1)

        value = int(values['-SLIDER-'])

        pos_y = 550 - (value-80)*50


        frame = cv2.resize(frame, [1280, 720], interpolation=cv2.INTER_LINEAR)

        motion = 0

        # Перевод в цветовое пространство LAB и выравнивание гистрограммы в L-канале

        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l_channel, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l_channel)

        limg = cv2.merge((cl, a, b))

        # Перевод в цветовое пространство RGB
        enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        frame = enhanced_img

        # Сглаживание
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if static_back is None:
            static_back = gray
            continue

        # Блок нахождения разницы кадров
        diff_frame = cv2.absdiff(static_back, gray)

        # Бинаризация
        thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
        
        # Блок морфологической обработки
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

        # Построение контуров
        cnts, _ = cv2.findContours(thresh_frame.copy(),
                                   cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Выделение контуров
        for contour in cnts:
            if cv2.contourArea(contour) < 100:
                continue
            motion = 1
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        # Нахождение координат верхней границы
        if motion == 1:
            cord_y = y + 50
            if cord_y == 50:
                cord_y = 700
        else:
            cord_y = 700

        # Расчет уровня
        lvl = 90 - round((cord_y * 10) / 650)
        lvl_str = str(lvl)

        # Визуальное отображение уровня
        if lvl >= value:
            lvl_str = '>89'
            cv2.rectangle(frame,(10,10),(1280,720),(0, 0, 255), 20)
            en = int(time.time())

            if (en - st) == 10:
                alarm = True;
        elif lvl_str == '80' or lvl_str == '79':
            lvl_str = '<80'
            cv2.rectangle(frame, (0, 0), (1280, 720), (255, 0, 0), 3)
            st = int(time.time())
            alarm = False
        else:
            alarm = False
            st = int(time.time())

        labels_bar = cv2.imread('bar.png', 1)
        cv2.rectangle(labels_bar, (100, 50), (200, 700), (0, 0, 255), 2)
        cv2.rectangle(labels_bar, (100, cord_y), (200, 700), (0, 0, 255), -1)
        cv2.putText(labels_bar, lvl_str, (220, 725), font, 1, (0, 0, 0), 2, cv2.LINE_AA)

        # Расчет актуального времени для записи в .xls
        loc = time.localtime()
        hour = str(loc.tm_hour)
        minut = str(loc.tm_min)
        sec = str(loc.tm_sec)
        times = hour + ':' + minut + ':' + sec

        year = str(loc.tm_year)
        month = str(loc.tm_mon)
        day = str(loc.tm_mday)
        dates = day + '.' + month + '.' + year

        # запись в таблицу
        if loc.tm_sec % 10 == 0:
            if lvl_str == '>89':
                list_time.append(times + '        ' + dates)
                list_level.append(lvl_str)
                time.sleep(1)       #избавиться
            elif lvl_str != '<80' and lvl_str != '>89':
                list_time.append(times + '        ' + dates)
                list_level.append(lvl_str)
                time.sleep(1)
            static_back = gray

        def append_df_to_excel(df, excel_path):
            df_excel = pd.read_excel(excel_path)
            result = pd.concat([df_excel, df], ignore_index=True)
            result.to_excel(excel_path, sheet_name='name_of_cam', index=False)

        df = pd.DataFrame({'Time': list_time,
                           'Level': list_level})

        # Привязка кнопок
        if event == 'Выход' or event == sg.WIN_CLOSED:
            return
        
        if event == 'СТОП':
            alarm == False
            sound.stop()
            
        elif event == 'Разность':
            if recording_cam == True:
                recording_cam = False
                recording_diff = True
            else:
                recording_cam = True
                recording_diff = False

        elif event == 'Обновить':
            static_back = gray

        elif event == 'Архив':
            append_df_to_excel(df, r"lvl.xlsx")
            sg.execute_command_subprocess(Archive)

        if recording_cam:
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
            window['image1'].update(data=imgbytes)

        if recording_diff:
            imgbytes = cv2.imencode('.png', thresh_frame)[1].tobytes()  # ditto
            window['image1'].update(data=imgbytes)

        if recording_bar:
            imgbytes = cv2.imencode('.png', labels_bar)[1].tobytes()  # ditto
            window['image2'].update(data=imgbytes)

        if alarm:
            sound.play()

main()
