import numpy as np
import mss
import time
import json
import pyautogui
import cv2

# Определим целевой цвет в RGB
target_color_rgb = np.uint8([[[226, 62, 75]]])

# Определим диапазон для целевого цвета в HSV
hue = target_color_rgb[0][0][0]
tolerance = 10  # Задаем погрешность в пределах 10 оттенков
lower_bound = np.array([hue - tolerance, 100, 100])
upper_bound = np.array([hue + tolerance, 255, 255])

# Прочитаем координаты окна из файла
with open('window_coordinates.json', 'r') as file:
    coordinates = json.load(file)

# Определим область захвата
monitor = {"top": coordinates["top_left"]["y"], "left": coordinates["top_left"]["x"],
           "width": coordinates["bottom_right"]["x"] - coordinates["top_left"]["x"],
           "height": coordinates["bottom_right"]["y"] - coordinates["top_left"]["y"]}

# Получим размеры экрана
screen_width, screen_height = pyautogui.size()

# Настроим скорость перемещения курсора
move_speed = 0.9

# Настроим гладкость перемещения
smoothness = 5

def smooth_move(start, end, steps):
    """
    Плавно перемещает курсор мыши от начальной точки до конечной точки.

    Args:
        start (tuple): Начальные координаты (x, y).
        end (tuple): Конечные координаты (x, y).
        steps (int): Количество шагов для плавного перемещения.
    """
    x_start, y_start = start
    x_end, y_end = end
    x_step = (x_end - x_start) / steps
    y_step = (y_end - y_start) / steps
    for i in range(steps):
        x = x_start + x_step * i
        y = y_start + y_step * i
        pyautogui.moveTo(x, y)
        time.sleep(0.01)


with mss.mss() as sct:
    while True:
        start_time = time.time()

        # Захватываем изображение определенной области
        screenshot = sct.grab(monitor)

        # Преобразуем изображение в формат numpy array
        screenshot_np = np.array(screenshot)

        # Преобразуем цвета из BGR (mss) в RGB
        screenshot_rgb = screenshot_np[:, :, :3]

        # Создаем маску для выделения целевого цвета
        mask = cv2.inRange(screenshot_rgb, lower_bound, upper_bound)

        # Находим контуры объектов на маске
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Инициализируем переменные для хранения информации о ближайшем прямоугольнике
        closest_rectangle = None
        min_distance = float('inf')

        # Пройдемся по всем контурам
        for contour in contours:
            # Получаем координаты ограничивающего прямоугольника
            x, y, w, h = cv2.boundingRect(contour)

            # Вычисляем центр прямоугольника
            rectangle_center = (x + w // 2, y + h // 2)

            # Вычисляем расстояние от центра маски до центра прямоугольника
            distance = np.linalg.norm(np.array([mask.shape[1] // 2, mask.shape[0] // 2]) - np.array(rectangle_center))

            # Проверяем размер прямоугольника
            if 5 <= w <= 40 and 5 <= h <= 40:
                # Если текущий прямоугольник ближе к центру маски и удовлетворяет условиям размера,
                # обновляем информацию о ближайшем прямоугольнике
                if distance < min_distance:
                    min_distance = distance
                    closest_rectangle = (x, y, w, h)

        # Если найден ближайший красный прямоугольник, перемещаем курсор мыши к его центру
        if closest_rectangle:
            # Получаем координаты центра прямоугольника
            x, y, w, h = closest_rectangle
            rectangle_center = (x + w // 2, y + h // 2)

            # Получаем текущие координаты курсора мыши
            current_cursor_position = pyautogui.position()

            # Вычисляем новые координаты курсора для перемещения к центру прямоугольника
            new_cursor_position = (
                current_cursor_position[0] + int((rectangle_center[0] - mask.shape[1] // 2) * move_speed),
                current_cursor_position[1] + int((rectangle_center[1] - mask.shape[0] // 2) * move_speed)
            )

            # Ограничим координаты курсора, чтобы они не выходили за пределы экрана
            new_cursor_position = (
                max(0, min(new_cursor_position[0], screen_width)),
                max(0, min(new_cursor_position[1], screen_height))
            )

            smooth_move(current_cursor_position, new_cursor_position, smoothness)

        print(f"FPS: {1.0 / (time.time() - start_time):.2f}")