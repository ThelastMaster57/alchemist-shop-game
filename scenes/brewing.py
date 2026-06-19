# pyrefly: ignore [missing-import]
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
            shop = self.game.scenes["shop"]
            shop.pot_contents = {}
            if self.success:
                # Başarı: gold ver ve sıradaki müşteriye geç
                self.game.gold += self.customer_data.get("reward", 40)
            # Başarı veya başarısızlık fark etmeksizin müşteri gidiyor, bir daha gelmiyor
            shop.current_customer_idx += 1
            shop.load_customer()  # Sıradaki müşteriye geç veya kuyruk bittiyse Heroes'a git

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
            screen.blit(overlay, (0, 0))

            if self.success:
                res_txt  = self.title_font.render("İKSİR BAŞARIYLA ÜRETİLDİ!", True, (100, 255, 100))
                sub_txt  = self.font.render("Altını almak ve sonraki müşteriye geçmek için TIKLA", True, (220, 220, 220))
                screen.blit(res_txt, (512 - res_txt.get_width() // 2, 310))
                screen.blit(sub_txt, (512 - sub_txt.get_width() // 2, 370))
            else:
                res_txt  = self.title_font.render("BAŞARISIZ! İksir Taşarak Bozuldu.", True, (255, 100, 100))
                sub_txt  = self.font.render("Müşteri beklemeye tahammül edemedi ve gitti. (Gold kazanılmadı)", True, (220, 180, 180))
                sub2_txt = self.font.render("Sonraki müşteriye geçmek için TIKLA", True, (180, 180, 180))
                screen.blit(res_txt,  (512 - res_txt.get_width()  // 2, 300))
                screen.blit(sub_txt,  (512 - sub_txt.get_width()  // 2, 360))
                screen.blit(sub2_txt, (512 - sub2_txt.get_width() // 2, 400))