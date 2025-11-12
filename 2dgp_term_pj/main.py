# main.py

from pico2d import *
from boy import Boy
import random

STATE_TITLE = 0
STATE_GAMEPLAY = 1
STATE_VIEWING_ART = 2
STATE_FADING_OUT = 3
STATE_FADING_IN = 4
STATE_POST_FADE_DELAY = 5
current_state = STATE_TITLE

ART_NONE = 0
ART_MONALISA = 1
ART_STARRY_NIGHT = 2
ART_ISLAND = 3
ART_EATING_PLANET = 4
currently_viewing_art = ART_NONE

current_room_index = 0
success_count = 0
FINAL_SUCCESS_COUNT = 7

is_anomaly_present = False
anomaly_type = 0

ANOMALY_MONALISA_SMILE = 1 #15개 이상현상까지 사용 예정

mona_x = 100
mona_y = 500
mona_w = 100
mona_h = 150

starry_night_y = 500
starry_night_w = 100
starry_night_h = 150
starry_night_x = mona_x + (mona_w // 2) + (starry_night_w // 2) + 100

island_x = starry_night_x + (starry_night_w // 2) + (100 // 2) + 100
island_y = 500
island_w = 100
island_h = 150

eating_planet_x = island_x + (island_w // 2) + (100 // 2) + 100
eating_planet_y = 500
eating_planet_w = 100
eating_planet_h = 150



interaction_distance = 75
mona_large_w = int(800 * 0.8)
mona_large_h = int(600 * 0.9)

fade_alpha = 0.0
transition_target_room = 0
transition_player_pos_x = 0
post_fade_delay_timer = 0.0
POST_FADE_DELAY_TIME = 0.3

def check_collision(a_x, a_y, b_x, b_y, distance_threshold):
    distance_sq = (a_x - b_x) ** 2 + (a_y - b_y) ** 2
    return distance_sq < distance_threshold ** 2

def setup_new_room():
    global is_anomaly_present, anomaly_type

    if random.randint(0, 1) == 0:
        is_anomaly_present = True

        anomaly_type = ANOMALY_MONALISA_SMILE
        print(f"DEBUG: ANOMALY PRESENT (Type: MONALISA SMILE - {anomaly_type})")
    else:
        is_anomaly_present = False
        anomaly_type = 0
        print("DEBUG: No Anomaly.")


# --- 1. 초기화 ---
open_canvas(800, 600)
player = Boy()

# 1-2. 배경 및 사물 로드
background = load_image('BACKGROUND.png')
monalisa_art = load_image('pic_1.png')
monalisa_smile_art = load_image('pic_1_2.png')
starry_night_art = load_image('pic_2.png')
island_art = load_image('pic_3.png')
eating_planet_art = load_image('pic_4.png')
black_pixel = load_image('black_pixel.png')
title_screen_image = load_image('title.png')
title_font = load_font('ariblk.ttf', 30)
ui_font = load_font('ariblk.ttf', 24)

running = True
setup_new_room()

# --- 2. 게임 루프 ---
while running:
# 3. 이벤트 처리
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False

        elif current_state == STATE_TITLE:
             if event.type == SDL_KEYDOWN:
                 current_state = STATE_GAMEPLAY

        elif event.type == SDL_KEYDOWN and event.key == SDLK_e:
            if current_state == STATE_GAMEPLAY:
                if current_room_index == 0:
                    if check_collision(player.x, player.y, mona_x, mona_y, interaction_distance):
                        current_state = STATE_VIEWING_ART
                        currently_viewing_art = ART_MONALISA
                    elif check_collision(player.x, player.y, starry_night_x, starry_night_y, interaction_distance):
                        current_state = STATE_VIEWING_ART
                        currently_viewing_art = ART_STARRY_NIGHT
                    elif check_collision(player.x, player.y, island_x, island_y, interaction_distance):
                        current_state = STATE_VIEWING_ART
                        currently_viewing_art = ART_ISLAND
                    elif check_collision(player.x, player.y, eating_planet_x, eating_planet_y, interaction_distance):
                        current_state = STATE_VIEWING_ART
                        currently_viewing_art = ART_EATING_PLANET

            elif current_state == STATE_VIEWING_ART:
                current_state = STATE_GAMEPLAY
                currently_viewing_art = ART_NONE
                player.dir_x, player.dir_y = 0, 0

        elif current_state != STATE_VIEWING_ART:
            player.handle_event(event)

    if current_state == STATE_GAMEPLAY:
        if current_room_index == 1:
            room_change_status = player.update()
            if room_change_status == 'PREV':
                current_state = STATE_FADING_OUT
                transition_target_room = 0
                success_count = 0
                transition_player_pos_x = player.boundary_right
                fade_alpha = 0.0

        elif current_room_index == 0:
            room_change_status = player.update()

            if room_change_status == 'NEXT' or room_change_status == 'PREV':
                is_correct_choice = False
                if room_change_status == 'NEXT' and not is_anomaly_present:
                    is_correct_choice = True
                elif room_change_status == 'PREV' and is_anomaly_present:
                    is_correct_choice = True
                if is_correct_choice:
                    success_count += 1
                else:
                    success_count = 0
                if success_count >= FINAL_SUCCESS_COUNT:
                    transition_target_room = 1
                else:
                    transition_target_room = 0

                current_state = STATE_FADING_OUT
                fade_alpha = 0.0
                if room_change_status == 'NEXT':
                    transition_player_pos_x = player.boundary_left
                else:  # 'PREV'
                    transition_player_pos_x = player.boundary_right

    elif current_state == STATE_FADING_OUT:
        fade_alpha += 0.05
        if fade_alpha >= 1.0:
            fade_alpha = 1.0
            current_room_index = transition_target_room
            player.x = transition_player_pos_x
            current_state = STATE_FADING_IN

    elif current_state == STATE_FADING_IN:
        fade_alpha -= 0.05
        if fade_alpha <= 0.0:
            fade_alpha = 0.0
            current_state = STATE_POST_FADE_DELAY
            post_fade_delay_timer = get_time()

    elif current_state == STATE_POST_FADE_DELAY:
        if get_time() - post_fade_delay_timer > POST_FADE_DELAY_TIME:
            current_state = STATE_GAMEPLAY
            if current_room_index == 0:
                setup_new_room()
            else:
                is_anomaly_present, anomaly_type = False, 0



    # 5. 그리기 (렌더링)
    clear_canvas()

    def draw_room_0_art():
        if anomaly_type == ANOMALY_MONALISA_SMILE:
            monalisa_smile_art.composite_draw(0, '', mona_x, mona_y, mona_w, mona_h)
        else:
            monalisa_art.composite_draw(0, '', mona_x, mona_y, mona_w, mona_h)
            #추후 14개 이상 로직 여기 추가

        starry_night_art.composite_draw(0, '', starry_night_x, starry_night_y, starry_night_w, starry_night_h)
        island_art.composite_draw(0, '', island_x, island_y, island_w, island_h)
        eating_planet_art.composite_draw(0, '', eating_planet_x, eating_planet_y, eating_planet_w, eating_planet_h)


    def draw_ui_text():
        if current_room_index == 0:
            ui_font.draw(700, 570, f"{success_count} / {FINAL_SUCCESS_COUNT}", (255, 255, 255))
        elif current_room_index == 1:
            ui_font.draw(720, 570, "EXIT", (0, 255, 0))


    if current_state == STATE_TITLE:
       title_screen_image.draw(400, 300, 800, 600)
       title_font.draw(180, 100, "press any key to start game", (255, 255, 255))

    elif current_state == STATE_GAMEPLAY or current_state == STATE_FADING_OUT:
       background.draw(400, 300)
       if current_room_index == 0:
           draw_room_0_art()
       elif current_room_index == 1:
           pass
       draw_ui_text()
       player.draw()

    elif current_state == STATE_FADING_IN or current_state == STATE_POST_FADE_DELAY:
         background.draw(400, 300)
         if current_room_index == 0:
             draw_room_0_art()
         elif current_room_index == 1:
             pass
         draw_ui_text()
         player.draw()


    # 5-2. 플레이어 그리기

    elif current_state == STATE_VIEWING_ART:
        background.draw(400, 300)


        if currently_viewing_art == ART_MONALISA:
            if anomaly_type == ANOMALY_MONALISA_SMILE:
                monalisa_smile_art.composite_draw(0, '', 400, 350, mona_large_w, mona_large_h)
            else:
                monalisa_art.composite_draw(0, '', 400, 300, mona_large_w, mona_large_h)
        elif currently_viewing_art == ART_STARRY_NIGHT:
            starry_night_art.composite_draw(0, '', 400, 300, mona_large_w, mona_large_h)
        elif currently_viewing_art == ART_ISLAND:
            island_art.composite_draw(0, '', 400, 300, mona_large_w, mona_large_h)
        elif currently_viewing_art == ART_EATING_PLANET:
            eating_planet_art.composite_draw(0, '', 400, 300, mona_large_w, mona_large_h)

    if current_state == STATE_FADING_OUT or current_state == STATE_FADING_IN:
        black_pixel.opacify(fade_alpha)
        black_pixel.draw(400, 300, 800, 600)

    update_canvas()
    delay(0.01)

# --- 6. 종료 ---
close_canvas()