from os import environ
from random import randint, choice

import pygame as pg
from pygame.locals import *

environ["SDL_VIDEO_WINDOW_POS"] = "100, 100"

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = (800, 600)
INVADER_START_POS = (170, 100)
INVADER_ROWS, INVADER_COLUMNS = (5, 11)
INVADER_GAP = (46, 41)
INVADERS_CONFIG = {
    0: (("a0", "a1"), (26, 26), 40),
    1: (("b0", "b1"), (32, 26), 20),
    2: (("b0", "b1"), (32, 26), 20),
    3: (("c0", "c1"), (35, 26), 10),
    4: (("c0", "c1"), (35, 26), 10)
}
FPS = 60
# https://fonts2u.com/space-invaders-regular.font
FONT = "font/space_invaders.ttf"
BUNKER_STRUCTURE = [
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
]


class Player(pg.sprite.Sprite):
    position = (400, 550)

    def __init__(self, image):
        super().__init__()
        self.size = (50, 25)
        self.move_x = 5
        self.bounds = pg.Rect(10, 538, 780, 25)
        self.image = pg.transform.scale(image, self.size)
        self.rect = self.image.get_rect(center=self.position)
        self.missile_move = -10

    def shoot(self):
        return Missile(self.rect.midtop, self.missile_move)

    def update(self, keys, *args):
        if keys[K_LEFT]:
            self.rect.move_ip(-self.move_x, 0)
        if keys[K_RIGHT]:
            self.rect.move_ip(self.move_x, 0)
        self.rect.clamp_ip(self.bounds)


class Invader(pg.sprite.Sprite):
    move = move_x, move_y = (10, 0)
    moved_down = False
    bottom_bound = 538

    def __init__(self, images, position, size, row):
        super().__init__()
        self.images = [pg.transform.scale(img, size) for img in images]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=position)
        self.left_bound, self.right_bound = (22, 778)
        self.missile_move = 5
        self.row = row

    def animate(self):
        self.index = 1 - self.index
        self.image = self.images[self.index]

    def is_on_edge(self):
        return self.rect.left <= self.left_bound or self.rect.right >= self.right_bound

    def shoot(self):
        return Missile(self.rect.midbottom, self.missile_move)

    def update(self, keys, time_to_move, *args):
        if time_to_move:
            self.animate()
            self.rect.move_ip(self.move)


class Mystery(pg.sprite.Sprite):
    pos = pos_left = (-25, 55)
    pos_right = (825, 55)
    move_x = 3

    def __init__(self, image, sound):
        super().__init__()
        self.size = (50, 20)
        self.image = pg.transform.scale(image, self.size).convert()
        self.rect = self.image.get_rect(center=self.pos)
        self.sound = sound
        self.sound.play(loops=-1)
        self.left_bound, self.right_bound = (0, 800)

    def off_screen(self):
        return self.rect.right <= self.left_bound or self.rect.left >= self.right_bound

    def update(self, *args):
        self.rect.move_ip(self.move_x, 0)
        if self.off_screen():
            self.sound.stop()
            self.kill()


class Missile(pg.sprite.Sprite):
    def __init__(self, position, move):
        super().__init__()
        self.size = (3, 10)
        self.image = pg.Surface(self.size)
        self.image.fill(pg.Color("White"))
        self.rect = self.image.get_rect(center=position)
        self.move_y = move

    def is_off_screen(self):
        return self.rect.top <= 0 or self.rect.bottom >= 600

    def update(self, *args):
        self.rect.move_ip(0, self.move_y)
        if self.is_off_screen():
            self.kill()


class Explosion(pg.sprite.Sprite):
    def __init__(self, image, position):
        super().__init__()
        self.size = (26, 26)
        self.image = pg.transform.scale(image, self.size)
        self.rect = self.image.get_rect(center=position)
        self.duration = 200
        self.time_created = pg.time.get_ticks()

    def update(self, keys, time_to_move, current_time, *args):
        if current_time - self.time_created > self.duration:
            self.kill()


