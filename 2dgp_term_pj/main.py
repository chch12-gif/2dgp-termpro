# main.py

from pico2d import *
from config import *
from boy import Boy
from background import Background
import random

# --- 변수 초기화 ---
current_state = STATE_TITLE
currently_viewing_art = ART_NONE
current_room_index = 0
success_count = 0

# 8번 출구 로직 변수
is_anomaly_present = False
anomaly_type = 0
is_first_game_run = True
seen_anomalies_this_run = []
shadow_x = 400
shadow_y = 300
shadow_speed = 1.0
shadow_dir = 0

#메세지 이상현상 변수
msg_timer = 0.0
msg_count = 0
msg_triggered = False

#이상현상 리스트
ALL_ANOMALIES = [
    ANOMALY_MONALISA_SMILE,
    ANOMALY_HAND_PRINT,
    ANOMALY_PLAYER_GIANT,
    ANOMALY_DARK_ZONE,
    ANOMALY_SHADOW_MAN,
    ANOMALY_VENUS_CENTER,
    ANOMALY_ALL_SAME,
    ANOMALY_ALL_GONE,
    ANOMALY_LEAVE_MSG,
    ANOMALY_STARRY_NIGHT_HORROR
]

# 페이드 변수
fade_alpha = 0.0
transition_target_room = 0
transition_player_pos_x = 0
post_fade_delay_timer = 0.0


# --- 헬퍼 함수 ---
def check_collision(a_x, a_y, b_x, b_y, distance_threshold):
    distance_sq = (a_x - b_x) ** 2 + (a_y - b_y) ** 2
    return distance_sq < distance_threshold ** 2


def setup_new_room():
    global is_anomaly_present, anomaly_type, seen_anomalies_this_run, is_first_game_run, shadow_x, shadow_y

    if is_first_game_run:
        is_anomaly_present = False
        anomaly_type = 0
        is_first_game_run = False
        print("DEBUG: First run of the game. No Anomaly.")
    else:
        if random.randint(0, 1) == 0:  # 50% 확률
            is_anomaly_present = True

            # 가능한 이상현상 리스트 필터링 (중복 방지)
            available_anomalies = [a for a in ALL_ANOMALIES if a not in seen_anomalies_this_run]

            if not available_anomalies:
                print("DEBUG: All anomalies seen. Resetting list.")
                seen_anomalies_this_run.clear()
                available_anomalies = list(ALL_ANOMALIES)

            anomaly_type = random.choice(available_anomalies)
            seen_anomalies_this_run.append(anomaly_type)

            if anomaly_type == ANOMALY_SHADOW_MAN:
                global shadow_x
                shadow_x = 400
                shadow_y = 300

            if anomaly_type == ANOMALY_LEAVE_MSG:
                msg_count = 0
                msg_timer = 0.0
                msg_triggered = False

            print(f"DEBUG: ANOMALY PRESENT (Type: {anomaly_type})")
        else:
            is_anomaly_present = False
            anomaly_type = 0
            print("DEBUG: No Anomaly.")


# --- 1. 초기화 ---
open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)

# 객체 생성
player = Boy()
background_manager = Background()

