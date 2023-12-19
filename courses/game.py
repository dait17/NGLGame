import sys

import pygame
from entities import Player, Enemy
from cards import Cards


class Game:
    def __init__(self):
        self.screen_size = (800, 600)
        self.screen = pygame.display.set_mode(self.screen_size)
        self.fps = 60
        self.clock = pygame.time.Clock()

        self.background = self.__load_img('./../assets/background.png')
        self.card_panel = self.__load_img('./../assets/panel.png')

        self.__bg_rect = self.background.get_rect()
        self.__cp_rect = self.card_panel.get_rect()
        self.__cp_rect.top = self.screen_size[1] - self.__cp_rect.height

        self.player_attack = True

        self.player = Player(self.screen, (200, 300), 'Player', 100, 20)
        self.player.set_ready_attack(self.player_attack)
        self.player.be_attacked(50)
        self.__init_enemy()
        self.__cur_enemy_attack = 0

        self.__cursor_img = self.__load_img('./../assets/sword.png')
        self.target_enemy :Enemy | None = None

        self.cards = Cards(self.__cp_rect, self.player)

        self.attack_cooldown = 2000
        self.last_attack_time = pygame.time.get_ticks()

        self.__target_point_attack = self.__cur_point_attack(self.player.cur_img_rect)

    def __cur_point_attack(self, entity_rect:pygame.Rect):
        return entity_rect.centerx, entity_rect.top - 6 - 40

    def __load_img(self, img_path: str):
        return pygame.image.load(img_path).convert_alpha()

    def __draw_background(self):
        self.screen.blit(self.background, self.__bg_rect)
        self.screen.blit(self.card_panel, self.__cp_rect)

    def __init_enemy(self):
        enemy1 = Enemy(self.screen, (500, 325), "Green Slime", 1000, 10)
        enemy2 = Enemy(self.screen, (700, 325), "Red Slime", 1000, 10)
        self.enemy_list = [enemy1, enemy2]

    def __enemy_hover_effect(self, enemy: Enemy, mouse_pos):
        if self.player.ready_attack and enemy.cur_img_rect.collidepoint(*mouse_pos):
            pygame.mouse.set_visible(False)
            self.screen.blit(self.__cursor_img, mouse_pos)

    def __set_attack_time(self):
        self.last_attack_time = pygame.time.get_ticks()

    def __select_enemy(self, enemy: Enemy, mouse_pos):
        if self.player.ready_attack and enemy.cur_img_rect.collidepoint(*mouse_pos):
            mouse_press = pygame.mouse.get_pressed(3)
            if mouse_press[0]:
                self.__unselect_enemy()
                self.target_enemy = enemy
                self.target_enemy.set_selected(True)

    def __draw_attack_hl(self):
        if self.player.ready_attack:
            self.screen.blit(self.__cursor_img, self.__target_point_attack)

    def __unselect_enemy(self):
        if self.target_enemy is not None:
            self.target_enemy.set_selected(False)
            self.target_enemy = None

    def __set_enemy_attack(self, enemy):
        enemy.set_ready_attack(True)
        enemy.set_attack()
        self.player.be_attacked(enemy.strength)
        self.__set_attack_time()

    def __get_cur_enemy_attack(self):
        return self.enemy_list[self.__cur_enemy_attack]

    def __control_attack(self):
        valid_time = self.__get_valid_time()

        if self.__cur_enemy_attack>=len(self.enemy_list):
            self.__cur_enemy_attack = 0
            self.player.set_ready_attack(True)
            return

        if len(self.enemy_list)>0 and not self.player.ready_attack and valid_time:
            cur_enemy = self.__get_cur_enemy_attack()
            if not cur_enemy.ready_attack:
                self.__set_enemy_attack(cur_enemy)
                self.__cur_enemy_attack += 1

    def __get_valid_time(self):
        return pygame.time.get_ticks() - self.last_attack_time >= self.attack_cooldown

    def __update_enemy(self):
        mouse_pos = pygame.mouse.get_pos()
        pygame.mouse.set_visible(True)
        for enemy in self.enemy_list:
            enemy.update()
            self.__enemy_hover_effect(enemy, mouse_pos)
            self.__select_enemy(enemy, mouse_pos)
            # self.__control_attack()
            # self.__update_enemy_attack(enemy)

    def run(self):

        while True:
            self.clock.tick(self.fps)
            self.__draw_background()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # self.enemy_green.set_attack()
                        self.player.set_health(20)
                        self.player.set_selected(not self.player.selected)
            # flag player just attack
            play_attack = self.player.ready_attack
            self.player.update()
            self.__update_enemy()
            self.__control_attack()
            self.__draw_attack_hl()
            self.cards.update_target_enemy(self.target_enemy)
            self.cards.update()
            if play_attack and not self.player.ready_attack:
                self.__set_attack_time()
                self.__unselect_enemy()


            pygame.display.flip()
            # pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()
    pygame.quit()
