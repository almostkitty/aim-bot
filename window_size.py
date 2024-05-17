import numpy as np
import mss
import cv2
import json

# Определим функцию для поиска контура черного окошка
def find_black_window(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_contour = None
    max_contour_area = 0

    for contour in contours:
        contour_area = cv2.contourArea(contour)
        if contour_area > max_contour_area:
            max_contour = contour
            max_contour_area = contour_area

    if max_contour is not None:
        x, y, w, h = cv2.boundingRect(max_contour)
        return x, y, x + w, y + h  # левая верхняя и правая нижняя точки
    return None

# Определим область захвата (весь экран)
with mss.mss() as sct:
    monitor = sct.monitors[1]
    screen_width = monitor["width"]
    screen_height = monitor["height"]

    # Захватываем скриншот всего экрана
    screenshot = np.array(sct.grab({"top": 0, "left": 0, "width": screen_width, "height": screen_height}))

    # Находим окошко
    window_coords = find_black_window(screenshot)
    if window_coords:
        x1, y1, x2, y2 = window_coords
        # Печатаем координаты окошка
        print(f"Левый верхний угол: ({x1}, {y1})\nПравый нижний угол: ({x2}, {y2})")

        # Создаем словарь с координатами окошка
        window_dict = {
            "top_left": {"x": x1, "y": y1},
            "bottom_right": {"x": x2, "y": y2}
        }

        # Сохраняем координаты окошка в файл JSON
        with open("../Python/aim-bot/window_coordinates.json", "w") as json_file:
            json.dump(window_dict, json_file)

        # Создаем новое изображение
        window_image = np.zeros_like(screenshot)

        # Копируем выделенную область в новое изображение
        window_image[y1:y2, x1:x2] = screenshot[y1:y2, x1:x2]

        # Сохраняем изображение с выделенной областью
        cv2.imwrite("detected_window.png", window_image)
