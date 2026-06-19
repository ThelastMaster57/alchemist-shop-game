import pygame
import math
from scenes.base import BaseScene

# Günlük görev listesi (gün → görev bilgisi)
DAILY_MISSIONS = {
    1: {"name": "Banliyölerde Goblinler", "type": "Savaş", "desc": "Yüksek Güç gerektirir. En iyi: Aldric."},
    2: {"name": "Büyüsel Anomali Araştırması", "type": "Büyü",  "desc": "Yüksek Zeka gerektirir. En iyi: Seraphel."},
    3: {"name": "Fısıldayan Orman Keşfi",  "type": "Keşif",  "desc": "Yüksek Çeviklik gerektirir. En iyi: Elysia."}
}

# --- GÖREV KAPASİTE EŞİKLERİ ---
TIRED_THRESHOLD  = 70   # Bu değer ve üzeri → göreve gidemez
MORALE_THRESHOLD = 20   # Bu değer ve altı  → göreve gidemez


class HeroesScene(BaseScene):
    """Hero Roster & Night Management Scene."""

    def __init__(self, game):
        super().__init__(game)
        self.display_mode  = "view"
        self.hero_names    = ["Aldric", "Seraphel", "Elysia"]
        self.anim_tick     = 0.0   # animasyon sayacı

        # Kart layout
        self.cards = [
            {"name": "Aldric",   "rect": pygame.Rect( 50, 175, 290, 440), "color": (45,  95, 160), "accent": (100, 160, 255)},
            {"name": "Seraphel", "rect": pygame.Rect(367, 175, 290, 440), "color": (140,  35,  95), "accent": (255, 100, 190)},
            {"name": "Elysia",   "rect": pygame.Rect(684, 175, 290, 440), "color": ( 60, 140,  45), "accent": (120, 230,  80)},
        ]
        self.bottom_button      = pygame.Rect(362, 635, 300, 55)
        self.hero_action_buttons = {}
        for card in self.cards:
            r = card["rect"]
            self.hero_action_buttons[card["name"]] = pygame.Rect(r.x + 25, r.y + 365, 240, 45)

    # ──────────────────────────────────────────────
    #  YARDIMCI METODLAR
    # ──────────────────────────────────────────────

    def set_mode(self, mode):
        self.display_mode = mode

    def _get_stat(self, hdata, *keys):
        """Dict veya obje üzerinde birden fazla anahtar adıyla güvenli okuma."""
        is_dict = isinstance(hdata, dict)
        for k in keys:
            if is_dict:
                if k in hdata: return hdata[k]
            else:
                if hasattr(hdata, k): return getattr(hdata, k)
        return 0

    def can_go_on_mission(self, hdata):
        """
        Kahramanın göreve çıkıp çıkamayacağını kontrol eder.
        Returns (bool can_go, str reason)
        """
        penalty_days = self._get_stat(hdata, "penalty_days")
        if penalty_days > 0:
            return False, f"YARALI ({penalty_days} Gün Dinlenmeli)"

        tired  = self._get_stat(hdata, "tired", "tiredness")
        morale = self._get_stat(hdata, "morale")
        if morale == 0:
            morale = 50  # hiç ayarlanmamışsa varsayılan

        if tired >= TIRED_THRESHOLD:
            return False, f"ÇOK YORGUN  ({int(tired)}/100)"
        if morale <= MORALE_THRESHOLD:
            return False, f"MORALİ ÇÖKMÜŞ  ({int(morale)}/100)"
        return True, ""

    def get_relationship_title(self, affection):
        try:
            import data.characters as ch
            if hasattr(ch, "AFFECTION_BANDS"):
                for band in ch.AFFECTION_BANDS:
                    if len(band) >= 3 and band[0] <= affection <= band[1]:
                        return band[2]
        except Exception:
            pass
        if affection <= 20:  return "Temkinli"
        if affection <= 50:  return "Tanıdık"
        if affection <= 80:  return "Güvenilir Dost"
        return "Yeminli"

    def get_success_chance(self, hero_name, title):
        hdata = (self.game.runtime_heroes.get(hero_name.lower())
                 or self.game.runtime_heroes.get(hero_name)) if self.game.runtime_heroes else None
        if not hdata:
            return 50
        day_num  = getattr(self.game, "day_number", 1)
        m_type   = DAILY_MISSIONS.get(day_num, {}).get("type", "Genel")
        specialties = {"aldric": "Savaş", "seraphel": "Büyü", "elysia": "Keşif"}
        morale = self._get_stat(hdata, "morale") or 50
        tired  = self._get_stat(hdata, "tired", "tiredness")
        chance = 50 + (morale // 2) - (tired // 2)
        if specialties.get(hero_name.lower()) == m_type:
            chance += 30
        return max(10, min(95, chance))

    # ──────────────────────────────────────────────
    #  EVENT HANDLING
    # ──────────────────────────────────────────────

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        mouse_pos = event.pos

        # Alt büyük buton
        if self.bottom_button.collidepoint(mouse_pos):
            if self.display_mode == "view":
                if "shop" in getattr(self.game, "scenes", {}):
                    self.game.change_scene("shop")

            elif self.display_mode == "missions":
                self.game.phase = "NIGHT"
                for hname in self.hero_names:
                    hdata = (self.game.runtime_heroes.get(hname.lower())
                             or self.game.runtime_heroes.get(hname))
                    if hdata:
                        if isinstance(hdata, dict): hdata["chat_completed"] = False
                        else: hdata.chat_completed = False
                self.set_mode("chat")
                print("[SİSTEM] Görevler kilitlendi → Gece Sohbet moduna geçildi.")

            elif self.display_mode == "chat":
                print("[SİSTEM] Geceyi bitir → görev sonuçları hesaplanıyor...")
                if hasattr(self.game, "execute_missions_and_results"):
                    self.game.execute_missions_and_results()
            return

        # Kahraman kart butonları
        for card in self.cards:
            hname     = card["name"]
            hero_data = (self.game.runtime_heroes.get(hname.lower())
                         or self.game.runtime_heroes.get(hname)) if self.game.runtime_heroes else None
            if not hero_data:
                continue
            btn_rect = self.hero_action_buttons[hname]
            if not btn_rect.collidepoint(mouse_pos):
                continue

            if self.display_mode == "missions":
                is_dict       = isinstance(hero_data, dict)
                on_mission    = hero_data.get("on_mission", False) if is_dict else getattr(hero_data, "on_mission", False)
                can_go, reason = self.can_go_on_mission(hero_data)

                if not on_mission and not can_go:
                    # Göreve çıkmak istiyor ama ehliyetsiz → reddet
                    print(f"[BLOK] {hname} göreve gönderilemiyor: {reason}")
                    return

                # Toggle
                new_val = not on_mission
                if is_dict: hero_data["on_mission"] = new_val
                else: hero_data.on_mission = new_val

            elif self.display_mode == "chat":
                is_dict        = isinstance(hero_data, dict)
                already_chatted = (hero_data.get("chat_completed", False) if is_dict
                                   else getattr(hero_data, "chat_completed", False))
                if not already_chatted:
                    self.game.scenes["dialogue"].start_night_dialogue(hname.lower(), self.game.day_number)
                    self.game.change_scene("dialogue")

    # ──────────────────────────────────────────────
    #  UPDATE
    # ──────────────────────────────────────────────

    def update(self, dt):
        self.anim_tick += dt

    # ──────────────────────────────────────────────
    #  DRAW
    # ──────────────────────────────────────────────

    def draw(self, screen):
        # ── Arka plan ──────────────────────────────
        screen.fill((12, 10, 26))
        # Yıldız parıltısı efekti (basit nokta animasyonu)
        for i in range(30):
            sx = (i * 137 + 50) % 1024
            sy = (i * 97  + 30) % 145
            alpha = int(120 + 80 * math.sin(self.anim_tick * 1.5 + i))
            star_surf = pygame.Surface((3, 3), pygame.SRCALPHA)
            star_surf.fill((255, 255, 255, alpha))
            screen.blit(star_surf, (sx, sy))

        # ── Üst header bar ─────────────────────────
        header_surf = pygame.Surface((1024, 155), pygame.SRCALPHA)
        header_surf.fill((28, 20, 58, 230))
        screen.blit(header_surf, (0, 0))
        pygame.draw.line(screen, (130, 90, 229), (0, 155), (1024, 155), 2)

        title_font  = pygame.font.SysFont("Trebuchet MS", 30, bold=True)
        sub_font    = pygame.font.SysFont("Trebuchet MS", 15)
        badge_font  = pygame.font.SysFont("Trebuchet MS", 13, bold=True)

        mode_titles = {
            "view":     "⚔  Kahraman Durum Panosu",
            "missions": "🗺  Günlük Görev Atama",
            "chat":     "🌙  Gece Sohbetleri"
        }
        lbl_title = title_font.render(mode_titles.get(self.display_mode, "Kahraman Panosu"), True, (220, 205, 255))
        screen.blit(lbl_title, (40, 14))

        day_num = getattr(self.game, "day_number", 1)
        lbl_day = title_font.render(f"Gün {day_num}", True, (255, 200, 80))
        screen.blit(lbl_day, (screen.get_width() - lbl_day.get_width() - 40, 14))

        # Kota göstergesi
        GOLD_TARGETS  = {1: 150, 2: 300, 3: 500}
        current_target = GOLD_TARGETS.get(day_num, 150)
        gold_val       = getattr(self.game, "gold", 0)
        quota_color    = (80, 255, 130) if gold_val >= current_target else (255, 120, 100)
        lbl_quota = sub_font.render(f"Kota: {gold_val}/{current_target} Altın", True, quota_color)
        screen.blit(lbl_quota, (screen.get_width() - lbl_quota.get_width() - 40, 55))

        # Aktif görev bilgisi
        mission      = DAILY_MISSIONS.get(day_num, {"name": "Devriye", "type": "Genel", "desc": ""})
        mission_surf = pygame.Surface((944, 32), pygame.SRCALPHA)
        mission_surf.fill((22, 14, 48, 200))
        screen.blit(mission_surf, (40, 108))
        pygame.draw.rect(screen, (90, 60, 170), pygame.Rect(40, 108, 944, 32), 1, border_radius=5)
        m_font = pygame.font.SysFont("Trebuchet MS", 14, bold=True)
        lbl_m  = m_font.render(f"AKTIF GÖREV:  {mission['name']}  [{mission['type']}]  →  {mission['desc']}", True, (255, 215, 0))
        screen.blit(lbl_m, (55, 116))

        # ── Hero kartları ───────────────────────────
        mouse_pos  = pygame.mouse.get_pos()
        h_font     = pygame.font.SysFont("Trebuchet MS", 21, bold=True)
        t_font     = pygame.font.SysFont("Trebuchet MS", 14, italic=True)
        cls_font   = pygame.font.SysFont("Trebuchet MS", 12, bold=True)
        m_bar_font = pygame.font.SysFont("Arial", 13, bold=True)
        stat_font  = pygame.font.SysFont("Trebuchet MS", 14, bold=True)
        warn_font  = pygame.font.SysFont("Trebuchet MS", 13, bold=True)
        hero_classes = {"aldric": "Şövalye", "seraphel": "Büyücü", "elysia": "Okçu"}

        for card in self.cards:
            hname      = card["name"]
            rect       = card["rect"]
            hero_color = card["color"]
            accent     = card["accent"]

            hdata = (self.game.runtime_heroes.get(hname.lower())
                     or self.game.runtime_heroes.get(hname)) if self.game.runtime_heroes else None

            # Yüklenmemişse gri kart
            if not hdata:
                pygame.draw.rect(screen, (22, 20, 32), rect, border_radius=14)
                pygame.draw.rect(screen, (50, 50, 60), rect, 2, border_radius=14)
                lbl_m = h_font.render(f"{hname} yükleniyor...", True, (100, 100, 110))
                screen.blit(lbl_m, (rect.centerx - lbl_m.get_width()//2, rect.centery))
                continue

            is_dict     = isinstance(hdata, dict)
            affection   = self._get_stat(hdata, "affection") or 50
            morale      = self._get_stat(hdata, "morale")   or 50
            tired       = self._get_stat(hdata, "tired", "tiredness")
            on_mission  = (hdata.get("on_mission", False) if is_dict else getattr(hdata, "on_mission", False))
            chat_done   = (hdata.get("chat_completed", False) if is_dict else getattr(hdata, "chat_completed", False))

            can_go, incap_reason = self.can_go_on_mission(hdata)
            title        = self.get_relationship_title(affection)
            success_rate = self.get_success_chance(hname, title)

            # Kart arka plan
            pygame.draw.rect(screen, (24, 18, 44), rect, border_radius=14)
            pygame.draw.rect(screen, accent if on_mission else (60, 48, 90), rect, 2, border_radius=14)

            # Renkli header şeridi
            header_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, 64)
            pygame.draw.rect(screen, hero_color, header_rect, border_radius=12)
            pygame.draw.rect(screen, hero_color, (rect.x + 2, rect.y + 52, rect.width - 4, 14))

            # İsim + sınıf
            lbl_name = h_font.render(hname, True, (255, 255, 255))
            screen.blit(lbl_name, (rect.x + 18, rect.y + 12))
            h_cls = hero_classes.get(hname.lower(), "Kahraman")
            lbl_cls = cls_font.render(f"[{h_cls}]", True, (255, 230, 140))
            screen.blit(lbl_cls, (rect.x + 22 + lbl_name.get_width(), rect.y + 18))
            lbl_rel = t_font.render(title, True, (230, 215, 255))
            screen.blit(lbl_rel, (rect.x + 18, rect.y + 38))

            # Metrik barlar
            self._draw_bar(screen, rect.x + 18, rect.y + 88,  rect.width - 36, affection, "Bağ",      (210, 100, 160), m_bar_font)
            self._draw_bar(screen, rect.x + 18, rect.y + 148, rect.width - 36, morale,    "Moral",    (80,  160, 220), m_bar_font)
            self._draw_bar(screen, rect.x + 18, rect.y + 208, rect.width - 36, tired,     "Yorgunluk",(220, 110,  70), m_bar_font, inverted=True)

            # Eşik uyarı rozetleri
            badge_y = rect.y + 272
            if tired >= TIRED_THRESHOLD:
                self._draw_badge(screen, rect.x + 18, badge_y, "⚠ ÇOK YORGUN", (200, 80, 40), warn_font)
                badge_y += 24
            if morale <= MORALE_THRESHOLD:
                self._draw_badge(screen, rect.x + 18, badge_y, "⚠ MORALİ ÇÖKMÜŞ", (180, 50, 50), warn_font)
                badge_y += 24

            # Missions modunda görev/başarı durumu
            if self.display_mode == "missions":
                status_str   = "GÖREVDE" if on_mission else ("DİNLENİYOR" if can_go else "KATILIM YOK")
                status_color = (255, 160, 40) if on_mission else ((100, 230, 100) if can_go else (200, 70, 70))
                lbl_status = stat_font.render(status_str, True, status_color)
                screen.blit(lbl_status, (rect.x + 18, rect.y + 318))
                rate_color = (120, 200, 255) if can_go or on_mission else (120, 120, 130)
                lbl_rate   = stat_font.render(f"Başarı: %{success_rate}", True, rate_color)
                screen.blit(lbl_rate, (rect.x + 18, rect.y + 340))
            else:
                chat_str   = "Sohbet: YAPILDI" if chat_done else "Sohbet: BEKLİYOR"
                chat_color = (110, 110, 140) if chat_done else (130, 255, 130)
                lbl_chat   = stat_font.render(chat_str, True, chat_color)
                screen.blit(lbl_chat, (rect.x + 18, rect.y + 318))
                miss_str   = f"Durum: GÖREVDE (%{success_rate})" if on_mission else "Durum: DİNLENİYOR"
                lbl_miss   = stat_font.render(miss_str, True, (190, 190, 220))
                screen.blit(lbl_miss, (rect.x + 18, rect.y + 340))

            # On-mission parlama efekti
            if on_mission:
                glow_alpha = int(40 + 30 * math.sin(self.anim_tick * 3))
                glow_surf  = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*accent, glow_alpha), (0, 0, rect.width, rect.height), border_radius=14)
                screen.blit(glow_surf, rect.topleft)

            # Aksiyon butonu
            btn_rect  = self.hero_action_buttons[hname]
            btn_hover = btn_rect.collidepoint(mouse_pos)

            if self.display_mode == "view":
                pygame.draw.rect(screen, (38, 32, 62), btn_rect, border_radius=8)
                pygame.draw.rect(screen, (80, 65, 110), btn_rect, 1, border_radius=8)
                lbl_btn = stat_font.render(title, True, (170, 160, 200))
                screen.blit(lbl_btn, (btn_rect.centerx - lbl_btn.get_width()//2, btn_rect.centery - lbl_btn.get_height()//2))

            elif self.display_mode == "missions":
                if on_mission:
                    # Görevden çek butonu (her zaman aktif)
                    btn_col = (220, 80, 60) if btn_hover else (180, 55, 40)
                    pygame.draw.rect(screen, btn_col, btn_rect, border_radius=8)
                    pygame.draw.rect(screen, (255, 160, 140), btn_rect, 1, border_radius=8)
                    lbl_btn = stat_font.render("Görevden Çek", True, (255, 255, 255))
                    screen.blit(lbl_btn, (btn_rect.centerx - lbl_btn.get_width()//2, btn_rect.centery - lbl_btn.get_height()//2))
                elif can_go:
                    # Göreve gönder butonu (aktif)
                    btn_col = (60, 200, 100) if btn_hover else (40, 160, 75)
                    pygame.draw.rect(screen, btn_col, btn_rect, border_radius=8)
                    pygame.draw.rect(screen, (150, 255, 180), btn_rect, 1, border_radius=8)
                    lbl_btn = stat_font.render("Göreve Gönder", True, (10, 25, 15))
                    screen.blit(lbl_btn, (btn_rect.centerx - lbl_btn.get_width()//2, btn_rect.centery - lbl_btn.get_height()//2))
                else:
                    # Devre dışı — neden gidemediğini göster
                    pygame.draw.rect(screen, (38, 28, 28), btn_rect, border_radius=8)
                    pygame.draw.rect(screen, (130, 60, 60), btn_rect, 1, border_radius=8)
                    short_reason = incap_reason.split("(")[0].strip()
                    lbl_btn = warn_font.render(short_reason, True, (200, 100, 100))
                    screen.blit(lbl_btn, (btn_rect.centerx - lbl_btn.get_width()//2, btn_rect.centery - lbl_btn.get_height()//2))

            elif self.display_mode == "chat":
                if chat_done:
                    pygame.draw.rect(screen, (28, 24, 42), btn_rect, border_radius=8)
                    pygame.draw.rect(screen, (70, 65, 90), btn_rect, 1, border_radius=8)
                    lbl_btn = stat_font.render("Sohbet Edildi ✓", True, (100, 100, 120))
                else:
                    btn_col = (50, 140, 210) if btn_hover else (38, 110, 175)
                    pygame.draw.rect(screen, btn_col, btn_rect, border_radius=8)
                    pygame.draw.rect(screen, (130, 200, 255), btn_rect, 1, border_radius=8)
                    lbl_btn = stat_font.render("Sohbet Et →", True, (255, 255, 255))
                screen.blit(lbl_btn, (btn_rect.centerx - lbl_btn.get_width()//2, btn_rect.centery - lbl_btn.get_height()//2))

        # ── Alt büyük buton ─────────────────────────
        hover_bot  = self.bottom_button.collidepoint(mouse_pos)
        pulse      = int(8 * math.sin(self.anim_tick * 2.5))
        bot_col    = (255, 185, 90) if hover_bot else (220, 150, 55)
        pygame.draw.rect(screen, bot_col, self.bottom_button, border_radius=12)
        pygame.draw.rect(screen, (255, 230, 160), self.bottom_button, 2, border_radius=12)

        btn_font = pygame.font.SysFont("Trebuchet MS", 19, bold=True)
        bot_labels = {
            "view":     "← Dükkana Dön",
            "missions": "Gönder & Geceyi Başlat  →",
            "chat":     "Geceyi Bitir / Sonuçlar  →"
        }
        lbl_bot = btn_font.render(bot_labels.get(self.display_mode, "Devam"), True, (20, 12, 5) if hover_bot else (40, 25, 10))
        screen.blit(lbl_bot, (self.bottom_button.centerx - lbl_bot.get_width()//2,
                               self.bottom_button.centery - lbl_bot.get_height()//2))

        # Kapasite eşiklerini hatırlatan küçük not
        note_font = pygame.font.SysFont("Arial", 12, italic=True)
        lbl_note  = note_font.render(f"  Uyarı: Yorgunluk ≥{TIRED_THRESHOLD} veya Moral ≤{MORALE_THRESHOLD} olan kahramanlar göreve gidemez.", True, (120, 110, 140))
        screen.blit(lbl_note, (40, 695))

    # ──────────────────────────────────────────────
    #  YARDIMCI ÇİZİM
    # ──────────────────────────────────────────────

    def _draw_bar(self, screen, x, y, width, value, label, color, font, inverted=False):
        """Metrik çubuk çizer. inverted=True → yüksek değer kötü (yorgunluk)."""
        lbl = font.render(f"{label}: {int(value)}/100", True, (200, 195, 220))
        screen.blit(lbl, (x, y))

        bg = pygame.Rect(x, y + 18, width, 13)
        pygame.draw.rect(screen, (18, 15, 28), bg, border_radius=4)

        fill_w = int((value / 100.0) * width)
        if fill_w > 0:
            # Doluluk rengi: inverted ise yüksek değerde kırmızıya kayar
            if inverted:
                r_ratio = value / 100.0
                draw_color = (
                    int(color[0] * r_ratio + 60 * (1 - r_ratio)),
                    int(color[1] * (1 - r_ratio)),
                    int(color[2] * (1 - r_ratio))
                )
            else:
                draw_color = color
            pygame.draw.rect(screen, draw_color, pygame.Rect(x, y + 18, fill_w, 13), border_radius=4)

        # Eşik çizgisi (yorgunluk barında kırmızı uyarı çizgisi)
        if inverted and value >= TIRED_THRESHOLD:
            tx = x + int((TIRED_THRESHOLD / 100.0) * width)
            pygame.draw.line(screen, (255, 80, 80), (tx, y + 15), (tx, y + 33), 2)

    def _draw_badge(self, screen, x, y, text, color, font):
        """Renkli uyarı rozeti çizer."""
        surf = font.render(text, True, (255, 255, 255))
        bg   = pygame.Rect(x - 4, y - 2, surf.get_width() + 8, surf.get_height() + 4)
        pygame.draw.rect(screen, color, bg, border_radius=5)
        screen.blit(surf, (x, y))