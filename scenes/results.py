import pygame
from scenes.base import BaseScene

class ResultsScene(BaseScene):
    """Displays mission outcomes, gold rewards, and hero statistic changes at the end of each night."""
    def __init__(self, game):
        super().__init__(game)
        self.results_data = []  # list of dicts: {hero_name, status, outcome, message, stats_change}
        self.gold_earned = 0
        self.continue_button = pygame.Rect(362, 620, 300, 60)
        self.is_game_over = False

    def set_results(self, results_data, gold_earned, is_game_over=False):
        """Initializes results logs for rendering."""
        self.results_data = results_data
        self.gold_earned = gold_earned
        self.is_game_over = is_game_over

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.continue_button.collidepoint(mouse_pos):
                if self.is_game_over:
                    # Reset the game to start over
                    self.game.reset_game()
                else:
                    # Advance to the next day
                    self.game.advance_day()

    def update(self, dt):
        pass

    def draw(self, screen):
        # Deep royal blue/violet night gradient background
        screen.fill((15, 12, 35))

        # Header bar
        pygame.draw.rect(screen, (30, 22, 60), (0, 0, 1024, 110))
        pygame.draw.line(screen, (130, 90, 229), (0, 110), (1024, 110), 2)

        title_font = pygame.font.SysFont("Trebuchet MS", 32, bold=True)
        sub_font = pygame.font.SysFont("Trebuchet MS", 16)
        card_title_font = pygame.font.SysFont("Trebuchet MS", 22, bold=True)
        text_font = pygame.font.SysFont("Arial", 16)

        title_text = "Final Chronicle / Game Results" if self.is_game_over else f"Day {self.game.day_number} Nightly Results"
        lbl_title = title_font.render(title_text, True, (255, 220, 150) if self.is_game_over else (220, 205, 255))
        screen.blit(lbl_title, (40, 20))

        desc_text = "Congratulations on finishing the 3-day cycle! See details below." if self.is_game_over else "Here is what transpired during the day's missions and rest cycle."
        lbl_desc = sub_font.render(desc_text, True, (170, 160, 195))
        screen.blit(lbl_desc, (40, 70))

        # Show mission logs cards (3 columns)
        card_y = 150
        card_w = 280
        card_h = 420
        gap = 42
        
        for idx, res in enumerate(self.results_data):
            hname = res["hero_name"]
            status = res["status"]  # "mission" or "rest"
            outcome = res["outcome"]  # "SUCCESS", "FAILURE", "REST"
            message = res["message"]
            changes = res["stats_change"]

            card_x = 50 + idx * (card_w + gap)
            card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

            # Draw card background
            pygame.draw.rect(screen, (25, 20, 45), card_rect, border_radius=15)
            pygame.draw.rect(screen, (70, 55, 110), card_rect, width=2, border_radius=15)

            # Card Header Color based on outcome
            if outcome == "SUCCESS":
                header_color = (45, 150, 95)
                banner_text = "MISSION SUCCESS"
            elif outcome == "FAILURE":
                header_color = (180, 50, 50)
                banner_text = "MISSION FAILED"
            else:
                header_color = (95, 100, 140)
                banner_text = "HERO RESTED"

            header_rect = pygame.Rect(card_x + 2, card_y + 2, card_w - 4, 60)
            pygame.draw.rect(screen, header_color, header_rect, border_radius=13)
            # Clip bottom corner
            pygame.draw.rect(screen, header_color, (card_x + 2, card_y + 50, card_w - 4, 12))

            # Hero Name & Outcome Text
            lbl_name = card_title_font.render(hname, True, (255, 255, 255))
            screen.blit(lbl_name, (card_x + 20, card_y + 12))

            lbl_banner = sub_font.render(banner_text, True, (255, 255, 255))
            screen.blit(lbl_banner, (card_x + 20, card_y + 36))

            # Render message
            # Wrap text
            words = message.split(' ')
            lines = []
            curr_line = ""
            for word in words:
                test_line = curr_line + " " + word if curr_line else word
                if text_font.size(test_line)[0] < (card_w - 40):
                    curr_line = test_line
                else:
                    lines.append(curr_line)
                    curr_line = word
            if curr_line:
                lines.append(curr_line)

            y_offset = card_y + 90
            for line in lines[:5]:
                lbl_line = text_font.render(line, True, (230, 230, 245))
                screen.blit(lbl_line, (card_x + 20, y_offset))
                y_offset += 22

            # Render statistic delta listings
            y_offset = card_y + 240
            stat_title = card_title_font.render("Metric Changes", True, (196, 175, 255))
            screen.blit(stat_title, (card_x + 20, y_offset))
            y_offset += 30

            for stat, val in changes.items():
                sign = "+" if val >= 0 else ""
                txt_color = (120, 230, 150) if val > 0 else ((255, 120, 120) if val < 0 else (200, 200, 200))
                # For tiredness, negative change is good (less tired), so make green
                if stat in ["tired", "tiredness"] and val < 0:
                    txt_color = (120, 230, 150)
                elif stat in ["tired", "tiredness"] and val > 0:
                    txt_color = (255, 120, 120)

                lbl_stat = text_font.render(f"{stat.capitalize()}: {sign}{val}", True, txt_color)
                screen.blit(lbl_stat, (card_x + 20, y_offset))
                y_offset += 24

        # Mission earnings display
        earned_font = pygame.font.SysFont("Trebuchet MS", 20, bold=True)
        if not self.is_game_over:
            lbl_earn = earned_font.render(f"Mission Gold Earned: +{self.gold_earned}g  |  Total Gold: {self.game.gold}g", True, (255, 200, 50))
            screen.blit(lbl_earn, (screen.get_width()//2 - lbl_earn.get_width()//2, 580))
        else:
            lbl_earn = earned_font.render(f"Final Shop Gold: {self.game.gold}g", True, (255, 200, 50))
            screen.blit(lbl_earn, (screen.get_width()//2 - lbl_earn.get_width()//2, 580))

        # Bottom Continue Button
        mouse_pos = pygame.mouse.get_pos()
        hover = self.continue_button.collidepoint(mouse_pos)
        
        btn_color = (255, 170, 80) if hover else (220, 140, 50)
        pygame.draw.rect(screen, btn_color, self.continue_button, border_radius=10)
        pygame.draw.rect(screen, (255, 220, 180), self.continue_button, width=2, border_radius=10)

        btn_font = pygame.font.SysFont("Trebuchet MS", 20, bold=True)
        btn_text = "Return to Main Title" if self.is_game_over else "Begin Next Day"
        lbl_btn = btn_font.render(btn_text, True, (25, 20, 45) if not hover else (10, 5, 25))
        screen.blit(lbl_btn, (self.continue_button.centerx - lbl_btn.get_width()//2, self.continue_button.centery - lbl_btn.get_height()//2))
