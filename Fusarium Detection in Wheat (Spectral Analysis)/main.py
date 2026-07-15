import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
import pandas as pd
import os
from datetime import datetime
import json

# Глобальные переменные для хранения изображения и состояния
image_left = None
image_right = None
original_image_left = None
original_image_right = None
canvas = None
canvas1 = None
calibration_used = False
calibration_mode = None
results_data = []


# Функция для калибровки изображения
def calibrate_image(image_left):
    image_left = cv2.cvtColor(image_left, cv2.COLOR_RGB2BGR)
    top = int(image_left.shape[0] * image_left.shape[1] * 0.01)
    b, g, r = cv2.split(image_left)
    rgbmax = [0, 0, 0]
    for i in range(3):
        hist, _ = np.histogram(cv2.split(image_left)[i].flatten(), 256, [0, 256])
        l = 255
        total = 0
        while total < top:
            l -= 1
            total += hist[l]
        rgbmax[i] = l
    b = (b / rgbmax[0] * 255).clip(0, 255).astype(np.uint8)
    g = (g / rgbmax[1] * 255).clip(0, 255).astype(np.uint8)
    r = (r / rgbmax[2] * 255).clip(0, 255).astype(np.uint8)
    image_left = cv2.merge([b, g, r])
    image_left = cv2.cvtColor(image_left, cv2.COLOR_BGR2RGB)
    return Image.fromarray(image_left)


# Функция для калибровки серый мир
def gray_world_calibration(image_left):
    image_left = cv2.cvtColor(np.array(image_left), cv2.COLOR_RGB2BGR)
    R, G, B = cv2.split(image_left)
    mR, mG, mB = np.mean(R), np.mean(G), np.mean(B)
    K = (mR + mG + mB) / 3
    R = cv2.multiply(R, K / mR)
    G = cv2.multiply(G, K / mG)
    B = cv2.multiply(B, K / mB)
    image_left = cv2.merge([B, G, R])
    image_left = cv2.cvtColor(image_left, cv2.COLOR_BGR2RGB)
    return Image.fromarray(image_left)


# Функция для спектральной селекции
def spectral_selection_with_overlay(image_left, Li, d_left, d_right, sensitivity=1.0):
    rgb_array = np.asarray(image_left, dtype=np.float32) / 255.0
    HSV = rgb_to_hsv(rgb_array)
    H, S, V = HSV[..., 0], HSV[..., 1], HSV[..., 2]

    L = 650 - 333.3 * H
    mask = (L >= Li - d_left) & (L <= Li + d_right) & (S > 0.1 * sensitivity)

    # Расчет статистики
    total_pixels = np.prod(mask.shape)
    infected_pixels = np.sum(mask)
    infection_percentage = (infected_pixels / total_pixels) * 100

    # Создаем изображение с наложением
    image_with_overlay = np.array(image_left)
    image_with_overlay[mask] = [255, 0, 0]  # Красный для зараженных областей

    # Построение гистограммы
    Lmin, Lmax = 380, 650
    num_bins = 100
    hist_all, bin_edges = np.histogram(L, bins=np.linspace(Lmin, Lmax, num_bins))
    hist_selected, _ = np.histogram(L[mask], bins=np.linspace(Lmin, Lmax, num_bins))

    return Image.fromarray(
        image_with_overlay), None, hist_all, hist_selected, bin_edges, infection_percentage, infected_pixels, total_pixels


