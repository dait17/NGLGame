import json
import os

import pygame
import random
from entities import Player, Enemy


class Cards:
    def __init__(self, panel_area:pygame.Rect, player:Player):
        self.panel_area = panel_area
        self.h_space = 80
        self.__card_info = self.__read_card_info()

        self._len_of_card = 3
        self._card_width = 100
        self.cur_card_list:list[BaseCard] = [self.__random_choice_card() for _ in range(self._len_of_card)]
        self.__init_card_pos()
        self.player = player
        self.target_enemy = None

    def __read_card_info(self):
        with open('./../assets/card.json', 'r') as f:
            return json.load(f)

    def __get_card(self, info:dict):
        if info['type'].lower() == 'attack':
            return AttackCard(info['value'], info['img_path'])
        if info['type'].lower() == 'heal':
            return HealthCard(info['value'], info['img_path'])

    def __random_choice_card(self):
        card_info_list = list(self.__card_info.values())
        card_info = random.choice(card_info_list)
        return self.__get_card(card_info)

    def get_pos_for_card(self):
        start_x = self.panel_area.centerx-self.h_space-self._card_width*1.5
        pos_list = [(start_x, self.panel_area.centery)]
        start_x += self._card_width
        for i in range(1, self._len_of_card):
            start_x += self.h_space
            pos_list.append((start_x, self.panel_area.centery))
            start_x += self._card_width
        print(pos_list)
        return pos_list

    def __init_card_pos(self):
        pos_list = self.get_pos_for_card()
        for index, card in enumerate(self.cur_card_list):
            card.set_center_pos(pos_list[index])

    def pick_card(self):
        for index, card in enumerate(self.cur_card_list):
            card.update()
            card.set_enable_hover(self.player.ready_attack)
            if card.is_hover and pygame.mouse.get_pressed(3)[0]:
                if card.enact(self.player, self.target_enemy):
                    new_card = self.__random_choice_card()
                    new_card.set_center_pos(card.get_center_pos())
                    self.cur_card_list[index] = new_card

    def update_target_enemy(self, target_enemy:Enemy):
        self.target_enemy = target_enemy
        # print(self.target_enemy)

    def update(self):
        self.pick_card()


class BaseCard:
    def __init__(self, value, img_path: str):
        self.screen = pygame.display.get_surface()
        self.value = value
        self.img = self._load_img(img_path)
        self.img_rect = self.img.get_rect()
        self._cur_img = self.img.copy()
        self._cur_img_rect = self.img_rect.copy()

        self.enable_hover = False
        self.is_hover = False

    def _load_img(self, img_path: str):
        try:
            img_path = os.path.join(r'.\..\assets\Cards', img_path)
            return pygame.image.load(img_path).convert_alpha()
        except Exception as e:
            print(e)
            return None

    def set_enable_hover(self, value:bool):
        self.enable_hover = value

    def _draw_card(self):
        self.screen.blit(self._cur_img, self._cur_img_rect)

    def set_center_pos(self, pos: tuple[float, float]):
        self.img_rect.center = pos

    def get_center_pos(self):
        return self.img_rect.center

    def _normalize_card(self):
        self.is_hover = False
        self._cur_img = self.img.copy()
        self._cur_img_rect = self.img_rect.copy()

    # Effect
    def _hover_effect(self):
        if self.enable_hover:
            mouse_pos = pygame.mouse.get_pos()
            if self.img_rect.collidepoint(*mouse_pos):
                self.is_hover = True
                w = self.img_rect.width * 1.1
                h = self.img_rect.height * 1.1
                self._cur_img = pygame.transform.smoothscale(self.img, (w, h))

                self._cur_img_rect.center = self.img_rect.center
            else:
                self._normalize_card()
        else:
            self._normalize_card()

    def enact(self, player, enemy_target):
        pass

    def update(self):
        self._hover_effect()
        self._draw_card()


class HealthCard(BaseCard):
    def __init__(self, value, img_path):
        super(HealthCard, self).__init__(value, img_path)

    def enact(self, player:Player, enemy_target):
        player.set_health(self.value)
        player.set_ready_attack(False)
        return True


class AttackCard(BaseCard):
    def __init__(self, value, img_path):
        super(AttackCard, self).__init__(value, img_path)

    def enact(self, player: Player, enemy_target:Enemy|None):
        if enemy_target is not None:
            player.set_attack()
            enemy_target.be_attacked(self.value)
            player.set_ready_attack(False)
            return True
        return False



