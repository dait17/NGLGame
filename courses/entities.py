import pygame

pygame.font.init()


class Entities:
    def __init__(self, screen, position: tuple[float, float], name: str, max_hp: int, strength: int):
        self.position = position
        self.screen = screen
        self.name = name
        self.max_hp = max_hp
        self.cur_hp = max_hp
        self.strength = strength

        self._animation_list = self.get_animation_list()
        self._animation_cooldow_list = [0.1, 0.3]
        self._cur_animation_id = 0
        self._cur_animation_frame_id = 0

        self.cur_img = self.get_cur_img()
        self.cur_img_rect = self.cur_img.get_rect(topleft=position)

        self._hp_box = None
        self._hp_bg_box = None
        self._hp_text_pos = None
        self._cur_hp_text = None
        self._health_hp = 0
        self._health_per_frame = 2

        self.ready_attack = False

        self.selected = False

        self.alive = True

        self.font = pygame.font.Font(pygame.font.get_default_font(), 14)

    def _control_frame(self):
        self._normalize_animation()
        if self._cur_animation_frame_id >= self.get_len_cur_animation():
            self._cur_animation_frame_id = 0

    def load_img(self, img_path: str):
        try:
            return pygame.image.load(img_path).convert_alpha()
        except Exception as e:
            print(e)
            return None

    def _load_idle_img(self):
        img_list = []
        for i in range(8):
            img = self.load_img(f"./../assets/{self.name}/Idle/{i}.png")
            if img is not None:
                img_list.append(img)
        return img_list

    def _load_attack_img(self):
        img_list = []
        for i in range(6):
            img = self.load_img(f"./../assets/{self.name}/Attack/{i}.png")
            if img is not None:
                img_list.append(img)
        return img_list

    def get_animation_list(self):
        animation_list = [self._load_idle_img(), self._load_attack_img()]
        return animation_list

    def set_ready_attack(self, value: bool):
        self.ready_attack = value

    def set_idle(self):
        self._cur_animation_id = 0
        self._cur_animation_frame_id = 0

    def set_attack(self):
        self._cur_animation_id = 1
        self._cur_animation_frame_id = 0

    def _set_health_effect(self, hp: int):
        self._health_hp += hp

    def set_selected(self, value: bool):
        self.selected = value

    def get_cur_animation_list(self):
        return self._animation_list[self._cur_animation_id]

    def get_len_cur_animation(self):
        return len(self.get_cur_animation_list())

    def get_cur_img(self):
        return self._animation_list[self._cur_animation_id][int(self._cur_animation_frame_id)]

    def get_cur_rect(self):
        img = self.get_cur_img()
        return img.get_rect()

    def _normalize_animation(self):
        if self._cur_animation_id != 0 and self._cur_animation_frame_id >= self.get_len_cur_animation():
            self.set_idle()
            self.ready_attack = False

    def _update_frame(self):
        self._cur_animation_frame_id += self._animation_cooldow_list[self._cur_animation_id]
        self._control_frame()

    def _update_animation(self):
        self.cur_img = self.get_cur_img()
        self.cur_img_rect = self.cur_img.get_rect(topleft=self.position)

    def _get_cur_hp_text(self):
        return self.font.render(f'{self.name} HP: {self.cur_hp}', True, (255, 255, 255))

    def _be_attacked_default(self, damage):
        if self.cur_hp > 0:
            self.cur_hp -= damage
            self._update_hp_display()

        if self.cur_hp <= 0:
            self.alive = False

    # Effect
    def _health_effect(self):
        if self._health_hp > 0 and self.cur_hp<self.max_hp:
            hp_added = min(self._health_per_frame, self._health_hp)
            self.cur_hp += hp_added
            self._health_hp -= hp_added
            self._update_hp_display()
        else:
            self._health_hp = 0

    def _selected_effect(self):
        if self.selected:
            w = self.cur_img_rect.width*1.1
            h = self.cur_img_rect.height*1.1
            self.cur_img = pygame.transform.smoothscale(self.cur_img, (w,h))

            self.cur_img_rect.top = self.cur_img_rect.top - (h - self.cur_img_rect.height)
            self.cur_img_rect.left = self.cur_img_rect.left - (w - self.cur_img_rect.width)

    def _update_hp_display(self):
        self._hp_box.width = self._hp_bg_box.width *( self.cur_hp/self.max_hp)
        self._cur_hp_text = self._get_cur_hp_text()

    def _update_effect(self):
        self._health_effect()
        self._selected_effect()

    def _draw_hp_box(self):
        if self._cur_hp_text is not None and self._hp_text_pos is not None:
            self.screen.blit(self._cur_hp_text, self._hp_text_pos)
        if self._hp_bg_box is not None and self._hp_box is not None:
            pygame.draw.rect(self.screen, (255, 0, 0), self._hp_bg_box)
            pygame.draw.rect(self.screen, (0, 255, 0), self._hp_box)

    def _draw_entities(self):
        self.screen.blit(self.cur_img, self.cur_img_rect)
        self._draw_hp_box()

    def _default_update(self):
        self._update_frame()
        self._update_animation()
        self._update_effect()

        self._draw_entities()

    def update(self):
        self._default_update()


class Player(Entities):
    def __init__(self, screen: pygame.Surface, position: tuple[int, int], name, max_hp, strength):
        super(Player, self).__init__(screen, position, name, max_hp, strength)

        self._hp_bg_box = pygame.Rect(10, 26, 100, 10)
        self._hp_box = pygame.Rect(10, 26, 100, 10)
        self._hp_text_pos = (10, 10)
        self._cur_hp_text = self._get_cur_hp_text()

    def be_attacked(self, damage: int):
        self._be_attacked_default(damage)

    def set_health(self, hp: int):
        self._set_health_effect(hp)


class Enemy(Entities):
    def __init__(self, screen: pygame.Surface, position: tuple[int, int], name, max_hp, strength):
        super(Enemy, self).__init__(screen, position, name, max_hp, strength)
        self.__create_hp_frame()

    def __create_hp_frame(self):
        self._hp_bg_box = pygame.Rect(0, self.cur_img_rect.top - 6, self.cur_img_rect.width - 20,
                                      4)
        self._hp_box = pygame.Rect(0, self.cur_img_rect.top - 6, self.cur_img_rect.width - 20, 4)

        self._hp_bg_box.centerx = self.cur_img_rect.centerx
        self._hp_box.centerx = self.cur_img_rect.centerx

    def be_attacked(self, damage: int):
        self._be_attacked_default(damage)

    def update(self):
        self._default_update()