# Функция для пакетной обработки
def batch_process():
    folder_path = filedialog.askdirectory(title="Выберите папку с изображениями")
    if not folder_path:
        return

    # Создаем папку для результатов
    results_folder = os.path.join(folder_path, f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(results_folder, exist_ok=True)

    # Параметры обработки
    Li = int(Li_entry.get())
    d_left = int(d_left_entry.get())
    d_right = int(d_right_entry.get())
    sensitivity = sensitivity_scale.get()

    results = []
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]

    progress_bar['maximum'] = len(image_files)

    for i, filename in enumerate(image_files):
        try:
            # Обновление прогресса
            progress_bar['value'] = i + 1
            root.update_idletasks()

            # Загрузка и обработка изображения
            file_path = os.path.join(folder_path, filename)
            img = Image.open(file_path)

            # Применение калибровки
            if calibration_mode == "gray_world":
                img_calibrated = gray_world_calibration(np.array(img))
            else:
                img_calibrated = calibrate_image(np.array(img))

            # Спектральная селекция
            selected_img, _, hist_all, hist_selected, bin_edges, infection_perc, infected_pix, total_pix = spectral_selection_with_overlay(
                img_calibrated, Li, d_left, d_right, sensitivity)

            # Сохранение результатов
            result_filename = f"processed_{filename}"
            selected_img.save(os.path.join(results_folder, result_filename))

            # Сохранение гистограммы
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(bin_edges[:-1], hist_all, width=(bin_edges[1] - bin_edges[0]), color='b', alpha=0.5,
                   label='Все длины волн')
            ax.bar(bin_edges[:-1], hist_selected, width=(bin_edges[1] - bin_edges[0]), color='r', alpha=0.5,
                   label='Выбранные длины волн')
            ax.set_title("Спектрограмма распределения длин волн")
            ax.set_xlabel("Длина волны (нм)")
            ax.set_ylabel("Количество пикселей")
            ax.legend()
            plt.savefig(os.path.join(results_folder, f"histogram_{os.path.splitext(filename)[0]}.png"))
            plt.close()

            # Добавление в результаты
            results.append({
                'filename': filename,
                'infection_percentage': infection_perc,
                'infected_pixels': infected_pix,
                'total_pixels': total_pix,
                'processing_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'parameters': f'Li={Li}, d_left={d_left}, d_right={d_right}, sensitivity={sensitivity}'
            })

        except Exception as e:
            print(f"Ошибка обработки {filename}: {str(e)}")

    # Сохранение сводного отчета
    df = pd.DataFrame(results)
    df.to_csv(os.path.join(results_folder, 'summary_report.csv'), index=False, encoding='utf-8')

    # Сохранение параметров
    params = {
        'Li': Li,
        'd_left': d_left,
        'd_right': d_right,
        'sensitivity': sensitivity,
        'calibration_mode': calibration_mode,
        'processing_date': datetime.now().isoformat(),
        'total_images_processed': len(results)
    }

    with open(os.path.join(results_folder, 'processing_parameters.json'), 'w') as f:
        json.dump(params, f, indent=2)

    messagebox.showinfo("Пакетная обработка завершена",
                        f"Обработано {len(results)} изображений.\nРезультаты сохранены в: {results_folder}")


# Функция для сохранения результатов
def save_results():
    if not results_data:
        messagebox.showwarning("Внимание", "Нет данных для сохранения!")
        return

    file_path = filedialog.asksaveasfilename(
        title="Сохранить отчет",
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
    )

    if file_path:
        df = pd.DataFrame(results_data)
        if file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        else:
            df.to_csv(file_path, index=False, encoding='utf-8')
        messagebox.showinfo("Сохранение", "Отчет успешно сохранен!")


# Функция для генерации отчета
def generate_report():
    if not results_data:
        messagebox.showwarning("Внимание", "Нет данных для отчета!")
        return

    report_window = tk.Toplevel(root)
    report_window.title("Сводный отчет")
    report_window.geometry("600x400")

    text_widget = tk.Text(report_window, wrap=tk.WORD)
    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Формирование отчета
    report_text = "СВОДНЫЙ ОТЧЕТ АНАЛИЗА ПОСЕВОВ\n"
    report_text += "=" * 50 + "\n\n"

    total_infection = sum(item['infection_percentage'] for item in results_data)
    avg_infection = total_infection / len(results_data) if results_data else 0

    report_text += f"Общее количество анализов: {len(results_data)}\n"
    report_text += f"Средний процент заражения: {avg_infection:.2f}%\n"
    report_text += f"Максимальный процент заражения: {max(item['infection_percentage'] for item in results_data):.2f}%\n"
    report_text += f"Минимальный процент заражения: {min(item['infection_percentage'] for item in results_data):.2f}%\n\n"

    report_text += "ДЕТАЛИЗИРОВАННЫЕ ДАННЫЕ:\n"
    report_text += "-" * 50 + "\n"

    for i, item in enumerate(results_data, 1):
        report_text += f"{i}. {item.get('filename', 'Изображение')}: {item['infection_percentage']:.2f}% заражения\n"

    text_widget.insert(tk.END, report_text)

    # Кнопка сохранения отчета
    save_btn = tk.Button(report_window, text="Сохранить отчет", command=save_results)
    save_btn.pack(pady=10)


