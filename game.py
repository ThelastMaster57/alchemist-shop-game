import pygame
import os
import sys
import random

# Oyunun çalıştığı dosyanın (game.py) gerçek ve tam klasör yolunu buluyoruz
base_dir = os.path.dirname(os.path.abspath(__file__))
# Python'ın çalışma dizinini zorunlu olarak bu klasöre eşitliyoruz
os.chdir(base_dir)

print(f"[System Check] Aktif çalışma dizini şuraya sabitlendi: {os.getcwd()}")

from scenes.shop import ShopScene
from scenes.brewing import BrewingScene
from scenes.heroes import HeroesScene
from scenes.dialogue import DialogueScene
from scenes.results import ResultsScene
from scenes.base import BaseScene


# --- YENİ: SİNEMATİK / INTRO SAHNESİ ---
class IntroScene(BaseScene):
    """Oyun başındaki siyah ekranlı, seslendirme uyumlu hikaye sinematiği."""
    def __init__(self, game):
        super().__init__(game)
        # Buraya istediğin hikaye metinlerini ekleyebilirsin kanka!
        self.story_lines = [
            "Büyük Element Savaşı'nın üzerinden tam kırk yıl geçti...",
            "Krallıklar yıkıldı, geriye sadece kadim simyanın külleri kaldı.",
            "Sen, bu topraklarda düzeni yeniden sağlayabilecek son Alchemist'sin.",
            "Kahramanları besle, ittifakları kur ve 3 günlük bu amansız sınavı tamamla.",
            "Kaderin kazanı kaynıyor... Macera başlıyor!"
        ]
        self.current_line_idx = 0
        self.text_alpha = 0
        self.fade_state = "FADEIN" # FADEIN, WAIT, FADEOUT
        self.state_timer = 0.0
        
    def handle_event(self, event):
        # Ekrana tıklanırsa veya Space'e basılırsa sonraki satıra geç (Geçme kolaylığı)
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or \
           (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
            self.next_line()

    def next_line(self):
        self.current_line_idx += 1
        if self.current_line_idx >= len(self.story_lines):
            # Hikaye bitti, dükkanı yükle ve başlat!
            self.game.scenes["shop"].start_day()
            self.game.change_scene("shop")
        else:
            self.text_alpha = 0
            self.fade_state = "FADEIN"
            self.state_timer = 0.0

    def update(self, dt):
        self.state_timer += dt
        
        if self.fade_state == "FADEIN":
            self.text_alpha += 150 * dt
            if self.text_alpha >= 255:
                self.text_alpha = 255
                self.fade_state = "WAIT"
                self.state_timer = 0.0
                
        elif self.fade_state == "WAIT":
            # Her satır ekranda 4 saniye dursun (Seslendirme yapman için süre tanıdık)
            if self.state_timer >= 4.0:
                self.fade_state = "FADEOUT"
                self.state_timer = 0.0
                
        elif self.fade_state == "FADEOUT":
            self.text_alpha -= 150 * dt
            if self.text_alpha <= 0:
                self.text_alpha = 0
                self.next_line()

    def draw(self, screen):
        # Tamamen siyah ekran sinematik atmosferi
        screen.fill((0, 0, 0))
        
        if self.current_line_idx < len(self.story_lines):
            font = pygame.font.SysFont("Trebuchet MS", 26, italic=True)
            text_surf = font.render(self.story_lines[self.current_line_idx], True, (240, 230, 255))
            
            # Alpha/Görünürlük ayarı (Yumuşak geçiş için)
            alpha_surf = text_surf.convert_alpha()
            alpha_surf.fill((255, 255, 255, int(self.text_alpha)), special_flags=pygame.BLEND_RGBA_MULT)
            
            x = screen.get_width() // 2 - text_surf.get_width() // 2
            y = screen.get_height() // 2 - text_surf.get_height() // 2
            screen.blit(alpha_surf, (x, y))
            
            # Alt kısma küçük bir geç uyarısı
            skip_font = pygame.font.SysFont("Arial", 14)
            lbl_skip = skip_font.render("[Geçmek için Tıkla veya Space'e Bas]", True, (80, 80, 90))
            screen.blit(lbl_skip, (screen.get_width()//2 - lbl_skip.get_width()//2, 700))


# Title / Start Scene
class StartScene(BaseScene):
    """Initial game splash cover page. Sets a mysterious, alchemical atmosphere."""
    def __init__(self, game):
        super().__init__(game)
        self.btn_rect = pygame.Rect(387, 420, 250, 60)
        self.settings_btn_rect = pygame.Rect(387, 500, 250, 50) # Ayarlar Butonu Alanı
        self.show_settings = False
        
        # Ayarlar içi ses seviyesi kontrol butonları (Artır, Azalt, Sustur)
        self.vol_up_rect = pygame.Rect(437, 560, 40, 40)
        self.vol_down_rect = pygame.Rect(497, 560, 40, 40)
        self.vol_mute_rect = pygame.Rect(557, 560, 40, 40)
        
        self.bubbles = []
        for _ in range(15):
            self.bubbles.append({
                "x": random.randint(100, 924),
                "y": random.randint(500, 768),
                "r": random.randint(5, 20),
                "speed": random.uniform(30, 80),
                "color": (random.randint(100, 150), random.randint(50, 100), random.randint(200, 255), random.randint(30, 70))
            })

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Ayarlar paneli açıkken buton tıklamaları
            if self.show_settings:
                if self.vol_up_rect.collidepoint(mouse_pos):
                    self.game.volume = min(1.0, self.game.volume + 0.1)
                    self.game.update_music_volume()
                    return
                elif self.vol_down_rect.collidepoint(mouse_pos):
                    self.game.volume = max(0.0, self.game.volume - 0.1)
                    self.game.update_music_volume()
                    return
                elif self.vol_mute_rect.collidepoint(mouse_pos):
                    self.game.volume = 0.0 if self.game.volume > 0.0 else 0.2
                    self.game.update_music_volume()
                    return

            if self.btn_rect.collidepoint(mouse_pos):
                self.game.start_new_game()
            elif self.settings_btn_rect.collidepoint(mouse_pos):
                self.show_settings = not self.show_settings

    def update(self, dt):
        # Update floaty cauldron bubbles
        for bubble in self.bubbles:
            bubble["y"] -= bubble["speed"] * dt
            if bubble["y"] < -50:
                bubble["y"] = random.randint(768, 850)
                bubble["x"] = random.randint(100, 924)

    def draw(self, screen):
        # Dark space bg
        screen.fill((10, 8, 22))

        # Bubble animations
        for bubble in self.bubbles:
            surf = pygame.Surface((bubble["r"] * 2, bubble["r"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, bubble["color"], (bubble["r"], bubble["r"]), bubble["r"])
            screen.blit(surf, (bubble["x"] - bubble["r"], bubble["y"] - bubble["r"]))

        # Title graphics (glowing text)
        title_font = pygame.font.SysFont("Trebuchet MS", 48, bold=True)
        subtitle_font = pygame.font.SysFont("Trebuchet MS", 20, italic=True)
        author_font = pygame.font.SysFont("Arial", 14)

        # Glow effect shadow
        lbl_shadow = title_font.render("İKSİR VE İTTİFAK", True, (60, 30, 100))
        screen.blit(lbl_shadow, (screen.get_width()//2 - lbl_shadow.get_width()//2 + 3, 140 + 3))

        lbl_title = title_font.render("İKSİR VE İTTİFAK", True, (220, 200, 255))
        screen.blit(lbl_title, (screen.get_width()//2 - lbl_title.get_width()//2, 140))

        lbl_sub = subtitle_font.render("Simyacının 3 Günlük Serüveni", True, (255, 180, 80))
        screen.blit(lbl_sub, (screen.get_width()//2 - lbl_sub.get_width()//2, 200))

        # Instructions
        desc_font = pygame.font.SysFont("Arial", 16)
        instr_y = 250
        instructions = [
            "1. Kazanda malzemeleri karıştırarak Kahramanlara ve Kasabalılara hizmet et.",
            "2. İksiri başarıyla demlemek için ibreyi hareketli hedefin içinde tut.",
            "3. Kahraman yoldaşlarını tehlikeli günlük görevlere gönder.",
            "4. Gece onlarla konuşarak moral, yorgunluk ve bağ dengesini sağla.",
            "Mirasına sahip çıkmak ve güvenlerini kazanmak için 3 günü tamamla!"
        ]
        for line in instructions:
            lbl_line = desc_font.render(line, True, (170, 170, 195))
            screen.blit(lbl_line, (screen.get_width()//2 - lbl_line.get_width()//2, instr_y))
            instr_y += 22

        # Start Button
        mouse_pos = pygame.mouse.get_pos()
        hover = self.btn_rect.collidepoint(mouse_pos)
        btn_color = (130, 90, 229) if hover else (95, 60, 180)
        
        pygame.draw.rect(screen, btn_color, self.btn_rect, border_radius=10)
        pygame.draw.rect(screen, (200, 180, 255), self.btn_rect, width=2, border_radius=10)

        btn_font = pygame.font.SysFont("Trebuchet MS", 22, bold=True)
        lbl_btn = btn_font.render("Serüvene Başla", True, (255, 255, 255))
        screen.blit(lbl_btn, (self.btn_rect.centerx - lbl_btn.get_width()//2, self.btn_rect.centery - lbl_btn.get_height()//2))

        # Settings Button Drawing
        hover_s = self.settings_btn_rect.collidepoint(mouse_pos)
        btn_s_color = (100, 100, 120) if hover_s else (60, 60, 75)
        pygame.draw.rect(screen, btn_s_color, self.settings_btn_rect, border_radius=10)
        pygame.draw.rect(screen, (150, 150, 170), self.settings_btn_rect, width=1, border_radius=10)
        
        lbl_btn_s = btn_font.render("Ayarlar / Ses", True, (230, 230, 240))
        screen.blit(lbl_btn_s, (self.settings_btn_rect.centerx - lbl_btn_s.get_width()//2, self.settings_btn_rect.centery - lbl_btn_s.get_height()//2))

        # Ayarlar Açıkken Kontrol Butonlarını Çiz
        if self.show_settings:
            # Mevcut Ses Durumu Yazısı
            status_font = pygame.font.SysFont("Arial", 16, bold=True)
            lbl_vol_status = status_font.render(f"Ses: %{int(self.game.volume * 100)}", True, (255, 200, 100))
            screen.blit(lbl_vol_status, (screen.get_width()//2 - lbl_vol_status.get_width()//2, 530))
            
            # Artır (+), Azalt (-), Sustur (X) Butonları
            pygame.draw.rect(screen, (40, 120, 40), self.vol_up_rect, border_radius=5)
            pygame.draw.rect(screen, (120, 40, 40), self.vol_down_rect, border_radius=5)
            pygame.draw.rect(screen, (80, 80, 90), self.vol_mute_rect, border_radius=5)
            
            sign_font = pygame.font.SysFont("Arial", 20, bold=True)
            screen.blit(sign_font.render("+", True, (255,255,255)), (self.vol_up_rect.centerx-6, self.vol_up_rect.centery-12))
            screen.blit(sign_font.render("-", True, (255,255,255)), (self.vol_down_rect.centerx-5, self.vol_down_rect.centery-12))
            screen.blit(sign_font.render("M", True, (255,255,255)), (self.vol_mute_rect.centerx-7, self.vol_mute_rect.centery-12))

        lbl_auth = author_font.render("Pygame ve dinamik mekaniklerle tasarlandı", True, (80, 80, 100))
        screen.blit(lbl_auth, (screen.get_width()//2 - lbl_auth.get_width()//2, 720))


# Game Engine
class Game:
    """Core Game Engine. Manages Pygame initialization, scene routing, and state machine cycle."""
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Potion & Alliance: Alchemist's Chronicles")
        
        # Screen dimensions
        self.width = 1024
        self.height = 768
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        
        # Global states
        self.gold = 100
        self.day_number = 1
        self.phase = "DAY"  # "DAY" or "NIGHT"
        self.runtime_heroes = {}
        self.volume = 0.2  # Varsayılan global ses seviyesi kanka
        self.current_scene_name = "start"

        # --- YENİ: COZY PLAYLIST SİSTEMİ BAŞLANGICI ---
        try:
            pygame.mixer.init()
            self.playlist = [
                "assets/cozy_bgm1.mp3",
                "assets/cozy_bgm2.mp3",
                "assets/cozy_bgm3.mp3",
                "assets/cozy_bgm4.mp3"
            ]
            self.current_track_index = 0
            
            # Şarkı bittiğinde Pygame döngüsüne düşecek özel event sinyali
            self.MUSIC_END_EVENT = pygame.USEREVENT + 1
            pygame.mixer.music.set_endevent(self.MUSIC_END_EVENT)
            
            # İlk parçayı başlat
            self.play_current_track()
        except Exception as e:
            print(f"Ses motoru başlatılamadı, müziksiz devam ediliyor: {e}")
            self.playlist = []
        # ----------------------------------------------

        # Scenes dictionary
        self.scenes = {
            "start": StartScene(self),
            "intro": IntroScene(self), # Yeni intro sahnemizi ekledik!
            "shop": ShopScene(self),
            "brewing": BrewingScene(self),
            "heroes": HeroesScene(self),
            "dialogue": DialogueScene(self),
            "results": ResultsScene(self)
        }
        
        # Initial scene
        self.active_scene = self.scenes["start"]

    def play_current_track(self):
        """Playlist içerisindeki aktif parçayı yükler ve güvenli şekilde yürütür."""
        if not self.playlist:
            return
        try:
            track = self.playlist[self.current_track_index]
            pygame.mixer.music.load(track)
            
            # Sahneye ve genel ses seviyesine göre desibel ayarı
            self.update_music_volume()
            
            # 1 kere çalması için tetikliyoruz. Bitince MUSIC_END_EVENT fırlayacak
            pygame.mixer.music.play(1)
            print(f"[Music Engine] Çalınıyor: {track} | Ses Seviyesi: {self.volume}")
        except Exception as e:
            print(f"[Music Engine] Şarkı yükleme hatası ({track}): {e}")

    def update_music_volume(self):
        """Mevcut aktif sahneye göre desibel ağırlığını koruyarak sesi günceller."""
        try:
            if pygame.mixer.music.get_busy():
                if self.current_scene_name == "dialogue":
                    pygame.mixer.music.set_volume(self.volume * 0.5) # Diyalogda arkaya çek
                elif self.current_scene_name == "shop":
                    pygame.mixer.music.set_volume(min(1.0, self.volume * 1.2)) # Dükkanda canlandır (max 1.0)
                else:
                    pygame.mixer.music.set_volume(self.volume)
        except:
            pass

    def change_scene(self, scene_name):
        """Transitions scene router."""
        if scene_name in self.scenes:
            self.active_scene = self.scenes[scene_name]
            self.current_scene_name = scene_name 
            self.update_music_volume()

    def reset_game(self):
        """Resets game states to original values."""
        self.gold = 100
        self.day_number = 1
        self.phase = "DAY"
        
        # Initialize runtime heroes
        try:
            import data.characters as characters
            if hasattr(characters, "build_runtime_heroes"):
                self.runtime_heroes = characters.build_runtime_heroes()
            else:
                self.runtime_heroes = self.get_fallback_heroes()
        except Exception as e:
            print(f"Error loading runtime heroes: {e}")
            self.runtime_heroes = self.get_fallback_heroes()

        # Mark all as not chat completed and not on mission
        for hero_name in ["Aldric", "Seraphel", "Elysia"]:
            hdata = self.runtime_heroes.get(hero_name)
            if hdata:
                if isinstance(hdata, dict):
                    hdata["on_mission"] = False
                    hdata["chat_completed"] = False
                    hdata.setdefault("penalty_days", 0)
                else:
                    hdata.on_mission = False
                    hdata.chat_completed = False
                    if not hasattr(hdata, "penalty_days"): setattr(hdata, "penalty_days", 0)

        self.change_scene("start")

    def start_new_game(self):
        """Starts a clean play cycle starting on the Intro Cinematic Scene."""
        self.gold = 100
        self.day_number = 1
        self.phase = "DAY"
        
        # Set up runtime heroes
        try:
            import data.characters as characters
            if hasattr(characters, "build_runtime_heroes"):
                self.runtime_heroes = characters.build_runtime_heroes()
            else:
                self.runtime_heroes = self.get_fallback_heroes()
        except Exception as e:
            print(f"Error loading runtime heroes: {e}")
            self.runtime_heroes = self.get_fallback_heroes()

        # Standardizing structure
        for hname, hdata in self.runtime_heroes.items():
            if isinstance(hdata, dict):
                hdata.setdefault("on_mission", False)
                hdata.setdefault("chat_completed", False)
                hdata.setdefault("affection", 50)
                hdata.setdefault("morale", 50)
                hdata.setdefault("tired", 0)
                hdata.setdefault("penalty_days", 0)
            else:
                if not hasattr(hdata, "on_mission"): setattr(hdata, "on_mission", False)
                if not hasattr(hdata, "chat_completed"): setattr(hdata, "chat_completed", False)
                if not hasattr(hdata, "affection"): setattr(hdata, "affection", 50)
                if not hasattr(hdata, "morale"): setattr(hdata, "morale", 50)
                if not hasattr(hdata, "tired") and not hasattr(hdata, "tiredness"): setattr(hdata, "tired", 0)
                if not hasattr(hdata, "penalty_days"): setattr(hdata, "penalty_days", 0)

        # Doğrudan dükkan yerine ÖNCE SİNEMATİK SAHNEYİ BAŞLAT kanka!
        self.change_scene("intro")

    def get_fallback_heroes(self):
        """Constructs fallback hero dictionary structure."""
        return {
            "Aldric": {"affection": 30, "morale": 50, "tired": 20, "on_mission": False, "chat_completed": False, "penalty_days": 0},
            "Seraphel": {"affection": 20, "morale": 60, "tired": 10, "on_mission": False, "chat_completed": False, "penalty_days": 0},
            "Elysia": {"affection": 40, "morale": 45, "tired": 30, "on_mission": False, "chat_completed": False, "penalty_days": 0}
        }

    def execute_missions_and_results(self):
        """Processes mission success chance checks, edits stats and displays reports."""
        results = []
        gold_earned = 0
        
        for hname in ["Aldric", "Seraphel", "Elysia"]:
            hdata = self.runtime_heroes.get(hname) or self.runtime_heroes.get(hname.lower())
            if not hdata:
                continue

            is_dict = isinstance(hdata, dict)
            
            affection = hdata.get("affection", 50) if is_dict else getattr(hdata, "affection", 50)
            morale = hdata.get("morale", 50) if is_dict else getattr(hdata, "morale", 50)
            tired = 0
            if is_dict:
                tired = hdata.get("tired", 0) if "tired" in hdata else hdata.get("tiredness", 0)
            else:
                tired = getattr(hdata, "tired", 0) if hasattr(hdata, "tired") else getattr(hdata, "tiredness", 0)

            on_mission = hdata.get("on_mission", False) if is_dict else getattr(hdata, "on_mission", False)

            stats_change = {}
            if on_mission:
                title = self.scenes["heroes"].get_relationship_title(affection)
                success_chance = self.scenes["heroes"].get_success_chance(hname, title)
                roll = random.randint(1, 100)
                
                if roll <= success_chance:
                    gold_reward = 100
                    gold_earned += gold_reward
                    aff_chg = 10
                    mor_chg = 15
                    trd_chg = 25
                    outcome = "SUCCESS"
                    message = f"{hname} zindanları fethetti, canavarı alt etti ve {gold_reward} altın getirdi!"
                else:
                    gold_reward = 0
                    aff_chg = -5
                    mor_chg = -20
                    trd_chg = 35
                    outcome = "FAILURE"
                    message = f"{hname} görevde başarısız oldu ve yaralandı. İyileşmesi için 1 gün göreve gidemeyecek."
                    if is_dict:
                        hdata["penalty_days"] = 1
                    else:
                        setattr(hdata, "penalty_days", 1)
                
                stats_change = {"affection": aff_chg, "morale": mor_chg, "tiredness": trd_chg}
            else:
                aff_chg = 0
                mor_chg = 5
                trd_chg = -40
                outcome = "REST"
                message = f"{hname} sığınakta dinlendi, sağlığını topladı ve büyü kitapları okudu."
                stats_change = {"affection": aff_chg, "morale": mor_chg, "tiredness": trd_chg}

            new_aff = max(0, min(100, affection + aff_chg))
            new_mor = max(0, min(100, morale + mor_chg))
            new_trd = max(0, min(100, tired + trd_chg))

            if is_dict:
                hdata["affection"] = new_aff
                hdata["morale"] = new_mor
                if "tired" in hdata: hdata["tired"] = new_trd
                else: hdata["tiredness"] = new_trd
            else:
                setattr(hdata, "affection", new_aff)
                setattr(hdata, "morale", new_mor)
                if hasattr(hdata, "tired"): setattr(hdata, "tired", new_trd)
                else: setattr(hdata, "tiredness", new_trd)

            results.append({
                "hero_name": hname,
                "status": "mission" if on_mission else "rest",
                "outcome": outcome,
                "message": message,
                "stats_change": stats_change
            })

        self.gold += gold_earned
        is_game_over = (self.day_number >= 3)
        
        if is_game_over:
            for r in results:
                hname = r["hero_name"]
                hdata = self.runtime_heroes.get(hname)
                is_dict = isinstance(hdata, dict)
                aff = hdata.get("affection", 50) if is_dict else getattr(hdata, "affection", 50)
                title = self.scenes["heroes"].get_relationship_title(aff)
                r["message"] = f"3 günün ardından, {hname} ile bağınız {aff}/100 seviyesinde sağlamlaştı. İlişki durumunuz: '{title.upper()}'."
                r["stats_change"] = {}

            self.scenes["results"].set_results(results, gold_earned, True)
            self.change_scene("results")
            print("[System Check] 3 Günlük macera bitti. Oyun sonu özeti yükleniyor...")
        else:
            # Gece raporu verilerini results sahnesine gönderiyoruz
            self.scenes["results"].set_results(results, gold_earned, is_game_over=is_game_over)
            # Doğrudan advance_day çağırmak yerine ÖNCE sonuç ekranını (results) gösteriyoruz kanka!
            self.change_scene("results")

    def advance_day(self):
        """Advances cycle days if gold target is met, resets day layouts, and returns to daytime shop."""
        daily_quotas = {1: 150, 2: 300, 3: 500}
        current_quota = daily_quotas.get(self.day_number, 150)

        # 1. KONTROL: KOTA ALTINDA KALDI MI? (KAYBETME)
        if self.gold < current_quota:
            print(f"[Game Over] Kota doldurulamadı! Hedef: {current_quota}, Sendeki: {self.gold}")
            self.scenes["results"].set_results([], 0, is_game_over=True, won=False)
            self.change_scene("results")
            return

        # 2. KONTROL: 3. GÜN BAŞARIYLA BİTTİ Mİ? (KAZANMA)
        if self.day_number >= 3:
            print(f"[Victory] 3 Günlük sınav tamamlandı! Toplam Altın: {self.gold}")
            self.scenes["results"].set_results([], 0, is_game_over=True, won=True)
            self.change_scene("results")
            return

        # 3. DURUM: HER ŞEY YOLUNDA, SONRAKİ GÜNE GEÇİŞ
        self.day_number += 1
        self.phase = "DAY"
        
        for hname in ["Aldric", "Seraphel", "Elysia"]:
            hdata = self.runtime_heroes.get(hname)
            if hdata:
                if isinstance(hdata, dict):
                    hdata["on_mission"] = False
                    hdata["chat_completed"] = False
                    if hdata.get("penalty_days", 0) > 0:
                        hdata["penalty_days"] -= 1
                else:
                    hdata.on_mission = False
                    hdata.chat_completed = False
                    if getattr(hdata, "penalty_days", 0) > 0:
                        hdata.penalty_days -= 1

        self.scenes["shop"].start_day()
        self.change_scene("shop")
        
    def run(self):
        """Main game loop."""
        while True:
            dt = self.clock.tick(60) / 1000.0
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif hasattr(self, 'MUSIC_END_EVENT') and event.type == self.MUSIC_END_EVENT:
                    if self.playlist:
                        self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
                        self.play_current_track()

                self.active_scene.handle_event(event)

            self.active_scene.update(dt)
            self.active_scene.draw(self.screen)
            pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()