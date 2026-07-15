import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb

# Глобальные переменные для хранения изображения и состояния
image = None
original_image = None
canvas = None
canvas1 = None
calibration_used = False
calibration_mode = None

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

def spectral_selection_with_overlay(image_left, Li, d_left, d_right):
    HSV = rgb_to_hsv(np.array(image_left))
    H, S, V = HSV[:, :, 0], HSV[:, :, 1], HSV[:, :, 2]
    L = 650 - 333.3 * H
    mask = (L >= Li - d_left) & (L <= Li + d_right) & (S > 0)

    H0 = np.where(mask, H, 0)
    S0 = np.where(mask, S, 0)
    V0 = np.where(mask, V, 0)

    HSV_out = np.stack((H0, S0, V0), axis=-1)
    RGB_out = hsv_to_rgb(HSV_out)

    image_with_overlay = np.array(image_left)
    image_with_overlay[mask] = [255, 0, 0]

    # Построение гистограммы
    Lmin, Lmax = 380, 650
    num_bins = 100
    hist_all, bin_edges = np.histogram(L, bins=np.linspace(Lmin, Lmax, num_bins))
    hist_selected, _ = np.histogram(L[mask], bins=np.linspace(Lmin, Lmax, num_bins))

    return Image.fromarray(image_with_overlay), RGB_out, hist_all, hist_selected, bin_edges

# Функция для отображения всплывающих сообщений
def show_message(title, message):
    messagebox.showinfo(title, message)

# Функция для отображения изображения
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

# Функция для отображения результирующего изображения
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

# Функция для отображения гистограммы
def display_histogram_left(hist_all, hist_selected, bin_edges):
    global canvas

    # Очистка предыдущей диаграммы
    if canvas:
        canvas.get_tk_widget().pack_forget()

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(bin_edges[:-1], hist_all, width=(bin_edges[1] - bin_edges[0]), color='b', alpha=0.5, label='All wavelengths')
    ax.bar(bin_edges[:-1], hist_selected, width=(bin_edges[1] - bin_edges[0]), color='r', alpha=0.5, label='Selected wavelengths')
    ax.set_title("Спектрограмма распределения длин волн")
    ax.set_xlabel("Длина волны (нм)")
    ax.set_ylabel("Количество пикселей")
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side='left', fill=tk.BOTH, expand=True)
    canvas.draw()

def display_histogram_right(hist_all, hist_selected, bin_edges):
    global canvas1

    # Очистка предыдущей диаграммы
    if canvas1:
        canvas1.get_tk_widget().pack_forget()

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(bin_edges[:-1], hist_all, width=(bin_edges[1] - bin_edges[0]), color='b', alpha=0.5, label='All wavelengths')
    ax.bar(bin_edges[:-1], hist_selected, width=(bin_edges[1] - bin_edges[0]), color='r', alpha=0.5, label='Selected wavelengths')
    ax.set_title("Спектрограмма распределения длин волн")
    ax.set_xlabel("Длина волны (нм)")
    ax.set_ylabel("Количество пикселей")
    ax.legend()

    canvas1 = FigureCanvasTkAgg(fig, master=root)
    canvas1.get_tk_widget().pack(side='right', fill=tk.BOTH, expand=True)
    canvas1.draw()

# Обработчики кнопок и функций
def open_image_left():
    global image_left, original_image_left, calibration_used
    file_path_left = filedialog.askopenfilename(title="Выберите изображение 1", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])
    if file_path_left:
        img = Image.open(file_path_left)
        image_left = img
        original_image_left = img.copy()
        calibration_used = False
        display_image_left(img)

def open_image_right():
    global image_right, original_image_right, calibration_used
    file_path_right = filedialog.askopenfilename(title="Выберите изображение 2", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])
    if file_path_right:
        img = Image.open(file_path_right)
        image_right = img
        original_image_right = img.copy()
        calibration_used = False
        display_image_right(img)

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
        show_message("Внимание", "Калибровка уже была применена. Сначала сбросьте изображение!")
    else:
        show_message("Ошибка", "Сначала выберите изображение!")

    if image_right:
        if calibration_mode == "gray_world":
            image_right = gray_world_calibration(np.array(image_right))
        elif calibration_mode == "calibrate":
            image_right = calibrate_image(np.array(image_right))
        display_image_right(image_right)

def apply_selection():
    global image_left,image_right
    if image_left:
        try:
            Li = int(Li_entry.get())
            d_left = int(d_left_entry.get())
            d_right = int(d_right_entry.get())
            selected_image, _, hist_all, hist_selected, bin_edges = spectral_selection_with_overlay(image_left, Li, d_left, d_right)
            display_selected_image_left(selected_image)
            display_histogram_left(hist_all, hist_selected, bin_edges)
        except ValueError:
            show_message("Ошибка", "Введите числовые значения для Li, d_left и d_right!")
    else:
        show_message("Ошибка", "Изображение должно быть выбрано!")

    if image_right:
        try:
            Li = int(Li_entry.get())
            d_left = int(d_left_entry.get())
            d_right = int(d_right_entry.get())
            selected_image_right, _, hist_all, hist_selected, bin_edges = spectral_selection_with_overlay(image_right, Li, d_left, d_right)
            display_selected_image_right(selected_image_right)
            display_histogram_right(hist_all, hist_selected, bin_edges)
        except ValueError:
            show_message("Ошибка", "Введите числовые значения для Li, d_left и d_right!")
    else:
        show_message("Ошибка", "Изображение должно быть выбрано!")

def reset_image():
    global image_left, original_image_left, calibration_used, image_right, original_image_right
    if original_image_left:
        image_left = original_image_left.copy()
        display_image_left(image_left)
        calibration_used = False
    else:
        show_message("Ошибка", "Оригинальное изображение не найдено!")

    if original_image_right:
        image_right = original_image_right.copy()
        display_image_right(image_right)
        calibration_used = False
    else:
        show_message("Ошибка", "Оригинальное изображение не найдено!")

def select_gray_world_calibration():
    global calibration_mode
    calibration_mode = "gray_world"
    apply_calibration()

def select_spectral_calibration():
    global calibration_mode
    calibration_mode = "calibrate"
    apply_calibration()

root = tk.Tk()
root.title("Калибровка и спектральная селекция изображений")

frame_buttons = tk.Frame(root)
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

frame_image = tk.Frame(root)
frame_image.pack(pady=10)

label_left = tk.Label(frame_image, width=60, height=40, relief="solid", bd=2)
label_left.pack(side="left", padx=10)

label_right = tk.Label(frame_image, width=60, height=40, relief="solid", bd=2)
label_right.pack(side="right", padx=10)

frame_entries = tk.Frame(root)
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

accept_button = tk.Button(root, text="Принять", command=apply_selection)
accept_button.pack(pady=10)

frame_output = tk.Frame(root)
frame_output.pack(pady=10)

label_selected_left = tk.Label(frame_output, width=60, height=40, relief="solid", bd=2)
label_selected_left.pack(side="left", padx=10)

label_selected_right = tk.Label(frame_output, width=60, height=40, relief="solid", bd=2)
label_selected_right.pack(side="right", padx=10)

# Запуск приложения
root.mainloop()

