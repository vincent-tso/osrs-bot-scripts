from PIL import ImageGrab
from functions import *
import sys


arguments = sys.argv

ACCOUNT_NAME = arguments[1]
CONSTRUCT = arguments[2]
PLANKS_COUNT = arguments[3]

READY_TO_FETCH_STATUS = f"butler_ready_to_fetch_{PLANKS_COUNT}"
REQUESTING_PAYMENT_STATUS = "butler_requesting_payment"

# Get Image Search Locations
client_title = ACCOUNT_NAME
print(client_title)

client_location = get_client_region(client_title)
screen_location = get_screen_region(client_location)
inventory_location = get_inventory_region(client_location)
chat_location = get_chat_region(client_location)

# Initiate Status Variables
is_fetching_planks = False
currently_building = False
currently_removing = False
waiting_for_menu = False
waiting_for_removal = False
waiting_on_butler = False


def wait_to_finish_interaction(status_image, confidence):
    waiting_to_finish_interaction = True

    print("Waiting for interaction")

    while waiting_to_finish_interaction:
        interaction_status = find_image(status_image, chat_location, confidence)

        if not interaction_status:
            waiting_to_finish_interaction = False
            print("Interaction finished")

        time.sleep(get_random_range(120, 150, 1000))


def fetch_planks():
    global is_fetching_planks

    pyautogui.press('1')

    # Wait for butler to fetch planks
    wait_to_finish_interaction("butler_fetching_planks", 0.8)

    print(f"Butler is fetching {PLANKS_COUNT} x Oak Planks")

    is_fetching_planks = True


def pay_butler():
    print("Butler is requesting payment.")

    pyautogui.press('space')

    # Wait to pay butler
    wait_to_finish_interaction("butler_requesting_payment", 0.8)

    pyautogui.press('1')

    # Wait to pay butler
    wait_to_finish_interaction("butler_payment_step_1", 0.8)

    pyautogui.press('space')

    # Wait to pay butler
    wait_to_finish_interaction("butler_payment_step_2", 0.8)

    print("Butler has been paid.")


def find_butler_location():
    left, top, width, height = screen_location[0], screen_location[1], screen_location[2], screen_location[3]

    butler_template_locations = ('butler_north', 'butler_east', 'butler_south')
    butler_template_search_boxes = (
        (left + math.floor(width / 3), top, left + math.floor(width * 2 / 3), top + math.floor(height / 3)),
        (left + math.floor(width * 2 / 3), top + math.floor(height / 3), left + width, top + math.floor(height * 2 / 3)),
        (left + math.floor(width/ 3), top + math.floor(height * 2 / 3), left + math.floor(width * 2 / 3), top + height)
    )

    for index, value in enumerate(butler_template_locations):
        bbox = butler_template_search_boxes[index]
        screenshot = ImageGrab.grab(bbox=bbox)

        location = find_template_location(screen_location, screenshot, value, 0.7)

        if location:
            print(f'Butler location found: {location}')
            return bbox[0] + location[0] - left, bbox[1] + location[1] - top, location[2], location[3]

    print('Butler could not be found.')
    return None


def find_construct(search_region, template):
    bbox = (search_region[0], search_region[1], search_region[0] + search_region[2],
            search_region[1] + search_region[3])

    screenshot = ImageGrab.grab(bbox=bbox)
    construct_location = find_template_location(search_region, screenshot, template)

    return construct_location


def check_butler_status():
    statuses = [READY_TO_FETCH_STATUS, "butler_requesting_payment", "butler_retrieved_planks"]

    for status in statuses:
        status_location = find_image(status, chat_location, 0.8)

        if status_location:
            print(f"Butler status found: {status}")
            return status

    return None


def check_butler():
    global is_fetching_planks
    global waiting_on_butler

    # Find butler
    butler_location = find_butler_location()

    if butler_location:
        is_fetching_planks = False

        if not waiting_on_butler:
            move(butler_location)

            waiting_on_butler = True

        elif waiting_on_butler:
            # Check for Butler Status
            butler_status = check_butler_status()

            if butler_status:

                if butler_status == REQUESTING_PAYMENT_STATUS:
                    pay_butler()
                    waiting_on_butler = False
                elif butler_status == READY_TO_FETCH_STATUS:
                    fetch_planks()
                    waiting_on_butler = False


def build_construct(build_location):
    global is_fetching_planks
    global currently_building
    global currently_removing
    global waiting_for_menu
    global waiting_on_butler

    if not currently_building:
        oak_plank_location = find_image('oak_plank', inventory_location, 0.8)

        if oak_plank_location and waiting_on_butler:
            waiting_on_butler = False
            return
        
        elif oak_plank_location and not waiting_on_butler:
            print("Building Construct")

            move(build_location)

            currently_building = True
            waiting_for_menu = True

            while waiting_for_menu:
                construct_option_menu = find_image(f'{CONSTRUCT}_option_menu', screen_location, 0.8)

                if construct_option_menu:
                    if CONSTRUCT == "larder":
                        pyautogui.press('2')
                    else:
                        pyautogui.press('1')

                    waiting_for_menu = False
                    currently_removing = False

                time.sleep(0.1)

        elif not oak_plank_location:
            is_fetching_planks = False


def remove_construct(remove_location):
    global currently_removing
    global currently_building
    global waiting_for_removal

    if not currently_removing:
        if remove_location and not waiting_for_removal:
            print("Removing Construct")

            move(remove_location)
            currently_removing = True
            waiting_for_removal = True
    else:
        construct_remove_confirmation = find_image('remove_confirmation', chat_location, 0.8)

        if construct_remove_confirmation and waiting_for_removal:
            pyautogui.press('1')
            waiting_for_removal = False
            currently_building = False


def construct():
    # Check state of Larder
    build_location = find_construct(screen_location, f"{CONSTRUCT}_build")

    if build_location:
        build_construct(build_location)
    else:
        remove_location = find_construct(screen_location, f"{CONSTRUCT}_remove")

        if remove_location and not waiting_on_butler:
            remove_construct(remove_location)


# TODO
# Move status checks from functions above to while loop
# Track if currently building or removing
# Move to larder if build or removing to a separate check
# Constantly check for status changes in chat

while True:
    pyautogui.moveTo(pyautogui.center(screen_location).x, pyautogui.center(screen_location).y)

    check_butler()

    # Check if Butler is Fetching Planks
    if is_fetching_planks:
        construct()

    time.sleep(0.1)
