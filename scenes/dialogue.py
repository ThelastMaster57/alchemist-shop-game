import pygame
import sys
import os
from scenes.base import BaseScene

class DialogueScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.hero_name = ""       # Küçük harfli (Örn: "elysia")
        self.display_name = ""    # Düzgün isim (Örn: "Elysia")
        self.day_num = 1
        self.current_node = "root"
        self.selected_index = 0
        
        # Yazı tipleri
        self.title_font = pygame.font.SysFont("Trebuchet MS", 26, bold=True)
        self.sub_font = pygame.font.SysFont("Trebuchet MS", 14, italic=True)
        self.text_font = pygame.font.SysFont("Arial", 16)
        self.stat_font = pygame.font.SysFont("Trebuchet MS", 14, bold=True)
        
        # Kahraman Sınıfları
        self.hero_classes = {
            "aldric": "Holy Knight / Vanguard",
            "seraphel": "High Archmage / Chronomancer",
            "elysia": "Elven Ranger / Scout Master"
        }
        
        # --- RESİMLERİ MUTLAK YOL İLE YÜKLEME ALANI ---
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.hero_images = {}
        for name in ["aldric", "seraphel", "elysia"]:
            try:
                img_path = os.path.join(base_dir, "assets", f"{name}.png")
                img = pygame.image.load(img_path).convert_alpha()
                self.hero_images[name] = pygame.transform.scale(img, (240, 210))
            except Exception as e:
                print(f"Warning: {name}.png bulunamadı. Hata: {e}")
                self.hero_images[name] = None
        
        # --- TÜM HİKAYE AĞACI (EKSİKSİZ VE TAM SÜRÜM) ---
        self.story_data = {
            "elysia": {
                1: {
                    "root": {
                        "text": "Elysia: Ormanın derinliklerindeki fısıltılar hiç iyi şeyler söylemiyor... Ağaçlar bile tedirgin. Ve dürüst olmak gerekirse, beni kapalı kapılar ardındaki bu dükkandan bir yerlere göndermen beni boğuyor.",
                        "choices": [
                            {"text": "Seni çok iyi anlıyorum Elysia. Ama yaban hayatını korumak için önce bu tehlikeleri haritadan silmeliyiz.", "next": "node_agree", "effect": {"affection": 10, "morale": 5}},
                            {"text": "Bu bir zorunluluk. Krallık buradaki izcilik ve keşif operasyonlerini koordine etme görevini bana verdi.", "next": "node_duty", "effect": {"affection": -5, "morale": 15}}
                        ]
                    },
                    "node_agree": {
                        "text": "Elysia: Haklısın, belki de fazla sabırsız davranıyorum. Doğanın dengesi için yayımı hazırlayacağım. Teşekkürler Alchemist. Yarın için sabırsızlanıyorum.",
                        "choices": [{"text": "[Konuşmayı Bitir ve Günü Tamamla]", "next": "END", "effect": {}}]
                    },
                    "node_duty": {
                        "text": "Elysia: Görev mi? Emirlere uymaktan her zaman nefret etmişimdir ama... İşimi yapacağım. Sadece benden duygusal bir bağ bekleme.",
                        "choices": [{"text": "[Konuşmayı Bitir ve Günü Tamamla]", "next": "END", "effect": {}}]
                    }
                },
                2: {
                    "root": {
                        "text": "Elysia: Bu gece rüzgar çok sert esiyor. İkinci günün gerginliği üzerimde... İksirlerin bana gerçekten yardımcı olup olmayacağından emin değilim.",
                        "choices": [
                            {"text": "Sana özel çeviklik iksirleri hazırlıyorum Elysia, bana güvenebilirsin.", "next": "node_trust", "effect": {"affection": 15, "morale": 10}},
                            {"text": "İksirler sadece bir araç, asıl güç senin okçuluk yeteneğinde saklı.", "next": "node_compliment", "effect": {"affection": 20, "morale": 5}}
                        ]
                    },
                    "node_trust": {
                        "text": "Elysia: (Hafifçe gülümser) İksirlerinin tadı berbat olsa da işe yaradıklarını itiraf etmeliyim. Yarın daha dikkatli olacağım.",
                        "choices": [{"text": "[Konuşmayı Bitir]", "next": "END", "effect": {}}]
                    },
                    "node_compliment": {
                        "text": "Elysia: Yeteneğime saygı duyman güzel. Ormanda attığını vuran bir dosta sahip olduğun için şanslısın.",
                        "choices": [{"text": "[Konuşmayı Bitir]", "next": "END", "effect": {}}]
                    }
                },
                3: {
                    "root": {
                        "text": "Elysia: Son geceye geldik... Bunca mücadeleden sonra, buradaki kaderimiz yarın tamamen belli olacak. Benim hakkımda ne düşünüyorsun?",
                        "choices": [
                            {"text": "Sen bu ekibin vazgeçilmez bir parçasısın. Sonsuza dek dost kalacağız.", "next": "node_end_good", "effect": {"affection": 25}},
                            {"text": "Güzel bir iş ortaklığıydı, profesyonel kalmamız en doğrusu.", "next": "node_end_neutral", "effect": {"morale": 15}}
                        ]
                    },
                    "node_end_good": {
                        "text": "Elysia: Dost kelimesini duymak güzel... Yarınki nihai sonuç ne olursa olsun, seninle çalışmak bir onurdu.",
                        "choices": [{"text": "[Konuşmayı Bitir]", "next": "END", "effect": {}}]
                    },
                    "node_end_neutral": {
                        "text": "Elysia: Demek sadece iş... Peki, nasıl istersen. Yarın son kez dükkanın için avlanacağım.",
                        "choices": [{"text": "[Konuşmayı Bitir]", "next": "END", "effect": {}}]
                    }
                }
            },
            "aldric": {
                1: {
                    "root": {
                        "text": "Aldric: Kalkanım ağırlaşıyor, Alchemist. Krallığın bu banliyölerindeki goblin tehdidi bitmek bilmiyor. Savaşçılar bile bazen dinlenmeli.",
                        "choices": [
                            {"text": "Sen bu krallığın kalkanısın Aldric, azmini kaybetme.", "next": "node_good", "effect": {"affection": 10, "morale": 10}},
                            {"text": "Daha güçlü iksirlerle acını hafifletebilirim, biraz daha dayan.", "next": "node_potion", "effect": {"morale": 15}}
                        ]
                    },
                    "node_good": {
                        "text": "Aldric: Sözlerin içimi ısıttı. Yarın cephede parlayacağıma söz veriyorum! Kılıcım krallık ve senin dükkanın için kalkacak.",
                        "choices": [{"text": "[Konuşmayı Bitir]", "next": "END", "effect": {}}]
                    },
                    "node_potion": {
                        "text": "Aldric: İksirlerin harika ama biraz da samimiyet fena olmazdı hani. Neyse, sağ ol.",
                        "choices": [{"text": "[Konuşmayı Bitir]", "next": "END", "effect": {}}]
                    }
                },
                2: {
                    "root": {
                        "text": "Aldric: İkinci gece oldu ama omuzlarımdaki yük hafiflemedi. Sence bu savaşı kazanabilecek miyiz?",
                        "choices": [
                            {"text": "Senin gibi bir şövalye yanımdayken mağlubiyet imkansız.", "next": "node_win", "effect": {"affection": 15, "morale": 15}},
                            {"text": "Kazanmak zorundayız, yoksa dükkanı kapatmak zorunda kalırım.", "next": "node_gold", "effect": {"affection": -10, "morale": 5}}
                        ]
                    },
                    "node_win": {
                        "text": "Aldric: İşte duymak istediğim inanç buydu! Kılıcım senin emrindedir. Yarın zafere yürüyeceğiz.",
                        "choices": [{"text": "[Konuşmayı Bitir]", "next": "END", "effect": {}}]
                    },
                    "node_gold": {
                        "text": "Aldric: Demek tek derdin altının ve dükkanın... Üzücü. Savaşçılar altın için değil şeref için dövüşür.",
                        "choices": [{"text": "[Konuşmayı Bitir]", "next": "END", "effect": {}}]
                    }
                },
                3: {
                    "root": {
                        "text": "Aldric: Yarın her şey bitiyor. Alchemist, seninle geçirdiğim bu macera benim için bir şerefti.",
                        "choices": [
                            {"text": "Benim için de öyle dostum. Yarın zafer bizim olacak!", "next": "node_final", "effect": {"affection": 20}},
                            {"text": "Umarım yarın yeterince altın kazanırız.", "next": "node_final_bad", "effect": {"affection": -20}}
                        ]
                    },
                    "node_final": {
                        "text": "Aldric: Zaferle kal Alchemist! Dostluğumuz krallığın duvarları yıkılsa bile baki kalacak.",
                        "choices": [{"text": "[Konuşmayı Bitir]", "next": "END", "effect": {}}]
                    },
                    "node_final_bad": {
                        "text": "Aldric: Paradan başka bir şey düşünmüyorsun. Yazık, sana güvenmiştim.",
                        "choices": [{"text": "[Konuşmayı Bitir]", "next": "END", "effect": {}}]
                    }
                }
            },
            "seraphel": {
                1: {
                    "root": {
                        "text": "Seraphel: Büyü hatlarındaki dalgalanmalar zihnimi çok yoruyor. Bu dükkandaki elementlerin kokusu olmasa çoktan pes ederdim.",
                        "choices": [
                            {"text": "Zihnini dinlendir Seraphel. Yıldızlar seninle.", "next": "node_stars", "effect": {"affection": 12}},
                            {"text": "Büyü gücün bu laboratuvar için çok değerli, çalışmaya devam etmeliyiz.", "next": "node_work", "effect": {"morale": 15, "tiredness": 5}}
                        ]
                    },
                    "node_stars": {
                        "text": "Seraphel: Yıldızların bilgeliğini anlayan birini bulmak çok nadirdir... Teşekkür ederim, bu gece daha huzurluyum.",
                        "choices": [{"text": "[Konuşmayı Bitir]", "next": "END", "effect": {}}]
                    },
                    "node_work": {
                        "text": "Seraphel: Sürekli çalışmak... Beni bir köle gibi görmeyi bırakmalısın. Enerjimi doğru yönetmeliyim.",
                        "choices": [{"text": "[Konuşmayı Bitir]", "next": "END", "effect": {}}]
                    }
                },
                2: {
                    "root": {
                        "text": "Seraphel: İkinci gecede kadim parşömenlerde garip kehanetler gördüm. Zaman daralıyor gibi hissediyorum.",
                        "choices": [
                            {"text": "Ne olursa olsun seni koruyacağım, kehanetleri birlikte aşacağız.", "next": "node_protect", "effect": {"affection": 20}},
                            {"text": "Boşver parşömenleri, yarınki iksir malzemelerine odaklan.", "next": "node_focus", "effect": {"affection": -10, "morale": 10}}
                        ]
                    },
                    "node_protect": {
                        "text": "Seraphel: (Sana bakar) Bir fani için çok cesurca bir söz... Hoşuma gitti. Belki de kader ortaklığımız gerçektir.",
                        "choices": [{"text": "[Konuşmayı Bitir]", "next": "END", "effect": {}}]
                    },
                    "node_focus": {
                        "text": "Seraphel: Maddiyatçı vizyonsuzluğun beni benden alıyor Alchemist. Kadim sırlar iksirlerden daha değerlidir.",
                        "choices": [{"text": "[Konuşmayı Bitir]", "next": "END", "effect": {}}]
                    }
                },
                3: {
                    "root": {
                        "text": "Seraphel: Büyük finale geldik. Yarın tüm büyülü güçlerimi senin için seferber edeceğim. Bana ne söylemek istersin?",
                        "choices": [
                            {"text": "Senin büyün ve benim iksirlerim bu dünyayı değiştirecek.", "next": "node_final_good", "effect": {"affection": 25}},
                            {"text": "Umarım yarın görev başarısız olmaz.", "next": "node_final_bad", "effect": {"morale": -15}}
                        ]
                    },
                    "node_final_good": {
                        "text": "Seraphel: Dünyayı değiştirmek mi? İddialı... Ama seninle neden olmasın? Yarın her şeyimizi ortaya koyalım.",
                        "choices": [{"text": "[Konuşmayı Bitir]", "next": "END", "effect": {}}]
                    },
                    "node_final_bad": {
                        "text": "Seraphel: Son saniyede bile sadece endişe ve güvensizlik... Sana olan inancımı sarsıyorsun.",
                        "choices": [{"text": "[Konuşmayı Bitir]", "next": "END", "effect": {}}]
                    }
                }
            }
        }

    def start_night_dialogue(self, hero_name, day_num):
        self.hero_name = hero_name.lower()
        self.display_name = hero_name.capitalize()
        self.day_num = day_num
        self.current_node = "root"
        self.selected_index = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            hero_tree = self.story_data.get(self.hero_name, {}).get(self.day_num, {})
            node = hero_tree.get(self.current_node, {})
            choices = node.get("choices", [])
            
            if not choices:
                return

            if event.key in [pygame.K_w, pygame.K_UP]:
                self.selected_index = (self.selected_index - 1) % len(choices)
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                self.selected_index = (self.selected_index + 1) % len(choices)
            elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                chosen = choices[self.selected_index]
                self._apply_effects(chosen.get("effect", {}))
                
                next_node = chosen.get("next", "END")
                if next_node == "END":
                    # Chat durumu güncellemesi
                    for key in [self.hero_name.capitalize(), self.hero_name]:
                        hdata = self.game.runtime_heroes.get(key)
                        if hdata:
                            if isinstance(hdata, dict): hdata["chat_completed"] = True
                            else: hdata.chat_completed = True
                    
                    if hasattr(self.game, "night_completed"): self.game.night_completed = True
                    if hasattr(self.game, "dialogue_completed"): self.game.dialogue_completed = True
                    
                    if hasattr(self.game, "next_day"):
                        self.game.next_day()
                    elif hasattr(self.game, "complete_night"):
                        self.game.complete_night()
                    
                    if "heroes" in getattr(self.game, "scenes", {}):
                        self.game.change_scene("heroes")
                    elif "main_shop" in getattr(self.game, "scenes", {}):
                        self.game.change_scene("main_shop")
                    else:
                        all_scenes = list(getattr(self.game, "scenes", {}).keys())
                        if all_scenes: self.game.change_scene(all_scenes[0])
                else:
                    self.current_node = next_node
                    self.selected_index = 0

    def _apply_effects(self, effect_dict):
        hdata = self.game.runtime_heroes.get(self.hero_name.capitalize()) or self.game.runtime_heroes.get(self.hero_name)
        if not hdata: return
        is_dict = isinstance(hdata, dict)
        for stat, delta in effect_dict.items():
            if stat in ["affection", "morale", "tiredness", "tired"]:
                # İsim eşleme koruması
                target_stat = stat
                if stat in ["tiredness", "tired"]:
                    if is_dict: target_stat = "tired" if "tired" in hdata else "tiredness"
                    else: target_stat = "tired" if hasattr(hdata, "tired") else "tiredness"
                
                val = hdata.get(target_stat, 50 if stat!="tired" else 0) if is_dict else getattr(hdata, target_stat, 50 if stat!="tired" else 0)
                new_val = max(0, min(100, val + delta))
                if is_dict: hdata[target_stat] = new_val
                else: setattr(hdata, target_stat, new_val)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((15, 12, 28))
        hdata = self.game.runtime_heroes.get(self.hero_name.capitalize()) or self.game.runtime_heroes.get(self.hero_name)
        aff_val, mor_val, trd_val = 50, 50, 0
        if hdata:
            is_d = isinstance(hdata, dict)
            aff_val = hdata.get("affection", 50) if is_d else getattr(hdata, "affection", 50)
            mor_val = hdata.get("morale", 50) if is_d else getattr(hdata, "morale", 50)
            t_key = "tired" if (is_d and "tired" in hdata) or (not is_d and hasattr(hdata, "tired")) else "tiredness"
            trd_val = hdata.get(t_key, 0) if is_d else getattr(hdata, t_key, 0)

        # --- PANEL 1: KAHRAMAN KARTI ---
        card_rect = pygame.Rect(80, 160, 280, 460)
        pygame.draw.rect(screen, (32, 26, 56), card_rect, border_radius=15)
        pygame.draw.rect(screen, (110, 80, 180), card_rect, width=2, border_radius=15)
        
        screen.blit(self.title_font.render(self.display_name, True, (255, 255, 255)), (card_rect.x + 20, card_rect.y + 15))
        h_class = self.hero_classes.get(self.hero_name, "Companion")
        screen.blit(self.sub_font.render(f"Class: {h_class}", True, (255, 180, 80)), (card_rect.x + 20, card_rect.y + 45))

        img_rect = pygame.Rect(card_rect.x + 20, card_rect.y + 70, 240, 210)
        hero_img = self.hero_images.get(self.hero_name)
        if hero_img: screen.blit(hero_img, img_rect.topleft)
        else: pygame.draw.rect(screen, (22, 18, 40), img_rect, border_radius=10)

        self._draw_mini_bar(screen, card_rect.x + 20, card_rect.y + 295, 240, aff_val, "Affection", (220, 110, 160))
        self._draw_mini_bar(screen, card_rect.x + 20, card_rect.y + 345, 240, mor_val, "Morale", (100, 180, 220))
        self._draw_mini_bar(screen, card_rect.x + 20, card_rect.y + 395, 240, trd_val, "Tiredness", (220, 120, 80))

        # --- PANEL 2: METİN VE SEÇENEKLER ---
        dialogue_rect = pygame.Rect(390, 160, 550, 460)
        pygame.draw.rect(screen, (22, 18, 40), dialogue_rect, border_radius=15)
        pygame.draw.rect(screen, (75, 55, 130), dialogue_rect, width=1, border_radius=15)
        
        # Gelişmiş Word Wrap (Kutudan Taşmayı Engeller)
        def wrap_text(text, max_w):
            words = text.split(' ')
            lines = []
            curr = ""
            for w in words:
                if self.text_font.size(curr + w)[0] < max_w:
                    curr += w + " "
                else:
                    lines.append(curr)
                    curr = w + " "
            lines.append(curr)
            return lines

        # Ana Diyaloğu Çizdir
        node = self.story_data.get(self.hero_name, {}).get(self.day_num, {}).get(self.current_node, {"text": "...", "choices": []})
        lines = wrap_text(node["text"], dialogue_rect.width - 50)
        y_offset = dialogue_rect.y + 25
        for line in lines:
            screen.blit(self.text_font.render(line, True, (210, 200, 240)), (dialogue_rect.x + 25, y_offset))
            y_offset += 22
            
        y_offset += 25 # Seçenekler için güvenli pay
        
        # Seçenekleri de Satırlara Bölerek Çizdir (Taşma Çözümü)
        choices = node.get("choices", [])
        for idx, choice in enumerate(choices):
            is_selected = (idx == self.selected_index)
            color = (255, 200, 80) if is_selected else (140, 130, 170)
            prefix = "> " if is_selected else "  "
            
            choice_lines = wrap_text(prefix + choice["text"], dialogue_rect.width - 60)
            for c_line in choice_lines:
                screen.blit(self.text_font.render(c_line, True, color), (dialogue_rect.x + 25, y_offset))
                y_offset += 22
            y_offset += 8 # Seçenek araları boşluğu

        lbl_nav = self.sub_font.render("Use W/S or UP/DOWN Arrow Keys to navigate, press SPACE or ENTER to select.", True, (100, 90, 130))
        screen.blit(lbl_nav, (dialogue_rect.centerx - lbl_nav.get_width()//2, dialogue_rect.bottom - 25))

    def _draw_mini_bar(self, screen, x, y, width, value, label, color):
        lbl = self.stat_font.render(f"{label}: {int(value)}/100", True, (200, 190, 220))
        screen.blit(lbl, (x, y))
        bg_rect = pygame.Rect(x, y + 22, width, 10)
        pygame.draw.rect(screen, (15, 12, 24), bg_rect, border_radius=3)
        fill_width = int((value / 100.0) * width)
        if fill_width > 0:
            pygame.draw.rect(screen, color, pygame.Rect(x, y + 22, fill_width, 10), border_radius=3)