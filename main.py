import threading

from PIL import Image, ImageDraw
from loguru import logger
from pystray import Icon as icon, Menu as menu, MenuItem as item
import dearpygui.dearpygui as dpg

logger.add("logs.txt", rotation="1 MB")

from start_app import start_app, stop_app

def create_image(width, height, color1, color2):
    # Generate an image and draw a pattern
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image


def on_clicked():
    threading.Thread(target=start_app).start()


def stop():
    ico.stop()
    stop_app()


ico = icon('PhotoshopRemaper', create_image(64, 64, 'black', 'white'),
           menu=menu(
               item(
                   'Открыть',
                   on_clicked),
               item(
                   'Закрыть',
                   stop)
           ))
ico.run_detached()

start_app()
