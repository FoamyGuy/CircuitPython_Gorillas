import time
import board
import displayio
import adafruit_imageload
import ugame
import random
from banana import Banana
from player import Player
from adafruit_display_text import label
import terminalio

STATE_TESTING = -1

STATE_PREGAME_SETUP = 0
STATE_WAITING_ANGLE_INPUT = 1
STATE_WAITING_VELOCITY_INPUT = 2
STATE_RESOlVING_THROW = 3

cur_player = 1

angle = 90
velocity = 50

CURRENT_STATE = STATE_PREGAME_SETUP

display = board.DISPLAY

# Load the sprite sheet (bitmap)
banana_sprites, palette = adafruit_imageload.load("/banana_all.bmp",
                                                  bitmap=displayio.Bitmap,
                                                  palette=displayio.Palette)

palette.make_transparent(0)
# Create a sprite (tilegrid)
banana_tilegrid = displayio.TileGrid(banana_sprites, pixel_shader=palette,
                                     width=1,
                                     height=1,
                                     tile_width=10,
                                     tile_height=10)

banana = Banana(banana_tilegrid)

break_stamp_bitmap, break_stamp_palette = adafruit_imageload.load("/break_stamp.bmp",
                                                  bitmap=displayio.Bitmap,
                                                  palette=displayio.Palette)

gorilla_sprites, gorilla_palette = adafruit_imageload.load("/gorilla_all.bmp",
                                                  bitmap=displayio.Bitmap,
                                                  palette=displayio.Palette)

gorilla_palette.make_transparent(0)

player_1 = Player(gorilla_sprites, gorilla_palette)
player_2 = Player(gorilla_sprites, gorilla_palette)


background_bitmap = bitmap = displayio.Bitmap(320, 240, 8)
bg_palette = displayio.Palette(8)
bg_palette[0] = 0x0402AC
bg_palette[1] = 0x04AAAC
bg_palette[2] = 0xAC0204
bg_palette[3] = 0xACAAAC
bg_palette[4] = 0xFCFE54
bg_palette[5] = 0x545654
#bg_palette.make_transparent(0)

background_tilegrid = displayio.TileGrid(background_bitmap, pixel_shader=bg_palette)


main_group = displayio.Group(scale=1, max_size=10)
main_group.append(background_tilegrid)

angle_text = label.Label(terminalio.FONT, max_glyphs=len("Angle: 111"))
angle_text.anchor_point = (0.0, 0.0)
angle_text.anchored_position = (0, 0)

velocity_text = label.Label(terminalio.FONT, max_glyphs=len("Velocity: 111"))
velocity_text.anchor_point = (1.0, 0.0)
velocity_text.anchored_position = (display.width, 0)

main_group.append(angle_text)
main_group.append(velocity_text)
# Add the Group to the Display
display.show(main_group)



def place_player(player, choices=[0,16,32]):
    player_x = random.choice(choices)
    player_y = display.height

    while background_bitmap[player_x,player_y] != 0:
        player_y -= 1

    player.x = player_x
    player.y = player_y - 15
    main_group.append(player)

def rect_intersect(l1, r1, l2, r2):
    # If one rectangle is on left side of other
    if(l1[0] >= r2[0] or l2[0] >= r1[0]):
        return False
    # If one rectangle is above other
    if(l1[1] >= r2[1] or l2[1] >= r1[1]):
        return False
    return True

def check_collision():
    for x in range(1,9):
        for y in range(1,9):
            #print("checking ({}, {})".format(banana.x + x, banana.y + y))
            try:
                if background_bitmap[banana.x + x,banana.y + y] != 0:
                    return (banana.x + x + 1, banana.y + y + 1)
            except IndexError:
                # ignore any pixels outside the screen
                pass

    return None

def break_background(coordinates):
    for x in range(-3,4):
        for y in range(-3,4):

            print("setting ({}, {}) = 0".format(coordinates[0]+x, coordinates[1]+y))
            if break_stamp_bitmap[x+3,y+3] != 0:
                try:
                    background_bitmap[coordinates[0]+x, coordinates[1]+y] = 0
                except IndexError:
                    pass

