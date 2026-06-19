DAILY_MISSIONS = {
    1: {"name": "Goblins in the Suburbs", "type": "Combat", "desc": "Requires high Strength/Combat focus. Best suited for Aldric."},
    2: {"name": "Magical Anomaly Investigation", "type": "Magic", "desc": "Requires high Intellect/Mana focus. Best suited for Seraphel."},
    3: {"name": "Scouting the Whispering Woods", "type": "Scout", "desc": "Requires high Agility/Speed focus. Best suited for Elysia."}
}

import pygame
from scenes.base import BaseScene

class HeroesScene(BaseScene):
    """Nighttime Status & Affection Scene. Shows all three heroes, their metrics, relationship status, and handles missions/chats."""
    def __init__(self, game):
        super().__init__(game)
        # Modes: "view" (read-only from shop), "missions" (assigning missions), "chat" (initiating night chats)
        self.display_mode = "view"
        
        # Hero names list
        self.hero_names = ["Aldric", "Seraphel", "Elysia"]
        
        # UI Layout: 3 columns for 3 heroes
        self.cards = [
            {"name": "Aldric", "rect": pygame.Rect(50, 180, 280, 420), "color": (45, 95, 150)},
            {"name": "Seraphel", "rect": pygame.Rect(372, 180, 280, 420), "color": (150, 45, 95)},
            {"name": "Elysia", "rect": pygame.Rect(694, 180, 280, 420), "color": (95, 150, 45)}
        ]
        
        # Bottom global confirm button
        self.bottom_button = pygame.Rect(362, 630, 300, 55)
        self.hero_action_buttons = {}  # hero_name -> button Rect

        for idx, card in enumerate(self.cards):
            hname = card["name"]
            self.hero_action_buttons[hname] = pygame.Rect(card["rect"].x + 20, card["rect"].y + 350, 240, 45)

    def set_mode(self, mode):
        """Sets the active display mode: 'view', 'missions', or 'chat'."""
        self.display_mode = mode

    def get_relationship_title(self, hero_affection):
        try:
            import data.characters as characters
            if hasattr(characters, "AFFECTION_BANDS"):
                bands = characters.AFFECTION_BANDS
                if isinstance(bands, list):
                    for band in bands:
                        if len(band) == 3:
                            if band[0] <= hero_affection <= band[1]:
                                return band[2]
                        elif len(band) == 2:
                            if hero_affection <= band[0]:
                                return band[1]
                elif isinstance(bands, dict):
                    for threshold in sorted(bands.keys()):
                        if hero_affection <= threshold:
                            return bands[threshold]
        except Exception as e:
            print(f"Error querying affection bands: {e}")
            
        if hero_affection <= 20: return "Wary"
        elif hero_affection <= 50: return "Associate"
        elif hero_affection <= 80: return "Trusted Ally"
        else: return "Oathbound"

    def get_success_chance(self, hero_name, title):
        hero_data = self.game.runtime_heroes.get(hero_name.lower()) if self.game.runtime_heroes else None
        if not hero_data:
            return 50
            
        day_num = getattr(self.game, "day_number", 1)
        current_mission = DAILY_MISSIONS.get(day_num, {"type": "General"})
        m_type = current_mission["type"]
        
        hero_specialties = {
            "aldric": "Combat",
            "seraphel": "Magic",
            "elysia": "Scout"
        }
        
        if isinstance(hero_data, dict):
            morale = hero_data.get("morale", 50)
            tired = hero_data.get("tired", 0) if "tired" in hero_data else hero_data.get("tiredness", 0)
        else:
            morale = getattr(hero_data, "morale", 50)
            tired = getattr(hero_data, "tired", 0) if hasattr(hero_data, "tired") else getattr(hero_data, "tiredness", 0)
            
        chance = 50 + (morale // 2) - (tired // 2)
        
        if hero_specialties.get(hero_name.lower()) == m_type:
            chance += 30
            
        return max(10, min(95, chance))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            # --- ÖNCELİK: BÜYÜK ALT CONFIRM BUTONU ---
            if self.bottom_button.collidepoint(mouse_pos) or (340 <= mouse_pos[0] <= 680 and 610 <= mouse_pos[1] <= 695):
                
                if self.display_mode == "view":
                    # İzleme modundaysa dükkana geri fırlat
                    for s_name in ["shop", "main_shop", "day_shop"]:
                        if s_name in getattr(self.game, "scenes", {}):
                            self.game.change_scene(s_name)
                            break
                    return
                    
                elif self.display_mode == "missions":
                    self.game.phase = "NIGHT"
                    for hname in self.hero_names:
                        hdata = self.game.runtime_heroes.get(hname.lower()) or self.game.runtime_heroes.get(hname)
                        if hdata:
                            if isinstance(hdata, dict):
                                hdata["chat_completed"] = False
                            else:
                                hdata.chat_completed = False
                    self.set_mode("chat")
                    print("[SİSTEM] Görevler kilitlendi, Gece Sohbet moduna geçildi.")
                    return
                    
                elif self.display_mode == "chat":
                    print("[SİSTEM] Geceyi bitir butonuna basıldı, zorunlu güvenli geçiş tetikleniyor...")
                    
                    # --- NİHAİ ÇÖZÜM: DOĞRUDAN VE ZORUNLU GEÇİŞ BLOKU ---
                    # game.py içindeki fonksiyonları tetiklemeyi dene
                    if hasattr(self.game, "execute_missions_and_results"):
                        self.game.execute_missions_and_results()
                    elif hasattr(self.game, "complete_night"):
                        self.game.complete_night()
                    elif hasattr(self.game, "next_day"):
                        self.game.next_day()
                    
                    # Güvenlik Kilidi: Eğer üstteki fonksiyonlar çalışsa bile sahne değişmediyse manuel olarak zorla değiştir!
                    if hasattr(self.game, "day_number"):
                        self.game.day_number += 1
                    elif hasattr(self.game, "day"):
                        self.game.day += 1
                        
                    # Döngüyü kırmak için oyunu DAY fazına çekip dükkan sahnelerinden birine paslıyoruz
                    self.game.phase = "DAY"
                    for s_name in ["shop", "main_shop", "day_shop"]:
                        if s_name in getattr(self.game, "scenes", {}):
                            print(f"[SİSTEM] Manuel olarak '{s_name}' sahnesine geçiş yapılıyor.")
                            self.game.change_scene(s_name)
                            break
                    return

            # --- KAHRAMAN KARTLARININ İÇİNDEKİ AKSİYON BUTONLARI ---
            for card in self.cards:
                hname = card["name"]
                hero_data = self.game.runtime_heroes.get(hname.lower()) if self.game.runtime_heroes else None
                if not hero_data:
                    continue
                
                btn_rect = self.hero_action_buttons[hname]
                if btn_rect.collidepoint(mouse_pos):
                    if self.display_mode == "missions":
                        if isinstance(hero_data, dict):
                            hero_data["on_mission"] = not hero_data.get("on_mission", False)
                        else:
                            hero_data.on_mission = not getattr(hero_data, "on_mission", False)
                        return
                    elif self.display_mode == "chat":
                        already_chatted = hero_data.get("chat_completed", False) if isinstance(hero_data, dict) else getattr(hero_data, "chat_completed", False)
                        if not already_chatted:
                            self.game.scenes["dialogue"].start_night_dialogue(hname.lower(), self.game.day_number)
                            self.game.change_scene("dialogue")
                            return

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((18, 14, 34))

        # Header bar
        pygame.draw.rect(screen, (35, 25, 65), (0, 0, 1024, 145))
        pygame.draw.line(screen, (130, 90, 229), (0, 145), (1024, 145), 2)

        title_font = pygame.font.SysFont("Trebuchet MS", 32, bold=True)
        sub_font = pygame.font.SysFont("Trebuchet MS", 16)
        
        mode_titles = {
            "view": "Companion Status Roster",
            "missions": "Assign Hero Squad Missions",
            "chat": "Night Quarter Talks"
        }
        
        lbl_title = title_font.render(mode_titles.get(self.display_mode, "Night Quarter Talks"), True, (220, 205, 255))
        screen.blit(lbl_title, (40, 15))

        lbl_day = title_font.render(f"Day {getattr(self.game, 'day_number', 1)}", True, (255, 190, 100))
        screen.blit(lbl_day, (screen.get_width() - lbl_day.get_width() - 40, 15))

        GOLD_TARGETS = {1: 150, 2: 300, 3: 500}
        current_target = GOLD_TARGETS.get(getattr(self.game, 'day_number', 1), 150)
        
        gold_val = getattr(self.game, 'gold', 0)
        target_color = (100, 255, 120) if gold_val >= current_target else (255, 130, 130)
        lbl_target = sub_font.render(f"Quota: {gold_val}/{current_target} Gold", True, target_color)
        screen.blit(lbl_target, (screen.get_width() - lbl_target.get_width() - 40, 55))

        lbl_desc = sub_font.render(
            "Review companion statistics, toggle mission readiness, or choose who to talk with at night.",
            True, (170, 160, 195)
        )
        screen.blit(lbl_desc, (40, 65))

        day_num = getattr(self.game, "day_number", 1)
        current_mission = DAILY_MISSIONS.get(day_num, {"name": "Standard Patrol", "type": "General", "desc": "Routine safety checks."})
        
        mission_title_font = pygame.font.SysFont("Trebuchet MS", 15, bold=True)
        mission_desc_font = pygame.font.SysFont("Trebuchet MS", 14, italic=True)
        
        pygame.draw.rect(screen, (22, 16, 45), (40, 98, 944, 32), border_radius=6)
        pygame.draw.rect(screen, (90, 60, 170), (40, 98, 944, 32), width=1, border_radius=6)
        
        lbl_m_info = mission_title_font.render(f"ACTIVE MISSION: {current_mission['name']} ({current_mission['type']})", True, (255, 215, 0))
        lbl_m_desc = mission_desc_font.render(f" -> {current_mission['desc']}", True, (200, 190, 230))
        
        screen.blit(lbl_m_info, (55, 104))
        screen.blit(lbl_m_desc, (60 + lbl_m_info.get_width(), 105))

        h_font = pygame.font.SysFont("Trebuchet MS", 22, bold=True)
        t_font = pygame.font.SysFont("Trebuchet MS", 16, italic=True)
        class_font = pygame.font.SysFont("Trebuchet MS", 13, bold=True)
        m_font = pygame.font.SysFont("Arial", 14, bold=True)
        status_font = pygame.font.SysFont("Trebuchet MS", 16, bold=True)

        mouse_pos = pygame.mouse.get_pos()
        hero_classes = {"aldric": "Knight", "seraphel": "Mage", "elysia": "Ranger"}

        for card in self.cards:
            hname = card["name"]
            rect = card["rect"]
            hero_color = card["color"]
            
            hero_data = self.game.runtime_heroes.get(hname.lower()) if self.game.runtime_heroes else None
            
            if not hero_data:
                pygame.draw.rect(screen, (25, 25, 30), rect, border_radius=15)
                pygame.draw.rect(screen, (50, 50, 55), rect, width=2, border_radius=15)
                lbl_missing = h_font.render(f"Loading {hname}...", True, (120, 120, 130))
                screen.blit(lbl_missing, (rect.centerx - lbl_missing.get_width()//2, rect.centery - lbl_missing.get_height()//2))
                continue

            if isinstance(hero_data, dict):
                affection = hero_data.get("affection", 50)
                morale = hero_data.get("morale", 50)
                tired = hero_data.get("tired", 0) if "tired" in hero_data else hero_data.get("tiredness", 0)
                on_mission = hero_data.get("on_mission", False)
                chat_completed = hero_data.get("chat_completed", False)
            else:
                affection = getattr(hero_data, "affection", 50)
                morale = getattr(hero_data, "morale", 50)
                tired = getattr(hero_data, "tired", 0) if hasattr(hero_data, "tired") else getattr(hero_data, "tiredness", 0)
                on_mission = getattr(hero_data, "on_mission", False)
                chat_completed = getattr(hero_data, "chat_completed", False)

            title = self.get_relationship_title(affection)
            success_rate = self.get_success_chance(hname, title)

            pygame.draw.rect(screen, (30, 24, 55), rect, border_radius=15)
            pygame.draw.rect(screen, (70, 50, 110), rect, width=2, border_radius=15)
            
            header_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, 60)
            pygame.draw.rect(screen, hero_color, header_rect, border_radius=13)
            pygame.draw.rect(screen, hero_color, (rect.x + 2, rect.y + 50, rect.width - 4, 12))

            lbl_name = h_font.render(hname, True, (255, 255, 255))
            screen.blit(lbl_name, (rect.x + 20, rect.y + 12))
            
            h_type = hero_classes.get(hname.lower(), "Hero")
            lbl_type = class_font.render(f"[{h_type}]", True, (255, 230, 150))
            screen.blit(lbl_type, (rect.x + 25 + lbl_name.get_width(), rect.y + 18))
            
            lbl_title_rel = t_font.render(title, True, (230, 210, 255))
            screen.blit(lbl_title_rel, (rect.x + 20, rect.y + 36))

            self._draw_metric_bar(screen, rect.x + 20, rect.y + 85, rect.width - 40, affection, "Affection", (220, 110, 160), m_font)
            self._draw_metric_bar(screen, rect.x + 20, rect.y + 145, rect.width - 40, morale, "Morale", (100, 180, 220), m_font)
            self._draw_metric_bar(screen, rect.x + 20, rect.y + 205, rect.width - 40, tired, "Tiredness", (220, 120, 80), m_font)

            if self.display_mode == "missions":
                status_str = f"Missions: {'ON MISSION' if on_mission else 'RESTING'}"
                status_color = (255, 140, 50) if on_mission else (80, 220, 100)
                lbl_status = status_font.render(status_str, True, status_color)
                screen.blit(lbl_status, (rect.x + 20, rect.y + 270))
                
                rate_str = f"Success Chance: {success_rate}%"
                lbl_rate = status_font.render(rate_str, True, (200, 200, 255))
                screen.blit(lbl_rate, (rect.x + 20, rect.y + 295))
            else:
                chat_str = "Chat: COMPLETED" if chat_completed else "Chat: AVAILABLE"
                chat_color = (130, 130, 150) if chat_completed else (150, 255, 150)
                lbl_chat = status_font.render(chat_str, True, chat_color)
                screen.blit(lbl_chat, (rect.x + 20, rect.y + 270))

                mission_str = "Status: RESTING"
                if on_mission:
                    mission_str = f"Status: ON MISSION ({success_rate}% Success)"
                lbl_mission = status_font.render(mission_str, True, (200, 200, 220))
                screen.blit(lbl_mission, (rect.x + 20, rect.y + 295))

            btn_rect = self.hero_action_buttons[hname]
            hover = btn_rect.collidepoint(mouse_pos)
            
            if self.display_mode == "view":
                pygame.draw.rect(screen, (45, 38, 75), btn_rect, border_radius=8)
                lbl_action = status_font.render(title, True, (180, 170, 210))
                screen.blit(lbl_action, (btn_rect.centerx - lbl_action.get_width()//2, btn_rect.centery - lbl_action.get_height()//2))
            
            elif self.display_mode == "missions":
                btn_color = (231, 76, 60) if on_mission else (46, 204, 113)
                if hover:
                    btn_color = (241, 140, 120) if on_mission else (100, 230, 150)
                pygame.draw.rect(screen, btn_color, btn_rect, border_radius=8)
                btn_text = "Rest Hero" if on_mission else "Assign to Mission"
                lbl_action = status_font.render(btn_text, True, (255, 255, 255) if hover else (10, 20, 10) if not on_mission else (255, 255, 255))
                screen.blit(lbl_action, (btn_rect.centerx - lbl_action.get_width()//2, btn_rect.centery - lbl_action.get_height()//2))

            elif self.display_mode == "chat":
                if chat_completed:
                    pygame.draw.rect(screen, (35, 30, 50), btn_rect, border_radius=8)
                    lbl_action = status_font.render("Already Spoken", True, (110, 110, 130))
                else:
                    btn_color = (52, 152, 219) if hover else (41, 128, 185)
                    pygame.draw.rect(screen, btn_color, btn_rect, border_radius=8)
                    lbl_action = status_font.render("Talk to Hero", True, (255, 255, 255))
                screen.blit(lbl_action, (btn_rect.centerx - lbl_action.get_width()//2, btn_rect.centery - lbl_action.get_height()//2))

        # Bottom Global Action Button
        hover_bottom = self.bottom_button.collidepoint(mouse_pos)
        bottom_color = (255, 170, 80) if hover_bottom else (220, 140, 50)
        
        pygame.draw.rect(screen, bottom_color, self.bottom_button, border_radius=10)
        pygame.draw.rect(screen, (255, 220, 180), self.bottom_button, width=2, border_radius=10)
        
        btn_font = pygame.font.SysFont("Trebuchet MS", 20, bold=True)
        if self.display_mode == "view":
            bottom_text = "Back to Shop"
        elif self.display_mode == "missions":
            bottom_text = "Send Heroes & Start Night"
        elif self.display_mode == "chat":
            bottom_text = "Complete Night / Results"

        lbl_bottom = btn_font.render(bottom_text, True, (25, 20, 45) if not hover_bottom else (10, 5, 25))
        screen.blit(lbl_bottom, (self.bottom_button.centerx - lbl_bottom.get_width()//2, self.bottom_button.centery - lbl_bottom.get_height()//2))

    def _draw_metric_bar(self, screen, x, y, width, value, label, bar_color, font):
        lbl = font.render(f"{label}: {int(value)}/100", True, (200, 200, 220))
        screen.blit(lbl, (x, y))

        bg_rect = pygame.Rect(x, y + 20, width, 14)
        pygame.draw.rect(screen, (20, 18, 30), bg_rect, border_radius=4)
        
        fill_width = int((value / 100.0) * width)
        if fill_width > 0:
            fill_rect = pygame.Rect(x, y + 20, fill_width, 14)
            pygame.draw.rect(screen, bar_color, fill_rect, border_radius=4)