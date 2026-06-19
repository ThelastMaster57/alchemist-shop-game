import pygame
import sys
import random
from scenes.shop import ShopScene
from scenes.brewing import BrewingScene
from scenes.heroes import HeroesScene
from scenes.dialogue import DialogueScene
from scenes.results import ResultsScene
from scenes.base import BaseScene

# Title / Start Scene
class StartScene(BaseScene):
    """Initial game splash cover page. Sets a mysterious, alchemical atmosphere."""
    def __init__(self, game):
        super().__init__(game)
        self.btn_rect = pygame.Rect(387, 450, 250, 60)
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
            if self.btn_rect.collidepoint(mouse_pos):
                self.game.start_new_game()

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
        lbl_shadow = title_font.render("POTION & ALLIANCE", True, (60, 30, 100))
        screen.blit(lbl_shadow, (screen.get_width()//2 - lbl_shadow.get_width()//2 + 3, 200 + 3))

        lbl_title = title_font.render("POTION & ALLIANCE", True, (220, 200, 255))
        screen.blit(lbl_title, (screen.get_width()//2 - lbl_title.get_width()//2, 200))

        lbl_sub = subtitle_font.render("Alchemist's 3-Day Chronicles", True, (255, 180, 80))
        screen.blit(lbl_sub, (screen.get_width()//2 - lbl_sub.get_width()//2, 260))

        # Instructions
        desc_font = pygame.font.SysFont("Arial", 16)
        instr_y = 320
        instructions = [
            "1. Serve Daily Heroes and Townsfolk by mixing cauldron ingredients.",
            "2. Keep the temperature needle within the moving target to brew successfully.",
            "3. Send your Hero companion squads on dangerous day missions.",
            "4. Talk to them at night, balancing morale, tiredness and affection delta values.",
            "Complete 3 days to establish your legacy and secure their trust!"
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
        lbl_btn = btn_font.render("Start Chronicles", True, (255, 255, 255))
        screen.blit(lbl_btn, (self.btn_rect.centerx - lbl_btn.get_width()//2, self.btn_rect.centery - lbl_btn.get_height()//2))

        lbl_auth = author_font.render("Designed with Pygame and dynamic mechanics", True, (80, 80, 100))
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

        # Scenes dictionary
        self.scenes = {
            "start": StartScene(self),
            "shop": ShopScene(self),
            "brewing": BrewingScene(self),
            "heroes": HeroesScene(self),
            "dialogue": DialogueScene(self),
            "results": ResultsScene(self)
        }
        
        # Initial scene
        self.active_scene = self.scenes["start"]

    def change_scene(self, scene_name):
        """Transitions scene router."""
        if scene_name in self.scenes:
            self.active_scene = self.scenes[scene_name]

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
                else:
                    hdata.on_mission = False
                    hdata.chat_completed = False

        self.change_scene("start")

    def start_new_game(self):
        """Starts a clean play cycle starting on Day 1 Shop."""
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

        # Standardizing structure: check if objects or dictionaries, ensure fields exist
        for hname, hdata in self.runtime_heroes.items():
            if isinstance(hdata, dict):
                hdata.setdefault("on_mission", False)
                hdata.setdefault("chat_completed", False)
                hdata.setdefault("affection", 50)
                hdata.setdefault("morale", 50)
                hdata.setdefault("tired", 0)
            else:
                if not hasattr(hdata, "on_mission"): setattr(hdata, "on_mission", False)
                if not hasattr(hdata, "chat_completed"): setattr(hdata, "chat_completed", False)
                if not hasattr(hdata, "affection"): setattr(hdata, "affection", 50)
                if not hasattr(hdata, "morale"): setattr(hdata, "morale", 50)
                if not hasattr(hdata, "tired") and not hasattr(hdata, "tiredness"): setattr(hdata, "tired", 0)

        # Launch Day 1 Shop
        self.scenes["shop"].start_day()
        self.change_scene("shop")

    def get_fallback_heroes(self):
        """Constructs fallback hero dictionary structure."""
        return {
            "Aldric": {"affection": 30, "morale": 50, "tired": 20, "on_mission": False, "chat_completed": False},
            "Seraphel": {"affection": 20, "morale": 60, "tired": 10, "on_mission": False, "chat_completed": False},
            "Elysia": {"affection": 40, "morale": 45, "tired": 30, "on_mission": False, "chat_completed": False}
        }

    def execute_missions_and_results(self):
        """Processes mission success chance checks, edits stats and displays reports."""
        results = []
        gold_earned = 0
        
        for hname in ["Aldric", "Seraphel", "Elysia"]:
            hdata = self.runtime_heroes.get(hname)
            if not hdata:
                continue

            # Check if hero is dictionary or object
            is_dict = isinstance(hdata, dict)
            
            # Read variables
            affection = hdata.get("affection", 50) if is_dict else getattr(hdata, "affection", 50)
            morale = hdata.get("morale", 50) if is_dict else getattr(hdata, "morale", 50)
            tired = 0
            if is_dict:
                tired = hdata.get("tired", 0) if "tired" in hdata else hdata.get("tiredness", 0)
            else:
                tired = getattr(hdata, "tired", 0) if hasattr(hdata, "tired") else getattr(hdata, "tiredness", 0)

            on_mission = hdata.get("on_mission", False) if is_dict else getattr(hdata, "on_mission", False)

            # Calculations
            stats_change = {}
            if on_mission:
                title = self.scenes["heroes"].get_relationship_title(affection)
                success_chance = self.scenes["heroes"].get_success_chance(hname, title)
                roll = random.randint(1, 100)
                
                if roll <= success_chance:
                    # Mission SUCCESS
                    gold_reward = 100
                    gold_earned += gold_reward
                    
                    aff_chg = 10
                    mor_chg = 15
                    trd_chg = 25
                    
                    outcome = "SUCCESS"
                    message = f"{hname} conquered the dungeons, defeating the beast and bringing home {gold_reward} gold!"
                else:
                    # Mission FAILURE
                    gold_reward = 0
                    
                    aff_chg = -5
                    mor_chg = -20
                    trd_chg = 35
                    
                    outcome = "FAILURE"
                    message = f"{hname} encountered a dragon and was forced to flee. They returned wounded and discouraged."
                
                stats_change = {"affection": aff_chg, "morale": mor_chg, "tiredness": trd_chg}
            else:
                # Hero RESTED
                aff_chg = 0
                mor_chg = 5
                trd_chg = -40
                
                outcome = "REST"
                message = f"{hname} rested in the sanctuary, recuperating their health and reading spellbooks."
                stats_change = {"affection": aff_chg, "morale": mor_chg, "tiredness": trd_chg}

            # Apply delta changes and clamp bounds (0 to 100)
            new_aff = max(0, min(100, affection + aff_chg))
            new_mor = max(0, min(100, morale + mor_chg))
            new_trd = max(0, min(100, tired + trd_chg))

            if is_dict:
                hdata["affection"] = new_aff
                hdata["morale"] = new_mor
                if "tired" in hdata:
                    hdata["tired"] = new_trd
                else:
                    hdata["tiredness"] = new_trd
            else:
                setattr(hdata, "affection", new_aff)
                setattr(hdata, "morale", new_mor)
                if hasattr(hdata, "tired"):
                    setattr(hdata, "tired", new_trd)
                else:
                    setattr(hdata, "tiredness", new_trd)

            results.append({
                "hero_name": hname,
                "status": "mission" if on_mission else "rest",
                "outcome": outcome,
                "message": message,
                "stats_change": stats_change
            })

        self.gold += gold_earned
        
        # Check if day is 3 (Game Over condition)
        is_game_over = (self.day_number >= 3)
        
        if is_game_over:
            # Overwrite messages with final relationship assessments
            for r in results:
                hname = r["hero_name"]
                hdata = self.runtime_heroes.get(hname)
                is_dict = isinstance(hdata, dict)
                aff = hdata.get("affection", 50) if is_dict else getattr(hdata, "affection", 50)
                title = self.scenes["heroes"].get_relationship_title(aff)
                
                r["message"] = f"After 3 days, your bond with {hname} has solidified at {aff}/100 Affection. Your relationship status is: '{title.upper()}'."
                r["stats_change"] = {}

        self.scenes["results"].set_results(results, gold_earned, is_game_over)
        self.change_scene("results")

    def advance_day(self):
        """Advances cycle days, resets day layouts, and returns to daytime shop."""
        self.day_number += 1
        self.phase = "DAY"
        
        # Reset hero mission triggers
        for hname in ["Aldric", "Seraphel", "Elysia"]:
            hdata = self.runtime_heroes.get(hname)
            if hdata:
                if isinstance(hdata, dict):
                    hdata["on_mission"] = False
                    hdata["chat_completed"] = False
                else:
                    hdata.on_mission = False
                    hdata.chat_completed = False

        self.scenes["shop"].start_day()
        self.change_scene("shop")

    def run(self):
        """Main game loop."""
        while True:
            # Calculate dt in seconds
            dt = self.clock.tick(60) / 1000.0
            
            # 1. Event Dispatching
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Route events to active scene
                self.active_scene.handle_event(event)

            # 2. Logic Updates
            self.active_scene.update(dt)

            # 3. Canvas Drawing
            self.active_scene.draw(self.screen)
            pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