class SpriteSheet(pg.sprite.Sprite):
    def __init__(self, image, position, size=(1350, 150), sprites_in_row=9, rows=2):
        super().__init__()
        self.size = self.size_width, self.size_height = size
        self.sprites_in_row = sprites_in_row
        self.rows = rows
        self.sprite_width, self.sprite_height = (self.size_width // self.sprites_in_row, self.size_height // self.rows)
        self.sprites_sheet = pg.transform.scale(image, self.size)
        self.sprite_list = self.create_sprites_list()
        self.index = 0
        self.image = self.sprite_list[self.index]
        self.rect = self.image.get_rect(center=position)
        self.time_created = pg.time.get_ticks()
        self.last_sprite_time = pg.time.get_ticks()
        self.counter = 0

    def create_sprites_list(self):
        sprite_list = []
        for row in range(self.rows):
            for sprite in range(self.sprites_in_row):
                sprite_list.append(self.sprites_sheet.subsurface(
                    self.sprite_width * sprite, self.sprite_height * row,
                    self.sprite_width, self.sprite_height))
        return sprite_list

    def update(self, keys, time_to_move, current_time, *args):
        if current_time - self.time_created < 1500:
            if current_time - self.last_sprite_time > 80:
                self.index = self.counter % 18
                self.image = self.sprite_list[self.index]
                self.counter += 1
                self.last_sprite_time += 80
        else:
            self.kill()


class Text(pg.sprite.Sprite):
    def __init__(self, txt, pos, font, font_size=16, font_color="Cyan"):
        super().__init__()
        self.pos = pos
        self.font = pg.font.Font(font, font_size)
        self.font_color = pg.Color(font_color)
        self.image = self.font.render(txt, True, self.font_color)
        self.rect = self.image.get_rect(topleft=self.pos)


class UpdatedText(Text):
    def update(self, keys, time_to_move, current_time, txt, *args):
        self.image = self.font.render(txt, True, self.font_color)


class BlinkingText(Text):
    def __init__(self, txt, pos, font):
        super().__init__(txt, pos, font)
        self.rect = self.image.get_rect(center=pos)
        self.txt_image = self.font.render(txt, True, self.font_color)
        self.blank_image = self.font.render("", True, self.font_color)
        self.time_created = pg.time.get_ticks()
        self.display_txt_image_time = 50
        self.total_time = 1500
        self.stop_blinking_time = 750

    def update(self, keys, time_to_move, current_time, *args):
        if current_time - self.time_created > self.total_time:
            self.kill()
        elif current_time % 100 < self.display_txt_image_time or \
                current_time - self.time_created > self.stop_blinking_time:
            self.image = self.txt_image
        else:
            self.image = self.blank_image


class PlayerLife(pg.sprite.Sprite):
    def __init__(self, image, position, size=(30, 15)):
        super().__init__()
        self.image = pg.transform.scale(image, size)
        self.rect = self.image.get_rect(center=position)


class BunkerRect(pg.sprite.Sprite):
    size = width, height = (5, 5)

    def __init__(self, pos):
        super().__init__()
        self.image = pg.Surface(self.size)
        self.image.fill(pg.Color("green"))
        self.rect = self.image.get_rect(topleft=pos)


class Game:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.main_sound = []

        self.game_over = False
        self.game_started = False
        self.game_paused = False
        self.player_destroyed = False
        self.player_shielded = False

        self.player = None
        self.mystery = None
        self.invaders_last_move_time = None
        self.mystery_created_time = None
        self.game_paused_time = None

        self.player_destroyed_time = 0
        self.player_reset_time = 2000
        self.player_score = 0
        self.player_remaining_lives = 2
        self.level = 1
        self.extra_lives_gained = 0
        self.invaders_animate_time = 800
        self.max_invader_speed = 50
        self.mystery_animate_time = randint(7500, 20000)
        self.main_sound_index = 0
        self.game_paused_duration = 2000

        self.all_sprites = pg.sprite.Group()
        self.player_grp = pg.sprite.GroupSingle()
        self.invader_grp = pg.sprite.Group()
        self.lowermost_invaders = pg.sprite.Group()
        self.mystery_grp = pg.sprite.GroupSingle()
        self.player_missile_grp = pg.sprite.Group()
        self.invader_missile_grp = pg.sprite.Group()
        self.text_grp = pg.sprite.Group()
        self.life_grp = pg.sprite.Group()
        self.bunker_grp = pg.sprite.Group()
        self.game_paused_grp = pg.sprite.Group()

        self.start_game()

    def start_game(self):
        self.load_images()
        self.load_sounds()
        self.create_text()
        self.create_lives(self.player_remaining_lives)

    def create_sprites(self):
        self.create_player()
        self.create_invaders()
        self.create_bunkers()
        self.mystery_created_time = pg.time.get_ticks()

    def load_images(self):
        # background.jpg: https://www.allwallpaper.in/outer-space-stars-wallpaper-16838.html
        image_names = ["a0", "a1", "b0", "b1", "c0", "c1",
                       "explosion", "explosion_9x2", "mystery", "player", "player_shield", "start"]

        for img in image_names:
            self.images[img] = pg.image.load(f"images/{img}.png").convert()
            self.images[img].set_colorkey(pg.Color("Black"))

        self.images["background"] = pg.image.load("images/background.jpg").convert()

    def load_sounds(self):
        # extra_life: https://freesound.org/people/plasterbrain/sounds/397355/
        # invader_kill: http://www.classicgaming.cc/classics/space-invaders/sounds
        # mystery: http://www.classicgaming.cc/classics/space-invaders/sounds
        # mystery_kill: https://freesound.org/people/Kodack/sounds/258020/
        # player_kill: https://freesound.org/people/Quaker540/sounds/245372/
        # player_shoot: http://www.classicgaming.cc/classics/space-invaders/sounds
        #
        # main_sound: https://freesound.org/people/PlanetroniK/sounds/371060/
        # main_sound conversion: https://www.conversion-tool.com/?lang=en
        # main_sound pitch shifting: http://onlinetonegenerator.com/pitch-shifter.html

        sound_names = ["extra_life", "invader_kill", "mystery", "mystery_kill", "player_kill", "player_shoot"]
        self.sounds = {name: pg.mixer.Sound(f"sounds/{name}.ogg") for name in sound_names}
        self.main_sound = [pg.mixer.Sound(f"sounds/move{i}.ogg") for i in range(4)]

        self.sounds["player_kill"].set_volume(0.25)
        self.sounds["mystery_kill"].set_volume(0.5)

    def create_player(self):
        image = self.images["player_shield"] if self.player_shielded else self.images["player"]
        self.player = Player(image)
        self.player_grp.add(self.player)
        self.all_sprites.add(self.player)

    def create_invaders(self):
        invaders_pos_y = min(INVADER_START_POS[1] + (self.level - 1) * 20, 200)

        for column in range(INVADER_COLUMNS):
            for row in range(INVADER_ROWS):
                invader_pos = (INVADER_START_POS[0] + column * INVADER_GAP[0],
                               invaders_pos_y + row * INVADER_GAP[1])
                images = [self.images[img] for img in INVADERS_CONFIG[row][0]]
                size = INVADERS_CONFIG[row][1]
                invader = Invader(images, invader_pos, size, row)
                self.invader_grp.add(invader)
                if row == INVADER_ROWS - 1:
                    self.lowermost_invaders.add(invader)

        self.all_sprites.add(self.invader_grp)
        self.invaders_last_move_time = pg.time.get_ticks()

    def create_mystery(self):
        if Invader.move_x > 0:
            Mystery.pos = Mystery.pos_left
            Mystery.move_x = 3
        else:
            Mystery.pos = Mystery.pos_right
            Mystery.move_x = -3

        self.mystery = Mystery(self.images["mystery"], self.sounds["mystery"])
        self.mystery_grp.add(self.mystery)
        self.all_sprites.add(self.mystery)

        self.mystery_animate_time = randint(7500, 20000)
        self.mystery_created_time = pg.time.get_ticks()

    def create_player_missile(self):
        self.sounds["player_shoot"].play()
        missile = self.player.shoot()
        self.player_missile_grp.add(missile)
        self.all_sprites.add(missile)

    def create_invader_missile(self):
        num = randint(1, 1000)

        if num < 7 + self.level * 3:
            invader_to_shoot = choice(self.lowermost_invaders.sprites())
            invader_missile = invader_to_shoot.shoot()
            self.invader_missile_grp.add(invader_missile)
            self.all_sprites.add(invader_missile)

    def create_text(self):
        score_text = Text("SCORE", (15, 15), FONT)
        lives_text = Text("LIVES", (730, 15), FONT)
        player_score_text = UpdatedText(f"{self.player_score}", (80, 15), FONT)
        self.text_grp.add(score_text, lives_text, player_score_text)
        self.all_sprites.add(score_text, lives_text, player_score_text)

    def create_game_over_screen(self):
        self.sounds["mystery"].stop()
        self.all_sprites.remove(self.invader_grp,
                                self.mystery_grp,
                                self.invader_missile_grp,
                                self.player_missile_grp,
                                self.bunker_grp)

        press_key_string = "Press N for new game or ESC to exit"
        press_key_pos = (SCREEN_WIDTH / 2, 450)
        press_key_text = Text(press_key_string, press_key_pos, FONT, 20)
        press_key_text.rect.center = press_key_text.pos

        game_over_string = "Game Over"
        game_over_pos = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        game_over_text = Text(game_over_string, game_over_pos, FONT, 36)
        game_over_text.rect.center = game_over_text.pos

        self.text_grp.add(press_key_text, game_over_text)

    def create_game_paused_screen(self):
        self.sounds["mystery"].stop()
        self.all_sprites.remove(self.mystery_grp, self.invader_missile_grp)
        self.mystery_grp.empty()
        self.invader_missile_grp.empty()
        level_str = f"LEVEL {self.level}"
        level_pos = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        level_txt = Text(level_str, level_pos, FONT, 30)
        level_txt.rect.center = level_txt.pos
        self.game_paused_grp.add(level_txt, self.text_grp, self.life_grp)

    def create_lives(self, lives):
        distance = 40
        pos_x, pox_y = (705 - distance * len(self.life_grp), 23)

        for i in range(lives):
            player_life = PlayerLife(self.images["player"], (pos_x - i * distance, pox_y))
            self.life_grp.add(player_life)
            self.all_sprites.add(player_life)

    def create_bunkers(self):
        total_bunkers = 4
        bunker_distance = 175
        bunker_start_pos_x, bunker_start_pos_y = (105, 400)

        for i in range(total_bunkers):
            pos_y = bunker_start_pos_y
            for row in BUNKER_STRUCTURE:
                pos_x = bunker_start_pos_x + i * bunker_distance
                for num in row:
                    if num:
                        bunker_rect = BunkerRect((pos_x, pos_y))
                        self.bunker_grp.add(bunker_rect)
                    pos_x += BunkerRect.width
                pos_y += BunkerRect.height

        self.all_sprites.add(self.bunker_grp)

    def calculate_score(self, row):
        if row == "Mystery":
            return choice([50, 100, 150, 200, 250, 300])
        else:
            return INVADERS_CONFIG[row][2]

    def update_score(self, score):
        self.player_score += score

        if self.player_score // 5000 > self.extra_lives_gained:
            self.extra_life()

    def extra_life(self):
        self.player_remaining_lives += 1
        self.extra_lives_gained += 1
        self.sounds["extra_life"].play()
        self.create_lives(1)

    def reset_invaders(self):
        Invader.move = Invader.move_x, Invader.move_y = (10, 0)
        Invader.moved_down = False
        self.invaders_animate_time = 800
        self.main_sound_index = 0
        self.mystery_created_time = pg.time.get_ticks()
        self.create_invaders()

    def reset_player(self, current_time):
        time_to_reset_player = current_time - self.player_destroyed_time > self.player_reset_time

        if time_to_reset_player:
            if self.player_remaining_lives < 0:
                self.create_game_over_screen()
                self.game_over = True
            elif self.player_reset_time == 2000:
                self.create_player()
                self.player_reset_time += 3000
            else:
                Player.position = self.player.rect.center
                self.player_shielded = False
                self.player.kill()
                self.create_player()
                self.player_destroyed = False
                self.player_reset_time = 2000

    def play_main_sound(self):
        self.main_sound_index %= 4
        self.main_sound[self.main_sound_index].play()
        self.main_sound_index += 1

    def lowest_invader_position(self):
        return max(inv.rect.bottom for inv in self.lowermost_invaders.sprites())

    def check_collisions(self):
        missile_invader_collision = pg.sprite.groupcollide(self.player_missile_grp, self.invader_grp, True, False)
        missile_player_collision = pg.sprite.groupcollide(self.invader_missile_grp, self.player_grp, True, False)
        missile_mystery_collision = pg.sprite.groupcollide(self.player_missile_grp, self.mystery_grp, True, False)

        pg.sprite.groupcollide(self.player_missile_grp, self.invader_missile_grp, True, True)
        pg.sprite.groupcollide(self.invader_missile_grp, self.bunker_grp, True, True)
        pg.sprite.groupcollide(self.player_missile_grp, self.bunker_grp, True, True)
        pg.sprite.groupcollide(self.invader_grp, self.bunker_grp, False, True)

        if missile_invader_collision:
            collided_invader = list(missile_invader_collision.values())[0][0]
            self.process_missile_invader_collision(collided_invader)

        if missile_player_collision:
            self.process_missile_player_collision()

        if missile_mystery_collision:
            self.process_missile_mystery_collision()

    def process_missile_invader_collision(self, collided_invader):
        if collided_invader in self.lowermost_invaders:
            collided_invader_idx = self.invader_grp.sprites().index(collided_invader)
            next_lowermost_invader = self.invader_grp.sprites()[collided_invader_idx - 1]
            if next_lowermost_invader not in self.lowermost_invaders:
                self.lowermost_invaders.add(next_lowermost_invader)

        self.sounds["invader_kill"].play()
        collided_invader_pos = collided_invader.rect.center
        self.update_score(self.calculate_score(collided_invader.row))
        collided_invader.kill()
        self.all_sprites.add(Explosion(self.images["explosion"], collided_invader_pos))
        self.process_invaders_speed(10)

        if not self.invader_grp:
            self.level += 1
            self.create_game_paused_screen()
            self.game_paused_time = pg.time.get_ticks()
            self.game_paused = True

    def process_missile_player_collision(self):
        if not self.player_shielded:
            self.player_destroyed_time = pg.time.get_ticks()
            self.player_destroyed = True
            self.sounds["player_kill"].play()
            player_pos = self.player.rect.center
            Player.position = player_pos
            self.player.kill()
            self.all_sprites.add(SpriteSheet(self.images["explosion_9x2"], player_pos))
            self.player_remaining_lives -= 1

            if self.life_grp:
                self.life_grp.sprites()[-1].kill()
                self.player_shielded = True

    def process_missile_mystery_collision(self):
        mystery_pos = self.mystery.rect.center
        self.sounds["mystery"].stop()
        self.sounds["mystery_kill"].play()
        self.mystery.kill()
        score = self.calculate_score("Mystery")
        self.update_score(score)
        self.all_sprites.add(BlinkingText(f"{score}", mystery_pos, FONT))

    def process_invaders(self):
        self.play_main_sound()
        self.invaders_last_move_time += self.invaders_animate_time
        index = -1 if Invader.move_x > 0 else 0
        boundary_invader = self.invader_grp.sprites()[index]

        if self.lowest_invader_position() >= Invader.bottom_bound:
            self.create_game_over_screen()
            self.game_over = True
        elif boundary_invader.is_on_edge() and not Invader.moved_down:
            Invader.move = (0, 30)
            Invader.moved_down = True
        elif Invader.moved_down:
            Invader.move_x *= -1
            Invader.move = (Invader.move_x, Invader.move_y)
            Invader.moved_down = False
            self.process_invaders_speed(25)

    def process_invaders_speed(self, value):
        self.invaders_animate_time = max(self.invaders_animate_time - value, self.max_invader_speed)

    def process_events(self):
        for event in pg.event.get():
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                return True
            if event.type == KEYDOWN and event.key == K_SPACE:
                if not self.player_missile_grp and self.player_grp and not self.game_paused:
                    self.create_player_missile()
            if event.type == KEYDOWN and event.key == K_n:
                if self.game_over:
                    Invader.move = Invader.move_x, Invader.move_y = (10, 0)
                    Invader.moved_down = False
                    Player.position = (SCREEN_WIDTH / 2, 550)
                    self.__init__()
                if not self.game_started:
                    self.game_paused = True
                    self.game_paused_time = pg.time.get_ticks()
                    self.create_game_paused_screen()

    def display_frame(self, screen):
        screen.blit(self.images["background"], (0, 0))

        if self.game_over:
            self.text_grp.draw(screen)

        elif self.game_paused:
            if pg.time.get_ticks() - self.game_paused_time < self.game_paused_duration:
                self.game_paused_grp.update(None, None, None, f"{self.player_score}")
                self.game_paused_grp.draw(screen)
            elif self.game_started:
                self.reset_invaders()
                self.game_paused = False
                self.game_paused_grp.empty()
            else:
                self.create_sprites()
                self.game_paused = False
                self.game_started = True
                self.game_paused_grp.empty()

        elif self.game_started:
            keys = pg.key.get_pressed()
            current_time = pg.time.get_ticks()
            time_to_move_invaders = current_time - self.invaders_last_move_time > self.invaders_animate_time
            time_to_create_mystery = current_time - self.mystery_created_time > self.mystery_animate_time

            if time_to_move_invaders:
                self.process_invaders()

            if time_to_create_mystery:
                self.create_mystery()

            if self.player_destroyed:
                self.reset_player(current_time)

            self.create_invader_missile()
            self.check_collisions()

            self.all_sprites.update(keys, time_to_move_invaders, current_time, f"{self.player_score}")
            self.all_sprites.draw(screen)

        else:
            screen.blit(self.images["start"], (0, 0))

        pg.display.flip()


def main():
    pg.mixer.init(buffer=256)
    pg.init()
    screen = pg.display.set_mode(SCREEN_SIZE)
    pg.display.set_caption("Invaders")
    pg.mouse.set_visible(False)
    clock = pg.time.Clock()
    done = False
    game = Game()

    while not done:
        done = game.process_events()
        game.display_frame(screen)
        clock.tick(FPS)

    pg.quit()


if __name__ == "__main__":
    main()
