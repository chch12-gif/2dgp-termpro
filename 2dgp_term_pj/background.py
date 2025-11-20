from pico2d import *
from config import *

class Background:
    def __init__(self):
        self.image = load_image('BACKGROUND.png')
        self.monalisa = load_image('pic_1.png')
        self.monalisa_smile = load_image('pic_1_2.png')
        self.starry_night = load_image('pic_2.png')
        self.island = load_image('pic_3.png')
        self.eating_planet = load_image('pic_4.png')
        self.hand_print = load_image('hand_print.png')
        self.dark_zone_overlay = load_image('dark.png')
        self.black_man_front = load_image('black_man.png')
        self.black_man_side = load_image('black_man_side.png')
        self.venus = load_image('venus.png')

    def draw(self, room_index, anomaly_type, player_x, shadow_x=0, shadow_y=300 ,shadow_dir=0):
        self.image.draw(400, 300)

        if room_index == 0:
            if anomaly_type == ANOMALY_MONALISA_SMILE:
                self.monalisa_smile.composite_draw(0, '', MONA_X, MONA_Y, MONA_W, MONA_H)
            else:
                self.monalisa.composite_draw(0, '', MONA_X, MONA_Y, MONA_W, MONA_H)

            if anomaly_type == ANOMALY_HAND_PRINT:
                self.hand_print.composite_draw(0, '', HAND_PRINT_X, HAND_PRINT_Y, HAND_PRINT_W, HAND_PRINT_H)

            self.starry_night.composite_draw(0, '', STARRY_NIGHT_X, STARRY_NIGHT_Y, STARRY_NIGHT_W, STARRY_NIGHT_H)
            self.island.composite_draw(0, '', ISLAND_X, ISLAND_Y, ISLAND_W, ISLAND_H)
            self.eating_planet.composite_draw(0, '', EATING_PLANET_X, EATING_PLANET_Y, EATING_PLANET_W, EATING_PLANET_H)
            self.venus.composite_draw(0, '', VENUS_X, VENUS_Y, VENUS_W, VENUS_H)

            if anomaly_type == ANOMALY_SHADOW_MAN:
                if shadow_dir == 1:
                    self.black_man_side.composite_draw(0, '', shadow_x, shadow_y, 70, 140)
                elif shadow_dir == -1:
                    self.black_man_side.composite_draw(0, 'h', shadow_x, shadow_y, 70, 140)
                else:
                    self.black_man_front.composite_draw(0, '', shadow_x, shadow_y, 70, 140)

            if anomaly_type == ANOMALY_DARK_ZONE:
                dark_start, dark_end = 200, 600
                if dark_start < player_x < dark_end:
                    self.dark_zone_overlay.opacify(0.7)
                    self.dark_zone_overlay.draw(400, 300, 800, 600)
                else:
                    self.dark_zone_overlay.opacify(0.0)
        elif room_index == 1:
            pass

    def draw_zoomed(self, viewing_art_id, anomaly_type):
        self.image.draw(400, 300)

        if viewing_art_id == ART_MONALISA:
            if anomaly_type == ANOMALY_MONALISA_SMILE:
                self.monalisa_smile.composite_draw(0, '', 400, 400, MONA_LARGE_W, MONA_LARGE_H)
            else:
                self.monalisa.composite_draw(0, '', 400, 300, MONA_LARGE_W, MONA_LARGE_H)

        elif viewing_art_id == ART_STARRY_NIGHT:
            self.starry_night.composite_draw(0, '', 400, 300, MONA_LARGE_W, MONA_LARGE_H)

        elif viewing_art_id == ART_ISLAND:
            self.island.composite_draw(0, '', 400, 300, MONA_LARGE_W, MONA_LARGE_H)

        elif viewing_art_id == ART_EATING_PLANET:
            self.eating_planet.composite_draw(0, '', 400, 300, MONA_LARGE_W, MONA_LARGE_H)

        elif viewing_art_id == ART_VENUS:
            self.venus.composite_draw(0, '', 400, 300, MONA_LARGE_W, MONA_LARGE_H)

