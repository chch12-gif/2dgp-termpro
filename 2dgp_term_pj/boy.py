# boy.py

from pico2d import *


class Boy:

    def __init__(self):
        # 이미지 로드
        self.ch_front = load_image('character.png')
        self.ch_side = load_image('side.png')
        self.ch_back = load_image('back.png')
        self.ch_run_1 = load_image('left_run.png')
        self.ch_run_2 = load_image('left_run_2.png')

        # 크기 설정
        self.scale = 0.3
        self.frame_w_orig = self.ch_front.w
        self.frame_h_orig = self.ch_front.h
        self.new_width = self.frame_w_orig * self.scale
        self.new_height = self.frame_h_orig * self.scale

        self.boundary_bottom = 260
        self.boundary_top = 440

        self.boundary_left = 0 + self.new_width // 2
        self.boundary_right = 800 - self.new_width // 2
        # 위치 및 속도 설정
        self.x = 400
        self.y = 300  # 바닥 타일 중앙(y=300)으로 설정
        self.walk_speed = 5
        self.run_speed = 10
        self.current_speed = self.walk_speed

        # 상태 변수
        self.dir_x = 0
        self.dir_y = 0
        self.running_state = False
        self.animation_frame = 0


    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_RIGHT:
                self.dir_x += 1
            elif event.key == SDLK_LEFT:
                self.dir_x -= 1
            elif event.key == SDLK_UP:
                self.dir_y += 1
            elif event.key == SDLK_DOWN:
                self.dir_y -= 1
            elif event.key == SDLK_LSHIFT or event.key == SDLK_RSHIFT:
                self.running_state = True
                self.current_speed = self.run_speed
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_RIGHT:
                self.dir_x -= 1
            elif event.key == SDLK_LEFT:
                self.dir_x += 1
            elif event.key == SDLK_UP:
                self.dir_y -= 1
            elif event.key == SDLK_DOWN:
                self.dir_y += 1
            elif event.key == SDLK_LSHIFT or event.key == SDLK_RSHIFT:
                self.running_state = False
                self.current_speed = self.walk_speed


    def update(self):

        potential_y = self.y + self.dir_y * self.current_speed
        if self.boundary_bottom <= potential_y <= self.boundary_top:
            self.y = potential_y

        potential_x = self.x + self.dir_x * self.current_speed

        if potential_x > self.boundary_right and self.dir_x > 0:
            self.x = self.boundary_right
            return 'NEXT'

        elif potential_x < self.boundary_left and self.dir_x < 0:
            self.x = self.boundary_left
            return 'PREV'
        self.x = potential_x

        if self.x < self.boundary_left:
            self.x = self.boundary_left
        elif self.x > self.boundary_right:
            self.x = self.boundary_right

        if self.running_state and (self.dir_x != 0 or self.dir_y != 0):
            self.animation_frame = int(get_time() * 10) % 2
        else:
            self.animation_frame = 0

        return 'NONE'


    def draw(self):
        image_to_draw = self.ch_front
        flip_option = ''

        if self.dir_x == 0 and self.dir_y == 0:
            image_to_draw = self.ch_front
        elif self.running_state and (self.dir_x != 0 or self.dir_y != 0):
            if self.animation_frame == 0:
                image_to_draw = self.ch_run_1
            else:
                image_to_draw = self.ch_run_2

            if self.dir_x > 0:
                flip_option = 'h'
            elif self.dir_x < 0:
                flip_option = ''
            else:
                flip_option = ''
        elif self.dir_x != 0:
            image_to_draw = self.ch_side
            if self.dir_x > 0:
                flip_option = 'h'
            else:
                flip_option = ''
        elif self.dir_y > 0:
            image_to_draw = self.ch_back
        elif self.dir_y < 0:
            image_to_draw = self.ch_front

        image_to_draw.composite_draw(
            0, flip_option,
            self.x, self.y, self.new_width, self.new_height
        )