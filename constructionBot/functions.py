from pywinauto import Application
from PIL import ImageGrab
import pyautogui
import cv2
import random
import math
import time
import numpy as np
import pytesseract

pyautogui.PAUSE = 0
TICK_INTERVAL = 0.6 # RuneScape tick duration in seconds
SCREEN_WIDTH = 512
SCREEN_HEIGHT = 340

CHAT_LEFT = 0
CHAT_TOP = 346
CHAT_WIDTH = 532
CHAT_HEIGHT = 134

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Vincent\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def find_image(image, region, confidence):
    try:
        return pyautogui.locateOnScreen(f'images/{image}.png', region=region, confidence=confidence)
    except:
        # print(f'Error: {image} could not be found.')
        return None

def get_client_region(title):
    app = Application().connect(title=f'RuneLite - {title}')

    window = app.window(title=f'RuneLite - {title}')
    window.set_focus()

    rect = window.rectangle()
    left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
    width, height = right - left, bottom - top

    # Handle negative values for coordinates
    left = max(0, left)  # Ensure the left boundary is non-negative
    top = max(0, top)  # Ensure the top boundary is non-negative

    client_border_left_offset = 8
    client_border_width_offset = 76
    client_border_height = 32
    client_border_height_offset = 6

    return (left + client_border_left_offset, top + client_border_height, width - client_border_width_offset, height - client_border_height - client_border_height_offset)

def get_screen_region(search_region):
    return (search_region[0], search_region[1], SCREEN_WIDTH, SCREEN_HEIGHT)



def get_chat_region(search_region):
    return (search_region[0] + CHAT_LEFT, search_region[1] + CHAT_TOP, CHAT_WIDTH, CHAT_HEIGHT)

def get_inventory_region(search_region):
    inventory_top_location = find_image('inventory_top_border', search_region, 0.8)
    inventory_bottom_location = find_image('inventory_bottom_border', search_region, 0.8)

    left, top, width, height = inventory_top_location.left, inventory_top_location.top, inventory_top_location.width, inventory_bottom_location.top + inventory_bottom_location.height - inventory_top_location.top

    return (left, top, width, height)

def get_random_range(start, end, divisor = 1):
    return random.randint(start, end) / divisor

def click(image_location): # Click on item in inventory
    rand_x = get_random_range(image_location.left, image_location.left + image_location.width)
    rand_y = get_random_range(image_location.top, image_location.top + image_location.height)
    centre_x, centre_y = pyautogui.center(image_location).x, pyautogui.center(image_location).y
    pyautogui.click(centre_x + math.floor((((rand_x - centre_x) * 2) / 3)),
                      centre_y + math.floor((((rand_y - centre_y) * 2) / 3)))

def move(image_location):  # Move cursor to 3d object on screen
    # rand_x = get_random_range(image_location[0], image_location[0] + image_location[2])
    # rand_y = get_random_range(image_location[1], image_location[1] + image_location[3])
    centre_x, centre_y = pyautogui.center(image_location).x, pyautogui.center(image_location).y
    # pyautogui.moveTo(centre_x + math.floor((rand_x - centre_x) / 3),
    #                  centre_y + math.floor((rand_y - centre_y) / 3))
    pyautogui.moveTo(centre_x, centre_y)
    time.sleep(get_random_range(100, 150, 1000))
    pyautogui.click()


def find_template_location(search_region, screenshot, template, threshold=0.8):
    # Load the screenshot and the template
    template = cv2.imread(f'images/{template}.png')  # Replace with your template

    # Convert the screenshot to a NumPy array and then to a format OpenCV can work with
    screenshot_np = np.array(screenshot)
    screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)  # Convert from RGB to BGR for OpenCV

    # Convert images to grayscale (optional, but usually more efficient)
    screenshot_gray = cv2.cvtColor(screenshot_cv2, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Perform template matching
    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    # Find the min and max locations in the result
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Return the top-left corner (x, y) of the match
    if max_val >= threshold:
        # A good match was found, return the top-left corner of the match
        # print("Found")

        top_left = max_loc
        h, w = template_gray.shape[:2]  # Height and width of the template

        return (search_region[0] + top_left[0], search_region[1] + top_left[1], w, h)
    else:
        # No good match was found
        # print("Not Found")
        # print(f'Confidence: {max_val}')
        return None