black_pixel = load_image('black_pixel.png')
title_screen_image = load_image('title.png')
title_font = load_font('ariblk.ttf', 30)
ui_font = load_font('ariblk.ttf', 24)
inst_font = load_font('ariblk.ttf',20)
title_bgm = load_music('bgm_1.mp3')
game_bgm = load_music('bgm_2.mp3')
title_bgm.set_volume(32)
game_bgm.set_volume(32)
title_bgm.repeat_play()
door_se = load_wav('door sound.wav')
door_se.set_volume(50)

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

        # [타이틀 화면]
        elif current_state == STATE_TITLE:
            if event.type == SDL_KEYDOWN:
                current_state = STATE_INSTRUCTIONS
        elif current_state == STATE_INSTRUCTIONS:
            if event.type == SDL_KEYDOWN:
                current_state = STATE_GAMEPLAY
                title_bgm.stop()
                game_bgm.repeat_play()


        # [상호작용 E키]
        elif event.type == SDL_KEYDOWN and event.key == SDLK_e:
            if current_state == STATE_GAMEPLAY:
                if current_room_index == 0:

                    if anomaly_type != ANOMALY_ALL_GONE:

                      if check_collision(player.x, player.y, MONA_X, MONA_Y, INTERACTION_DISTANCE):
                          current_state = STATE_VIEWING_ART
                          currently_viewing_art = ART_MONALISA
                      elif check_collision(player.x, player.y, STARRY_NIGHT_X, STARRY_NIGHT_Y, INTERACTION_DISTANCE):
                          current_state = STATE_VIEWING_ART
                          currently_viewing_art = ART_STARRY_NIGHT
                      elif check_collision(player.x, player.y, ISLAND_X, ISLAND_Y, INTERACTION_DISTANCE):
                          current_state = STATE_VIEWING_ART
                          currently_viewing_art = ART_ISLAND
                      elif check_collision(player.x, player.y, EATING_PLANET_X, EATING_PLANET_Y, INTERACTION_DISTANCE):
                          current_state = STATE_VIEWING_ART
                          currently_viewing_art = ART_EATING_PLANET
                      else:
                          if anomaly_type == ANOMALY_VENUS_CENTER:
                              target_venus_x, target_venus_y = VENUS_CENTER_X, VENUS_CENTER_Y
                          else:
                              target_venus_x, target_venus_y = VENUS_X, VENUS_Y
                          if check_collision(player.x, player.y, target_venus_x, target_venus_y, 200):
                              current_state = STATE_VIEWING_ART
                              currently_viewing_art = ART_VENUS
                          elif check_collision(player.x, player.y, MAN_BUST_X, MAN_BUST_Y, 150):
                              current_state = STATE_VIEWING_ART
                              currently_viewing_art = ART_MAN_BUST

            elif current_state == STATE_VIEWING_ART:
                current_state = STATE_GAMEPLAY
                currently_viewing_art = ART_NONE
                player.dir_x, player.dir_y = 0, 0
                get_events()

        # [그 외 입력]
        elif current_state != STATE_VIEWING_ART:
            player.handle_event(event)

    # 4. 논리 계산 (업데이트)
    if current_state == STATE_GAMEPLAY:
        current_obstacles = []

        # [1번 방: 탈출/성공 방]
        if current_room_index == 1:

            room_change_status = player.update(current_obstacles)
            if room_change_status == 'PREV':
                door_se.play()
                current_state = STATE_FADING_OUT
                transition_target_room = 0
                success_count = 0
                seen_anomalies_this_run.clear()
                transition_player_pos_x = player.boundary_right
                fade_alpha = 0.0


        # [0번 방: 판단 방]
        elif current_room_index == 0:

            if anomaly_type != ANOMALY_ALL_GONE:
                if anomaly_type == ANOMALY_VENUS_CENTER:
                    obs_x, obs_y = VENUS_CENTER_X, VENUS_CENTER_Y
                else:
                    obs_x, obs_y = VENUS_X, VENUS_Y

                current_obstacles.append((obs_x, obs_y, VENUS_W * 0.6, VENUS_H * 0.3))
                current_obstacles.append((MAN_BUST_X, MAN_BUST_Y, MAN_BUST_W * 0.5, MAN_BUST_H * 0.3))

            room_change_status = player.update(current_obstacles)

            if anomaly_type == ANOMALY_LEAVE_MSG:
                if not msg_triggered and player.x > 260:
                    msg_triggered = True

                if msg_triggered:
                    msg_timer += 0.01
                    if msg_timer > 0.15:
                        msg_count += 1
                        msg_timer = 0
                        if msg_count > 15: msg_count = 20


            if anomaly_type == ANOMALY_SHADOW_MAN:
                if player.x > shadow_x:
                   shadow_x += shadow_speed
                   shadow_dir = 1
                elif player.x < shadow_x:
                   shadow_x -= shadow_speed
                   shadow_dir = -1
                if player.y > shadow_y:
                    shadow_y += shadow_speed
                elif player.y < shadow_y:
                    shadow_y -= shadow_speed



                if abs(player.x - shadow_x) < 35 and abs(player.y - shadow_y) < 70:
                    print("CAUGHT! RESET!")
                    current_state = STATE_FADING_OUT
                    transition_target_room = 0
                    success_count = 0
                    seen_anomalies_this_run.clear()
                    transition_player_pos_x = player.boundary_left
                    fade_alpha = 0.0


            if room_change_status == 'NEXT' or room_change_status == 'PREV':
                door_se.play()
                is_correct_choice = False
                # 정답 판별 로직
                if room_change_status == 'NEXT' and not is_anomaly_present:
                    is_correct_choice = True
                elif room_change_status == 'PREV' and is_anomaly_present:
                    is_correct_choice = True

                if is_correct_choice:
                    success_count += 1
                else:
                    success_count = 0
                    seen_anomalies_this_run.clear()
                    print("DEBUG: Wrong choice! Resetting anomaly list.")

                # 목표 달성 확인
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
            if current_room_index == 0:
                setup_new_room()
            else:
                is_anomaly_present = False
                anomaly_type = 0

            player.x = transition_player_pos_x

            if anomaly_type == ANOMALY_PLAYER_GIANT:
                player.y = 350
                if player.x < 400:
                    player.x = 100
                else:
                    player.x = 700

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


    # 5. 그리기 (렌더링)
    clear_canvas()


    def draw_ui_text():
        if current_room_index == 0:
            ui_font.draw(700, 570, f"{success_count} / {FINAL_SUCCESS_COUNT}", (255, 255, 255))
        elif current_room_index == 1:
            ui_font.draw(720, 570, "EXIT", (0, 255, 0))


    # [타이틀]
    if current_state == STATE_TITLE:
        title_screen_image.draw(400, 300, 800, 600)
        title_font.draw(180, 100, "press any key to start game", (255, 255, 255))
    elif current_state == STATE_INSTRUCTIONS:
        black_pixel.opacify(1.0)
        black_pixel.draw(400, 300, 800, 600)

        inst_font.draw(50, 480, "You were in a strange space for an unknown reason", (255, 255, 255))
        inst_font.draw(50, 450, "while you were looking at an art gallery.", (255, 255, 255))

        inst_font.draw(50, 400, "You have to go through seven rooms", (255, 255, 255))
        inst_font.draw(50, 370, "to escape from that space.", (255, 255, 255))

        inst_font.draw(50, 320, "Move: Arrow Keys | Dash: SHIFT | Interact: E", (255, 255, 255))

        inst_font.draw(50, 270, "Move to the LEFT if you find an 'abnormal phenomenon',", (255, 255, 255))
        inst_font.draw(50, 240, "and to the RIGHT if you do not find it.", (255, 255, 255))

        title_font.draw(200, 100, "'Press Any Key to Start'", (255, 255, 255))

    # [게임 플레이 / 암전 / 밝아짐 / 딜레이]
    elif current_state == STATE_GAMEPLAY or current_state == STATE_FADING_OUT or \
            current_state == STATE_FADING_IN or current_state == STATE_POST_FADE_DELAY:

        # 1. 배경 및 그림 그리기 (background_manager 사용!)

        background_manager.draw(current_room_index, anomaly_type, player.x, shadow_x, shadow_y, shadow_dir, msg_count)

        # 2. UI 그리기
        draw_ui_text()

        # 3. 캐릭터 거대화 이상현상 처리
        if anomaly_type == ANOMALY_PLAYER_GIANT:
            player.current_w = player.original_w * 3
            player.current_h = player.original_h * 3
        else:
            player.current_w = player.original_w
            player.current_h = player.original_h

        # 4. 캐릭터 그리기
        player.draw()

        background_manager.draw_foreground(current_room_index, anomaly_type)

    # [그림 확대 보기]
    elif current_state == STATE_VIEWING_ART:

        background_manager.draw_zoomed(currently_viewing_art, anomaly_type)

    # [페이드 효과]
    if current_state == STATE_FADING_OUT or current_state == STATE_FADING_IN:
        black_pixel.opacify(fade_alpha)
        black_pixel.draw(400, 300, 800, 600)

    update_canvas()
    delay(0.01)

# --- 6. 종료 ---
close_canvas()