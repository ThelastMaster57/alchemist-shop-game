import pygame
import random
from scenes.base import BaseScene

class BrewingScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 20)
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.reset_game()

    def setup_minigame(self, potion_key, customer_data):
        self.potion_key = potion_key
        self.customer_data = customer_data
        self.reset_game()

    def reset_game(self):
        self.temperature = 30.0
        self.target_min = 60.0
        self.target_max = 80.0
        self.duration = 5.0
        self.time_elapsed = 0.0
        self.green_zone_time = 0.0
        self.game_over = False
        self.success = False

    def handle_event(self, event):
        if self.game_over and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.success:
                self.game.gold += self.customer_data.get("reward", 40)
                shop = self.game.scenes["shop"]
                shop.pot_contents = {}
                shop.current_customer_idx += 1
                shop.dialogue_page = 0
                self.game.change_scene("shop")
            else:
                self.game.scenes["shop"].pot_contents = {}
                self.game.change_scene("shop")

    def update(self, dt):
        if self.game_over: return
        self.time_elapsed += dt

        if pygame.mouse.get_pressed()[0]:
            self.temperature += 80.0 * dt
        else:
            self.temperature -= 50.0 * dt

        self.temperature += random.uniform(-15.0, 15.0) * dt
        if self.temperature < 0: self.temperature = 0
        if self.temperature > 100: self.temperature = 100

        if self.target_min <= self.temperature <= self.target_max:
            self.green_zone_time += dt

        if self.time_elapsed >= self.duration:
            self.game_over = True
            if (self.green_zone_time / self.duration) >= 0.65:
                self.success = True
            else:
                self.success = False

    def draw(self, screen):
        screen.fill((30, 24, 42))
        title = self.title_font.render("Kazan Isısı Ayarlanıyor...", True, (240, 220, 100))
        screen.blit(title, (340, 80))

        bar_rect = pygame.Rect(312, 300, 400, 40)
        pygame.draw.rect(screen, (50, 45, 65), bar_rect, border_radius=6)

        green_rect = pygame.Rect(312 + int(self.target_min * 4), 300, int((self.target_max - self.target_min) * 4), 40)
        pygame.draw.rect(screen, (46, 184, 114), green_rect)

        needle_x = 312 + int(self.temperature * 4)
        pygame.draw.line(screen, (255, 65, 65), (needle_x, 285), (needle_x, 355), 5)

        info_txt = self.font.render("FARENİN SOL TIKINI basılı tutarak ibreyi YEŞİL bölgede tut!", True, (200, 200, 200))
        screen.blit(info_txt, (270, 200))

        time_left = max(0, self.duration - self.time_elapsed)
        timer_txt = self.font.render(f"Kalan Süre: {time_left:.1f}s", True, (255, 255, 255))
        screen.blit(timer_txt, (450, 400))

        if self.game_over:
            overlay = pygame.Surface((1024, 768), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0,0))
            if self.success:
                res_txt = self.title_font.render("İKSİR BAŞARIYLA ÜRETİLDİ!", True, (100, 255, 100))
                sub_txt = self.font.render("Altını almak ve sonraki müşteriye geçmek için TIKLA", True, (220, 220, 220))
            else:
                res_txt = self.title_font.render("BAŞARISIZ! İksir Taşarak Bozuldu.", True, (255, 100, 100))
                sub_txt = self.font.render("Dükkana dönmek ve malzemeleri yeniden seçmek için TIKLA", True, (220, 220, 220))
            screen.blit(res_txt, (340, 320))
            screen.blit(sub_txt, (290, 380))