# Loop through each sprite in the sprite sheet
source_index = 0
prev_btn_vals = ugame.buttons.get_pressed()
while True:

    if banana in main_group:
        banana.update()
    time.sleep(0.10)

    cur_btn_vals = ugame.buttons.get_pressed()

    if CURRENT_STATE == STATE_PREGAME_SETUP:
        background_bitmap.fill(0)
        for building in range(0,160,16):
            random_height = random.randint(16,70)
            random_color = random.choice([1,2,3])
            for y in range(0, random_height):
                for x in range(0,16):
                    background_bitmap[building+x, display.height - y] = random_color

            # Windows
            for window_y in range(2, random_height-4, 5):
                window_0_color = random.choice([4,4,4,4,4,4,5])
                window_1_color = random.choice([4,4,4,4,4,4,5])
                for window_x in [4,5]:
                    background_bitmap[building + window_x, display.height - window_y-2] = window_0_color
                    background_bitmap[building + window_x, display.height - window_y-1] = window_0_color
                    background_bitmap[building + window_x, display.height - window_y] = window_0_color
                for window_x in [10,11]:
                    background_bitmap[building + window_x, display.height - window_y-2] = window_1_color
                    background_bitmap[building + window_x, display.height - window_y-1] = window_1_color
                    background_bitmap[building + window_x, display.height - window_y] = window_1_color

        place_player(player_1, choices=[0,16,32])
        place_player(player_2, choices=[160-48,160-32,160-16])
        CURRENT_STATE = STATE_WAITING_ANGLE_INPUT

    if CURRENT_STATE == STATE_WAITING_ANGLE_INPUT:
        angle_text.text = "Angle: {}".format(angle)
        if not prev_btn_vals & ugame.K_O and cur_btn_vals & ugame.K_O:
            prev_btn_vals = cur_btn_vals
            CURRENT_STATE = STATE_WAITING_VELOCITY_INPUT
        if cur_btn_vals & ugame.K_UP:
            angle += 1
        if cur_btn_vals & ugame.K_DOWN:
            angle -= 1
    if CURRENT_STATE == STATE_WAITING_VELOCITY_INPUT:
        velocity_text.text = "Velocity: {}".format(velocity)
        if cur_btn_vals & ugame.K_UP:
            velocity += 1
        if cur_btn_vals & ugame.K_DOWN:
            velocity -= 1
        if not prev_btn_vals & ugame.K_O and cur_btn_vals & ugame.K_O:
            if cur_player == 1:
                if banana not in main_group:
                    banana.x = player_1.x
                    banana.y = player_1.y - 16
                    main_group.append(banana)
                    banana.throw(angle, velocity/10)
                    cur_player = 2
                angle_text.text = ""
                velocity_text.text = ""
                CURRENT_STATE = STATE_RESOlVING_THROW
            elif cur_player == 2:
                if banana not in main_group:
                    banana.x = player_2.x
                    banana.y = player_2.y - 16
                    main_group.append(banana)
                    banana.throw(180-angle, velocity/10)
                    cur_player = 1
                angle_text.text = ""
                velocity_text.text = ""
                CURRENT_STATE = STATE_RESOlVING_THROW

    if CURRENT_STATE == STATE_RESOlVING_THROW:
        if banana.is_throwing:
            if rect_intersect(
                (banana.x+1, banana.y+1),
                (banana.x+9, banana.y+9),
                (player_1.x, player_1.y),
                (player_1.x+16, player_1.y+16)
            ):
                # player 1 was hit
                player_2.celebrate()
                main_group.remove(player_1)
                main_group.remove(player_2)
                banana.stop_throw()
                main_group.remove(banana)
                CURRENT_STATE = STATE_PREGAME_SETUP
                continue

            if rect_intersect(
                (banana.x+1, banana.y+1),
                (banana.x+9, banana.y+9),
                (player_2.x, player_2.y),
                (player_2.x+16, player_2.y+16)
            ):
                # player 2 was hit
                player_1.celebrate()
                main_group.remove(player_1)
                main_group.remove(player_2)
                banana.stop_throw()
                main_group.remove(banana)
                CURRENT_STATE = STATE_PREGAME_SETUP
                continue

            if banana.x > display.width or banana.x < 0 - 10:
                banana.stop_throw()
                main_group.remove(banana)
                CURRENT_STATE = STATE_WAITING_ANGLE_INPUT
            collision_point = check_collision()
            if collision_point:
                print(collision_point)
                break_background(collision_point)
                banana.stop_throw()
                main_group.remove(banana)
                CURRENT_STATE = STATE_WAITING_ANGLE_INPUT
    if CURRENT_STATE == STATE_TESTING:


        cur_btn_vals = ugame.buttons.get_pressed()  # update button sate
        if cur_btn_vals & ugame.K_UP:
            if banana in main_group:
                banana.stop_throw()
                main_group.remove(banana)
            else:
                main_group.append(banana)
                banana.x = 120
                banana.y = 80


        if not prev_btn_vals & ugame.K_DOWN and cur_btn_vals & ugame.K_DOWN:
            if banana not in main_group:
                banana.x = player_1.x
                banana.y = player_1.y - 16
                main_group.append(banana)
                banana.throw(60, 7)
    prev_btn_vals = cur_btn_vals