# Функции отображения изображений (остаются без изменений)
def display_image_left(image_left):
    label_width, label_height = 640, 480
    img_width, img_height = image_left.size
    aspect_ratio = img_width / img_height
    if img_width > label_width or img_height > label_height:
        if aspect_ratio > 1:
            new_width = label_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = label_height
            new_width = int(new_height * aspect_ratio)
    else:
        new_width, new_height = img_width, img_height
    image_left = image_left.resize((new_width, new_height), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(image_left)
    label_left.config(image=img_tk, width=label_width, height=label_height)
    label_left.image = img_tk


def display_image_right(image_right):
    label_width, label_height = 640, 480
    img_width, img_height = image_right.size
    aspect_ratio = img_width / img_height
    if img_width > label_width or img_height > label_height:
        if aspect_ratio > 1:
            new_width = label_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = label_height
            new_width = int(new_height * aspect_ratio)
    else:
        new_width, new_height = img_width, img_height
    image_right = image_right.resize((new_width, new_height), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(image_right)
    label_right.config(image=img_tk, width=label_width, height=label_height)
    label_right.image = img_tk


def display_selected_image_left(image_left):
    label_selected_width, label_selected_height = 640, 480
    img_width, img_height = image_left.size
    aspect_ratio = img_width / img_height
    if img_width > label_selected_width or img_height > label_selected_height:
        if aspect_ratio > 1:
            new_width = label_selected_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = label_selected_height
            new_width = int(new_height * aspect_ratio)
    else:
        new_width, new_height = img_width, img_height
    image_left = image_left.resize((new_width, new_height), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(image_left)
    label_selected_left.config(image=img_tk, width=label_selected_width, height=label_selected_height)
    label_selected_left.image = img_tk


def display_selected_image_right(image_right):
    label_selected_width, label_selected_height = 640, 480
    img_width, img_height = image_right.size
    aspect_ratio = img_width / img_height
    if img_width > label_selected_width or img_height > label_selected_height:
        if aspect_ratio > 1:
            new_width = label_selected_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = label_selected_height
            new_width = int(new_height * aspect_ratio)
    else:
        new_width, new_height = img_width, img_height
    image_right = image_right.resize((new_width, new_height), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(image_right)
    label_selected_right.config(image=img_tk, width=label_selected_width, height=label_selected_height)
    label_selected_right.image = img_tk


# Функции для гистограмм (остаются без изменений)
def display_histogram_left(hist_all, hist_selected, bin_edges):
    global canvas
    if canvas:
        canvas.get_tk_widget().pack_forget()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(bin_edges[:-1], hist_all, width=(bin_edges[1] - bin_edges[0]), color='b', alpha=0.5, label='Все длины волн')
    ax.bar(bin_edges[:-1], hist_selected, width=(bin_edges[1] - bin_edges[0]), color='r', alpha=0.5,
           label='Выбранные длины волн')
    ax.set_title("Спектрограмма распределения длин волн")
    ax.set_xlabel("Длина волны (нм)")
    ax.set_ylabel("Количество пикселей")
    ax.legend()
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side='left', fill=tk.BOTH, expand=True)
    canvas.draw()


def display_histogram_right(hist_all, hist_selected, bin_edges):
    global canvas1
    if canvas1:
        canvas1.get_tk_widget().pack_forget()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(bin_edges[:-1], hist_all, width=(bin_edges[1] - bin_edges[0]), color='b', alpha=0.5, label='Все длины волн')
    ax.bar(bin_edges[:-1], hist_selected, width=(bin_edges[1] - bin_edges[0]), color='r', alpha=0.5,
           label='Выбранные длины волн')
    ax.set_title("Спектрограмма распределения длин волн")
    ax.set_xlabel("Длина волны (нм)")
    ax.set_ylabel("Количество пикселей")
    ax.legend()
    canvas1 = FigureCanvasTkAgg(fig, master=root)
    canvas1.get_tk_widget().pack(side='right', fill=tk.BOTH, expand=True)
    canvas1.draw()


# Обработчики кнопок с добавлением функциональности
def open_image_left():
    global image_left, original_image_left, calibration_used
    file_path_left = filedialog.askopenfilename(title="Выберите изображение 1",
                                                filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])
    if file_path_left:
        img = Image.open(file_path_left)
        image_left = img
        original_image_left = img.copy()
        calibration_used = False
        display_image_left(img)
        # Сохраняем имя файла для отчета
        global current_filename_left
        current_filename_left = os.path.basename(file_path_left)


def open_image_right():
    global image_right, original_image_right, calibration_used
    file_path_right = filedialog.askopenfilename(title="Выберите изображение 2",
                                                 filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])
    if file_path_right:
        img = Image.open(file_path_right)
        image_right = img
        original_image_right = img.copy()
        calibration_used = False
        display_image_right(img)
        # Сохраняем имя файла для отчета
        global current_filename_right
        current_filename_right = os.path.basename(file_path_right)


def apply_calibration():
    global calibration_mode, image_left, image_right, calibration_used
    if image_left and not calibration_used:
        if calibration_mode == "gray_world":
            image_left = gray_world_calibration(np.array(image_left))
        elif calibration_mode == "calibrate":
            image_left = calibrate_image(np.array(image_left))
        display_image_left(image_left)
        calibration_used = True
    elif calibration_used:
        messagebox.showwarning("Внимание", "Калибровка уже была применена. Сначала сбросьте изображение!")
    else:
        messagebox.showerror("Ошибка", "Сначала выберите изображение!")

    if image_right:
        if calibration_mode == "gray_world":
            image_right = gray_world_calibration(np.array(image_right))
        elif calibration_mode == "calibrate":
            image_right = calibrate_image(np.array(image_right))
        display_image_right(image_right)


def apply_selection():
    global image_left, image_right, results_data
    sensitivity = sensitivity_scale.get()

    if image_left:
        try:
            Li = int(Li_entry.get())
            d_left = int(d_left_entry.get())
            d_right = int(d_right_entry.get())
            selected_image, _, hist_all, hist_selected, bin_edges, infection_perc, infected_pix, total_pix = spectral_selection_with_overlay(
                image_left, Li, d_left, d_right, sensitivity)
            display_selected_image_left(selected_image)
            display_histogram_left(hist_all, hist_selected, bin_edges)

            # Сохранение результатов для отчета
            results_data.append({
                'filename': getattr(current_filename_left, 'current_filename_left', 'Изображение 1'),
                'infection_percentage': infection_perc,
                'infected_pixels': infected_pix,
                'total_pixels': total_pix,
                'processing_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'parameters': f'Li={Li}, d_left={d_left}, d_right={d_right}, sensitivity={sensitivity}'
            })

            # Показать статистику
            stats_label_left.config(text=f"Заражение: {infection_perc:.2f}% ({infected_pix}/{total_pix} пикселей)")

        except ValueError:
            messagebox.showerror("Ошибка", "Введите числовые значения для Li, d_left и d_right!")
    else:
        messagebox.showerror("Ошибка", "Изображение должно быть выбрано!")

    if image_right:
        try:
            Li = int(Li_entry.get())
            d_left = int(d_left_entry.get())
            d_right = int(d_right_entry.get())
            selected_image_right, _, hist_all, hist_selected, bin_edges, infection_perc, infected_pix, total_pix = spectral_selection_with_overlay(
                image_right, Li, d_left, d_right, sensitivity)
            display_selected_image_right(selected_image_right)
            display_histogram_right(hist_all, hist_selected, bin_edges)

            # Сохранение результатов для отчета
            results_data.append({
                'filename': getattr(current_filename_right, 'current_filename_right', 'Изображение 2'),
                'infection_percentage': infection_perc,
                'infected_pixels': infected_pix,
                'total_pixels': total_pix,
                'processing_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'parameters': f'Li={Li}, d_left={d_left}, d_right={d_right}, sensitivity={sensitivity}'
            })

            # Показать статистику
            stats_label_right.config(text=f"Заражение: {infection_perc:.2f}% ({infected_pix}/{total_pix} пикселей)")

        except ValueError:
            messagebox.showerror("Ошибка", "Введите числовые значения для Li, d_left и d_right!")
    else:
        messagebox.showerror("Ошибка", "Изображение должно быть выбрано!")


def reset_image():
    global image_left, original_image_left, calibration_used, image_right, original_image_right
    if original_image_left:
        image_left = original_image_left.copy()
        display_image_left(image_left)
        calibration_used = False
        stats_label_left.config(text="")
    else:
        messagebox.showerror("Ошибка", "Оригинальное изображение не найдено!")

    if original_image_right:
        image_right = original_image_right.copy()
        display_image_right(image_right)
        calibration_used = False
        stats_label_right.config(text="")
    else:
        messagebox.showerror("Ошибка", "Оригинальное изображение не найдено!")


def select_gray_world_calibration():
    global calibration_mode
    calibration_mode = "gray_world"
    apply_calibration()


def select_spectral_calibration():
    global calibration_mode
    calibration_mode = "calibrate"
    apply_calibration()


def on_closing():
    if messagebox.askokcancel("Выход", "Вы действительно хотите выйти?"):
        root.destroy()


# Создание главного окна
root = tk.Tk()
root.title("Псевдоспектральный мониторинг посевов - Заключительная версия")
root.geometry("1400x900")

# Создание вкладок
tab_control = ttk.Notebook(root)

# Вкладка индивидуальной обработки
tab_individual = ttk.Frame(tab_control)
tab_control.add(tab_individual, text='Индивидуальная обработка')

# Вкладка пакетной обработки
tab_batch = ttk.Frame(tab_control)
tab_control.add(tab_batch, text='Пакетная обработка')

tab_control.pack(expand=1, fill='both')

# Содержимое вкладки индивидуальной обработки
frame_buttons = tk.Frame(tab_individual)
frame_buttons.pack(pady=10)

select_button_left = tk.Button(frame_buttons, text="Выбрать изображение 1", command=open_image_left)
select_button_left.pack(side="left", padx=20)

select_button_right = tk.Button(frame_buttons, text="Выбрать изображение 2", command=open_image_right)
select_button_right.pack(side="left", padx=20)

gray_world_button = tk.Button(frame_buttons, text="Калибровка серый мир", command=select_gray_world_calibration)
gray_world_button.pack(side="left", padx=5)

calibrate_button = tk.Button(frame_buttons, text="Калибровка", command=select_spectral_calibration)
calibrate_button.pack(side="left", padx=5)

reset_button = tk.Button(frame_buttons, text="Сбросить к оригинальному", command=reset_image)
reset_button.pack(side="left", padx=5)

report_button = tk.Button(frame_buttons, text="Сгенерировать отчет", command=generate_report)
report_button.pack(side="left", padx=5)

save_button = tk.Button(frame_buttons, text="Сохранить результаты", command=save_results)
save_button.pack(side="left", padx=5)

frame_image = tk.Frame(tab_individual)
frame_image.pack(pady=10)

label_left = tk.Label(frame_image, width=60, height=40, relief="solid", bd=2)
label_left.pack(side="left", padx=10)

label_right = tk.Label(frame_image, width=60, height=40, relief="solid", bd=2)
label_right.pack(side="right", padx=10)

# Фрейм для статистики
stats_frame = tk.Frame(tab_individual)
stats_frame.pack(pady=5)

stats_label_left = tk.Label(stats_frame, text="", fg="red", font=("Arial", 10))
stats_label_left.pack(side="left", padx=150)

stats_label_right = tk.Label(stats_frame, text="", fg="red", font=("Arial", 10))
stats_label_right.pack(side="right", padx=150)

frame_entries = tk.Frame(tab_individual)
frame_entries.pack(pady=10)

tk.Label(frame_entries, text="Левое значение (d_left)").pack(side="left")
d_left_entry = tk.Entry(frame_entries, width=5)
d_left_entry.pack(side="left", padx=5)
d_left_entry.insert(0, "10")

tk.Label(frame_entries, text="Среднее значение (Li)").pack(side="left")
Li_entry = tk.Entry(frame_entries, width=5)
Li_entry.pack(side="left", padx=5)
Li_entry.insert(0, "630")

tk.Label(frame_entries, text="Правое значение (d_right)").pack(side="left")
d_right_entry = tk.Entry(frame_entries, width=5)
d_right_entry.pack(side="left", padx=5)
d_right_entry.insert(0, "10")

# Шкала чувствительности
tk.Label(frame_entries, text="Чувствительность:").pack(side="left", padx=(20, 5))
sensitivity_scale = tk.Scale(frame_entries, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, length=150)
sensitivity_scale.set(1.0)
sensitivity_scale.pack(side="left", padx=5)

accept_button = tk.Button(tab_individual, text="Применить анализ", command=apply_selection)
accept_button.pack(pady=10)

frame_output = tk.Frame(tab_individual)
frame_output.pack(pady=10)

label_selected_left = tk.Label(frame_output, width=60, height=40, relief="solid", bd=2)
label_selected_left.pack(side="left", padx=10)

label_selected_right = tk.Label(frame_output, width=60, height=40, relief="solid", bd=2)
label_selected_right.pack(side="right", padx=10)

# Содержимое вкладки пакетной обработки
batch_frame = tk.Frame(tab_batch)
batch_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

tk.Label(batch_frame, text="ПАКЕТНАЯ ОБРАБОТКА ИЗОБРАЖЕНИЙ", font=("Arial", 14, "bold")).pack(pady=10)

# Параметры для пакетной обработки
params_frame = tk.Frame(batch_frame)
params_frame.pack(pady=10)

tk.Label(params_frame, text="Параметры анализа:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=4,
                                                                                   pady=5)

tk.Label(params_frame, text="Li:").grid(row=1, column=0, padx=5)
batch_Li_entry = tk.Entry(params_frame, width=8)
batch_Li_entry.grid(row=1, column=1, padx=5)
batch_Li_entry.insert(0, "630")

tk.Label(params_frame, text="d_left:").grid(row=1, column=2, padx=5)
batch_d_left_entry = tk.Entry(params_frame, width=8)
batch_d_left_entry.grid(row=1, column=3, padx=5)
batch_d_left_entry.insert(0, "10")

tk.Label(params_frame, text="d_right:").grid(row=1, column=4, padx=5)
batch_d_right_entry = tk.Entry(params_frame, width=8)
batch_d_right_entry.grid(row=1, column=5, padx=5)
batch_d_right_entry.insert(0, "10")

tk.Label(params_frame, text="Чувствительность:").grid(row=2, column=0, padx=5, pady=10)
batch_sensitivity_scale = tk.Scale(params_frame, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, length=150)
batch_sensitivity_scale.set(1.0)
batch_sensitivity_scale.grid(row=2, column=1, columnspan=3, padx=5, pady=10)

# Кнопка запуска пакетной обработки
batch_button = tk.Button(batch_frame, text="Запустить пакетную обработку", command=batch_process,
                         bg="lightblue", font=("Arial", 12), height=2)
batch_button.pack(pady=20)

# Прогресс-бар
progress_bar = ttk.Progressbar(batch_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
progress_bar.pack(pady=10)

# Информация о пакетной обработке
info_text = tk.Text(batch_frame, height=8, width=80)
info_text.pack(pady=10, fill=tk.BOTH, expand=True)
info_text.insert(tk.END, "ИНФОРМАЦИЯ О ПАКЕТНОЙ ОБРАБОТКЕ:\n\n")
info_text.insert(tk.END, "• Выберите папку с изображениями для обработки\n")
info_text.insert(tk.END, "• Установите параметры анализа\n")
info_text.insert(tk.END, "• Нажмите кнопку 'Запустить пакетную обработку'\n")
info_text.insert(tk.END, "• Результаты будут сохранены в подпапке 'results_дата_время'\n")
info_text.insert(tk.END, "• Будут созданы: обработанные изображения, гистограммы и сводный отчет\n")
info_text.config(state=tk.DISABLED)

root.protocol("WM_DELETE_WINDOW", on_closing)

# Запуск приложения
root.mainloop()
os._exit()
