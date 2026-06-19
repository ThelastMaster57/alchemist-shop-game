import pygame
import random
import math
from scenes.base import BaseScene

class ShopScene(BaseScene):
    """Daytime Shop Scene. Displays customers, stepping through lines of dialogue, and mixing recipes in the cauldron."""
    def __init__(self, game):
        super().__init__(game)
        
        # Pot state
        self.pot_contents = {}
        
        # Customer state
        self.customers_queue = []
        self.current_customer_idx = 0
        self.dialogue_page = 0
        
        # Ingredients pool
        self.ingredients_pool = ["dragonsblood", "ironbark", "moonflower", "glowmoss", "mistdew", "voidash"]
        
        # Color mapping for cauldron bubble visuals
        self.ing_colors = {
            "dragonsblood": (220, 50, 50),
            "ironbark": (139, 90, 43),
            "moonflower": (200, 200, 255),
            "glowmoss": (100, 220, 100),
            "mistdew": (150, 220, 255),
            "voidash": (50, 50, 60)
        }

        # UI rect structures
        self.ingredient_buttons = []
        for idx, ing in enumerate(self.ingredients_pool):
            x = 80 + idx * 145
            self.ingredient_buttons.append({
                "rect": pygame.Rect(x, 600, 130, 50),
                "key": ing
            })
            
        self.clear_button = pygame.Rect(780, 500, 160, 50)
        self.brew_button = pygame.Rect(580, 500, 180, 50)
        self.heroes_button = pygame.Rect(40, 25, 180, 45)
        self.cauldron_rect = pygame.Rect(387, 260, 250, 250)
        
        # Text box matching requested collision checks
        self.text_box_rect = pygame.Rect(250, 120, 550, 120)

    def parse_customer_data(self, data, fallback_name, fallback_potion, fallback_reward=40):
        """Safely extracts clean string variables and lists from user story.py structure."""
        if not data:
            return {
                "name": fallback_name,
                "lines": [f"Greetings. I am {fallback_name}.", f"I require a {fallback_potion}."],
                "request": fallback_potion,
                "reward": fallback_reward
            }
        
        # 1. Extract name
        name = ""
        for key in ["hero", "name", "hero_key", "customer", "customer_name"]:
            if isinstance(data, dict):
                if key in data:
                    name = data[key]
                    break
            else:
                if hasattr(data, key):
                    name = getattr(data, key)
                    break
        if not name:
            name = fallback_name
            
        # 2. Extract lines
        lines = []
        for key in ["intro_lines", "dialogue_lines", "all_lines", "dialogue", "lines"]:
            if isinstance(data, dict):
                if key in data:
                    val = data[key]
                    if isinstance(val, list):
                        lines = [str(x) for x in val]
                    elif isinstance(val, str):
                        lines = [val]
                    break
            else:
                if hasattr(data, key):
                    val = getattr(data, key)
                    if isinstance(val, list):
                        lines = [str(x) for x in val]
                    elif isinstance(val, str):
                        lines = [val]
                    break
        if not lines:
            lines = [f"Greetings, Alchemist. I am {name}.", f"I require a potion."]
            
        # 3. Extract request
        request = ""
        for key in ["potion", "request", "potion_key", "wanted"]:
            if isinstance(data, dict):
                if key in data:
                    request = data[key]
                    break
            else:
                if hasattr(data, key):
                    request = getattr(data, key)
                    break
        if not request:
            request = fallback_potion
            
        # 4. Extract reward
        reward = 0
        for key in ["reward", "gold", "price"]:
            if isinstance(data, dict):
                if key in data:
                    reward = data[key]
                    break
            else:
                if hasattr(data, key):
                    reward = getattr(data, key)
                    break
        if not reward:
            reward = fallback_reward
            
        return {
            "name": name,
            "lines": lines,
            "request": request,
            "reward": reward
        }

    def start_day(self):
        """Builds customer queue for the active day from data layer story pools."""
        self.pot_contents = {}
        self.customers_queue = []
        self.current_customer_idx = 0
        self.dialogue_page = 0
        
        try:
            import data.story as story
            
            # 1. Look up Daily Hero info
            daily_hero_data = None
            if hasattr(story, "DAILY_HEROES"):
                dh = story.DAILY_HEROES
                day_idx = self.game.day_number - 1
                if isinstance(dh, list) and 0 <= day_idx < len(dh):
                    daily_hero_data = dh[day_idx]
                elif isinstance(dh, dict):
                    daily_hero_data = dh.get(self.game.day_number) or dh.get(f"day_{self.game.day_number}")

            hero_parsed = self.parse_customer_data(daily_hero_data, "Aldric", "Health Potion", 80)
            self.customers_queue.append(hero_parsed)

            # 2. Look up Townsfolk info
            townsfolk_list = []
            if hasattr(story, "get_two_townsfolk"):
                townsfolk_list = story.get_two_townsfolk()
            elif hasattr(story, "TOWNSFOLK_POOL"):
                if isinstance(story.TOWNSFOLK_POOL, list):
                    townsfolk_list = random.sample(story.TOWNSFOLK_POOL, min(2, len(story.TOWNSFOLK_POOL)))
                elif isinstance(story.TOWNSFOLK_POOL, dict):
                    keys = list(story.TOWNSFOLK_POOL.keys())
                    selected_keys = random.sample(keys, min(2, len(keys)))
                    townsfolk_list = [story.TOWNSFOLK_POOL[k] for k in selected_keys]

            for tf in townsfolk_list:
                tf_parsed = self.parse_customer_data(tf, "Townsfolk", "Speed Potion", 40)
                self.customers_queue.append(tf_parsed)
        except Exception as e:
            print(f"Error compiling shop queue: {e}")
            # Fallback queue
            self.customers_queue = [
                {
                    "name": "Aldric", 
                    "lines": ["Greetings, Alchemist. I am Aldric.", "I am heading out to clear the Bandit Camp.", "I need a Health Potion to survive the raid."], 
                    "request": "Health Potion", 
                    "reward": 80
                },
                {
                    "name": "Garrick", 
                    "lines": ["Hello there.", "My muscles ache from forging armor.", "I need a Strength Potion to keep lifting my hammer."], 
                    "request": "Strength Potion", 
                    "reward": 45
                }
            ]

        self.load_customer()

    def get_current_customer(self):
        """Getter for active queue index customer data."""
        if 0 <= self.current_customer_idx < len(self.customers_queue):
            return self.customers_queue[self.current_customer_idx]
        return None

    def load_customer(self):
        """Loads and prepares variables for the current customer order."""
        self.pot_contents = {}
        self.dialogue_page = 0
        
        # If queue is finished, change scene to missions planner roster
        if self.current_customer_idx >= len(self.customers_queue):
            self.game.phase = "DAY"
            self.game.scenes["heroes"].set_mode("missions")
            self.game.change_scene("heroes")
        else:
            self.game.change_scene("shop")

    def get_recipe_text(self, potion_name):
        """Looks up a recipe from data/potions.py POTIONS[potion_key]['recipe'] structure."""
        try:
            import data.potions as potions
            if hasattr(potions, "POTIONS"):
                pot_data = potions.POTIONS.get(potion_name)
                if pot_data:
                    recipe_list = None
                    if isinstance(pot_data, dict):
                        recipe_list = pot_data.get("recipe")
                    elif isinstance(pot_data, list):
                        recipe_list = pot_data
                    
                    if recipe_list:
                        if isinstance(recipe_list, list):
                            counts = {}
                            for ing in recipe_list:
                                counts[ing] = counts.get(ing, 0) + 1
                            parts = [f"{count}x {ing}" for ing, count in counts.items()]
                            return ", ".join(parts)
                        elif isinstance(recipe_list, dict):
                            parts = [f"{count}x {ing}" for ing, count in recipe_list.items()]
                            return ", ".join(parts)
        except Exception as e:
            print(f"Error fetching recipe: {e}")
        return "Unknown Ingredients"

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            cust = self.get_current_customer()
            
            # 1. If there's a customer and they are still talking, clicking advances text
            if cust and self.dialogue_page < len(cust["lines"]) - 1:
                if self.text_box_rect.collidepoint(pos):
                    self.dialogue_page += 1
                    return
                # Return immediately, locking ingredient shelf logically
                return

            # 2. If no customers remain, clicking the screen or roster button changes scene to heroes safely
            if not cust:
                if self.text_box_rect.collidepoint(pos) or self.heroes_button.collidepoint(pos):
                    self.game.phase = "DAY"
                    self.game.scenes["heroes"].set_mode("missions")
                    self.game.change_scene("heroes")
                return

            # 3. Ingredients shelf only unlocks after dialogue is fully read
            for btn in self.ingredient_buttons:
                if btn["rect"].collidepoint(pos):
                    key = btn["key"]
                    self.pot_contents[key] = self.pot_contents.get(key, 0) + 1
                    return

            if self.clear_button.collidepoint(pos):
                self.pot_contents = {}
                return
                
            if self.brew_button.collidepoint(pos):
                from data.potions import check_recipe
                recipe_match = check_recipe(self.pot_contents)
                if cust and recipe_match == cust["request"]:
                    if "brewing" in self.game.scenes:
                        # Kazan ısı mini oyununu hazırlar ve sahneyi değiştirir
                        self.game.scenes["brewing"].setup_minigame(cust["request"], cust)
                        self.game.change_scene("brewing")
                return

            # 4. Roster button is always clickable if there's a customer active
            if self.heroes_button.collidepoint(pos):
                self.game.scenes["heroes"].set_mode("view")
                self.game.change_scene("heroes")
                
    def update(self, dt):
        pass

    def draw(self, screen):
        # Background: cozy alchemist lab
        screen.fill((25, 20, 40))

        # Shelves/Counters
        pygame.draw.rect(screen, (15, 12, 28), (0, 0, 1024, 580))
        pygame.draw.rect(screen, (80, 50, 30), (0, 550, 1024, 218))
        pygame.draw.rect(screen, (50, 30, 15), (0, 550, 1024, 10))

        # Top HUD bar
        pygame.draw.rect(screen, (35, 30, 55), (0, 0, 1024, 85))
        pygame.draw.line(screen, (130, 90, 229), (0, 85), (1024, 85), 2)

        # Draw Heroes Button
        mouse_pos = pygame.mouse.get_pos()
        hover_heroes = self.heroes_button.collidepoint(mouse_pos)
        h_color = (110, 70, 220) if hover_heroes else (80, 50, 170)
        pygame.draw.rect(screen, h_color, self.heroes_button, border_radius=8)
        pygame.draw.rect(screen, (180, 160, 255), self.heroes_button, width=2, border_radius=8)
        
        hud_font = pygame.font.SysFont("Trebuchet MS", 18, bold=True)
        lbl_hbtn = hud_font.render("Heroes Roster", True, (255, 255, 255))
        screen.blit(lbl_hbtn, (self.heroes_button.centerx - lbl_hbtn.get_width()//2, self.heroes_button.centery - lbl_hbtn.get_height()//2))

        # Gold display
        lbl_gold = hud_font.render(f"Gold: {self.game.gold}g", True, (255, 200, 50))
        screen.blit(lbl_gold, (screen.get_width() - lbl_gold.get_width() - 40, 32))

        # Day display
        lbl_day = hud_font.render(f"Day {self.game.day_number} (Shop Phase)", True, (220, 205, 255))
        screen.blit(lbl_day, (screen.get_width() // 2 - lbl_day.get_width() // 2, 32))

        # Render Customer Dialogue Box or finished state report
        cust = self.get_current_customer()
        is_dialogue_finished = False
        
        if cust:
            is_dialogue_finished = (self.dialogue_page >= len(cust["lines"]) - 1)
            
            # Dialogue Box Rect
            pygame.draw.rect(screen, (32, 24, 56), self.text_box_rect, border_radius=12)
            pygame.draw.rect(screen, (130, 90, 229), self.text_box_rect, width=2, border_radius=12)
            
            # Speaker Tag
            name_font = pygame.font.SysFont("Trebuchet MS", 18, bold=True)
            lbl_name = name_font.render(f"{cust['name']}:", True, (196, 175, 255))
            screen.blit(lbl_name, (self.text_box_rect.x + 20, self.text_box_rect.y + 12))

            # Dialogue Line (renders only index segment)
            text_font = pygame.font.SysFont("Arial", 16)
            current_line = cust["lines"][self.dialogue_page]
            lbl_line = text_font.render(current_line, True, (240, 240, 255))
            screen.blit(lbl_line, (self.text_box_rect.x + 20, self.text_box_rect.y + 38))

            if is_dialogue_finished:
                # Displays wants to buy
                req_text = f"Wants to buy: {cust['request']}"
                lbl_req = text_font.render(req_text, True, (255, 180, 80))
                screen.blit(lbl_req, (self.text_box_rect.x + 20, self.text_box_rect.y + 68))
                
                # Displays recipe formula text
                recipe_info = self.get_recipe_text(cust["request"])
                recipe_text = f"Recipe: {recipe_info}"
                lbl_recipe = text_font.render(recipe_text, True, (130, 230, 160))
                screen.blit(lbl_recipe, (self.text_box_rect.x + 20, self.text_box_rect.y + 88))
            else:
                # Blink continue indicator
                if (pygame.time.get_ticks() // 500) % 2 == 0:
                    lbl_cont = text_font.render("Click here to continue...", True, (150, 140, 180))
                    screen.blit(lbl_cont, (self.text_box_rect.right - lbl_cont.get_width() - 20, self.text_box_rect.bottom - 25))
        else:
            # End state indicator
            pygame.draw.rect(screen, (32, 24, 56), self.text_box_rect, border_radius=12)
            pygame.draw.rect(screen, (130, 90, 229), self.text_box_rect, width=2, border_radius=12)
            
            text_font = pygame.font.SysFont("Trebuchet MS", 18, bold=True)
            lbl_status = text_font.render("All customers served for today!", True, (120, 230, 150))
            screen.blit(lbl_status, (self.text_box_rect.centerx - lbl_status.get_width()//2, self.text_box_rect.y + 30))
            
            sub_font = pygame.font.SysFont("Arial", 16)
            lbl_prompt = sub_font.render("Click here or on Heroes Roster to plan missions.", True, (200, 200, 220))
            screen.blit(lbl_prompt, (self.text_box_rect.centerx - lbl_prompt.get_width()//2, self.text_box_rect.y + 65))

        # Draw the Cauldron in the center
        pygame.draw.ellipse(screen, (20, 20, 30), self.cauldron_rect)
        pygame.draw.ellipse(screen, (60, 60, 75), self.cauldron_rect, width=6)
        
        # Inner liquid surface
        liquid_rect = pygame.Rect(self.cauldron_rect.x + 15, self.cauldron_rect.y + 15, self.cauldron_rect.width - 30, self.cauldron_rect.height - 30)
        pygame.draw.ellipse(screen, (40, 25, 60), liquid_rect)

        # Bubble rendering based on dict contents
        bubbles_flat = []
        for ing, count in self.pot_contents.items():
            bubbles_flat.extend([ing] * count)

        for idx, ing in enumerate(bubbles_flat):
            color = self.ing_colors.get(ing, (150, 150, 150))
            angle = (idx * (360 / max(1, len(bubbles_flat)))) + (pygame.time.get_ticks() / 15.0)
            rad = math.radians(angle)
            dist = 40 + 10 * math.sin(pygame.time.get_ticks() / 200.0)
            bx = self.cauldron_rect.centerx + int(dist * math.cos(rad))
            by = self.cauldron_rect.centery + int(dist * math.sin(rad))
            
            pygame.draw.circle(screen, color, (bx, by), 16)
            pygame.draw.circle(screen, (255, 255, 255), (bx - 5, by - 5), 4) # reflection

        # Pot status texts
        status_font = pygame.font.SysFont("Trebuchet MS", 16)
        try:
            from data.potions import check_recipe
            recipe_match = check_recipe(self.pot_contents)
        except Exception:
            recipe_match = None
            
        if recipe_match:
            lbl_status = status_font.render(f"Cauldron: {recipe_match}", True, (80, 220, 100))
        else:
            lbl_status = status_font.render("Ingredients do not match a known recipe" if self.pot_contents else "Cauldron is empty", True, (180, 180, 200))
        screen.blit(lbl_status, (self.cauldron_rect.centerx - lbl_status.get_width()//2, self.cauldron_rect.bottom + 15))

        # List items in pot
        contents_parts = [f"{count}x {ing}" for ing, count in self.pot_contents.items()]
        contents_str = "Contents: " + (", ".join(contents_parts) if contents_parts else "Empty")
        lbl_contents = status_font.render(contents_str, True, (240, 240, 255))
        screen.blit(lbl_contents, (self.cauldron_rect.centerx - lbl_contents.get_width()//2, self.cauldron_rect.bottom + 40))

        # Ingredients shelf (Locked until dialogue is finished or if no customer remains)
        shelves_title_font = pygame.font.SysFont("Trebuchet MS", 18, bold=True)
        lbl_shelves = shelves_title_font.render("Ingredients Shelf", True, (220, 210, 250))
        screen.blit(lbl_shelves, (40, 565))

        shelf_enabled = is_dialogue_finished and (cust is not None)

        for btn in self.ingredient_buttons:
            rect = btn["rect"]
            ing = btn["key"]
            hover = rect.collidepoint(mouse_pos) and shelf_enabled
            color = self.ing_colors[ing]
            
            if shelf_enabled:
                bg_color = (color[0] // 2, color[1] // 2, color[2] // 2) if hover else (color[0] // 3, color[1] // 3, color[2] // 3)
                border_color = color
                text_color = (255, 255, 255)
            else:
                # Grayed out locked appearance
                bg_color = (30, 30, 35)
                border_color = (55, 55, 60)
                text_color = (80, 80, 85)
                
            pygame.draw.rect(screen, bg_color, rect, border_radius=10)
            pygame.draw.rect(screen, border_color, rect, width=2, border_radius=10)
            
            lbl_ing = status_font.render(ing.capitalize(), True, text_color)
            screen.blit(lbl_ing, (rect.centerx - lbl_ing.get_width()//2, rect.centery - lbl_ing.get_height()//2))

        # Lock text if dialogue not finished
        if not shelf_enabled:
            lock_font = pygame.font.SysFont("Trebuchet MS", 14, italic=True)
            lock_msg = "(Shelf locked - read dialogue to unlock)" if cust else "(No customers remaining)"
            lbl_lock = lock_font.render(lock_msg, True, (255, 120, 120))
            screen.blit(lbl_lock, (200, 568))

        # Clear Pot Button (only active if shelf unlocked)
        hover_clear = self.clear_button.collidepoint(mouse_pos) and shelf_enabled
        if shelf_enabled:
            c_color = (200, 60, 60) if hover_clear else (150, 40, 40)
            c_border = (255, 150, 150)
            c_text = (255, 255, 255)
        else:
            c_color = (40, 40, 45)
            c_border = (65, 65, 70)
            c_text = (90, 90, 95)
            
        pygame.draw.rect(screen, c_color, self.clear_button, border_radius=10)
        pygame.draw.rect(screen, c_border, self.clear_button, width=2, border_radius=10)
        lbl_clear = shelves_title_font.render("Clear Pot", True, c_text)
        screen.blit(lbl_clear, (self.clear_button.centerx - lbl_clear.get_width()//2, self.clear_button.centery - lbl_clear.get_height()//2))

        # Brew Button
        is_recipe_valid = False
        if cust and recipe_match == cust["request"]:
            is_recipe_valid = True
            
        hover_brew = self.brew_button.collidepoint(mouse_pos) and is_recipe_valid and shelf_enabled
        
        if is_recipe_valid and shelf_enabled:
            b_color = (130, 90, 229) if hover_brew else (100, 60, 190)
            b_border = (200, 180, 255)
            b_text = (255, 255, 255)
        else:
            b_color = (50, 45, 60)
            b_border = (80, 75, 90)
            b_text = (110, 105, 120)

        pygame.draw.rect(screen, b_color, self.brew_button, border_radius=10)
        pygame.draw.rect(screen, b_border, self.brew_button, width=2, border_radius=10)
        lbl_brew = shelves_title_font.render("Brew!", True, b_text)
        screen.blit(lbl_brew, (self.brew_button.centerx - lbl_brew.get_width()//2, self.brew_button.centery - lbl_brew.get_height()//2))