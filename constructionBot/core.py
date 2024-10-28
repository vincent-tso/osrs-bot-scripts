from PIL import ImageGrab
from functions import *
import pyautogui


def wait_to_finish_interaction(status_image, confidence):
    waiting_to_finish_interaction = True

    while waiting_to_finish_interaction:
        interaction_status = find_image(status_image, chat_location, confidence)

        if not interaction_status:
            waiting_to_finish_interaction = False

        time.sleep(get_random_range(120, 160, 1000))


def fetch_planks():
    global is_fetching_planks
    global interacting_with_butler

    pyautogui.press('1')

    # Wait for butler to fetch planks
    wait_to_finish_interaction("butler_fetching_planks", 0.8)

    is_fetching_planks = True
    interacting_with_butler = False


def pay_butler():
    pyautogui.press('space')

    # Wait to pay butler
    wait_to_finish_interaction("butler_requesting_payment", 0.8)

    pyautogui.press('1')

    # Wait to pay butler
    wait_to_finish_interaction("butler_payment_step_1", 0.8)

    pyautogui.press('space')

    # Wait to pay butler
    wait_to_finish_interaction("butler_payment_step_2", 0.8)


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
    statuses = ["butler_ready_to_fetch_20", "butler_requesting_payment", "butler_retrieved_planks"]

    for status in statuses:
        status_location = find_image(status, chat_location, 0.8)

        if status_location:
            return status

    return None


def check_butler():
    global is_fetching_planks
    global interacting_with_butler
    global waiting_on_butler
    global waiting_for_removal
    global currently_removing

    # Find butler
    butler_location = find_butler_location()

    if butler_location:
        # Check Butler Status
        # interacting_with_butler = False
        butler_status = check_butler_status()

        if waiting_for_removal:
            waiting_for_removal = False
            currently_removing = False

        if butler_status:
            is_fetching_planks = False

            match butler_status:
                case 'butler_requesting_payment':
                    pay_butler()
                case 'butler_ready_to_fetch_20':
                    fetch_planks()
                    waiting_on_butler = False

        print(f"Butler is fetching planks: {is_fetching_planks}")

        time.sleep(get_random_range(100, 150, 1000))

        if not interacting_with_butler and not is_fetching_planks:
            move(butler_location)

            waiting_for_butler_interaction = True

            while waiting_for_butler_interaction:
                curr_butler_status = check_butler_status()

                if curr_butler_status and (curr_butler_status == "butler_ready_to_fetch_20" or curr_butler_status == "butler_requesting_payment"):
                    waiting_for_butler_interaction = False
                    interacting_with_butler = True

                time.sleep(0.1)


# Get Image Search Locations
client_title = 'Mausies Rat'
print(client_title)

client_location = get_client_region(client_title)
screen_location = get_screen_region(client_location)
inventory_location = get_inventory_region(client_location)
chat_location = get_chat_region(client_location)

construct = "door"

# Initiate Status Variables
is_fetching_planks = False
interacting_with_butler = False
currently_building = False
currently_removing = False
waiting_for_menu = False
waiting_for_removal = False
waiting_on_butler = False

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
        # Check if Construct is ready to build
        build_location = find_construct(screen_location, f"{construct}_build")

        if build_location:
            # Check oak planks
            oak_plank_location = find_image('oak_plank', inventory_location, 0.8)

            if not oak_plank_location:
                waiting_on_butler = True

            if oak_plank_location and not waiting_on_butler:
                # Check if not currently Building Larder
                if not currently_building:
                    print("Building Construct")
                    currently_building = True
                    move(build_location)
                    currently_removing = False
                    waiting_for_menu = True
        else:
            if currently_building:
                # Check for creation option menu
                construct_option_menu = find_image(f'{construct}_option_menu', screen_location, 0.8)

                if construct_option_menu and waiting_for_menu:
                    pyautogui.press('1')
                    waiting_for_menu = False

            # Check if not currently Removing Larder
            if not currently_removing:
                remove_location = find_construct(screen_location, f'{construct}_remove')

                if remove_location and not waiting_for_removal:
                    move(remove_location)
                    print("Removing Construct")
                    currently_removing = True
                    currently_building = False
                    waiting_for_removal = True

            construct_remove_confirmation = find_image('remove_confirmation', chat_location, 0.8)

            if construct_remove_confirmation:
                pyautogui.press('1')
                waiting_for_removal = False

    time.sleep(0.1)
