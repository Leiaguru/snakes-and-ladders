import os
os.environ["KIVY_NO_CONSOLELOG"] = "1"
import math
import random
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex
from multiprocessing import freeze_support
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Rectangle, Line, Ellipse



class GameBoardWidget(Widget):
    def __init__(self, game_engine, **kwargs):
        super(GameBoardWidget, self).__init__(**kwargs)
        self.game = game_engine
        self.bind(pos=self.draw_everything, size=self.draw_everything)

    def get_cell_coordinates(self, position):
        if position < 1:
            position = 1
        grid_size = 10
        cell_width = self.width / grid_size
        cell_height = self.height / grid_size
        
        row = (position - 1) // grid_size
        col = (position - 1) % grid_size
        
        if row % 2 == 1:
            col = (grid_size - 1) - col
            
        x = self.x + (col * cell_width) + (cell_width / 2)
        y = self.y + (row * cell_height) + (cell_height / 2)
        return x, y, cell_width, cell_height

    def draw_everything(self, *args):
        self.canvas.clear()
        with self.canvas:
            # 1. Draw Board Grid & Tile Numbers
            for i in range(1, 101):
                x, y, w, h = self.get_cell_coordinates(i)
                hex_color = self.game.board_layout[i]
                
                Color(*get_color_from_hex(hex_color))
                Rectangle(pos=(x - w/2, y - h/2), size=(w, h))
                
                Color(1, 1, 1, 0.4)
                Line(rectangle=(x - w/2, y - h/2, w, h), width=1)
                
                text_color = (1, 1, 1, 1) if hex_color == "#2E7D32" else (0.1, 0.3, 0.1, 1)
                blabel = CoreLabel(text=str(i), font_size=max(h*0.25, 12), bold=True, color=text_color)
                blabel.refresh()
                
                Color(1, 1, 1, 1) 
                Rectangle(texture=blabel.texture, pos=(x - w/2 + 4, y - h/2 + 4), size=blabel.texture.size)

            # 2. Draw Ladders with Wide Spacing
            for start, end in self.game.ladders.items():
                x1, y1, _, _ = self.get_cell_coordinates(start)
                x2, y2, _, _ = self.get_cell_coordinates(end)
                dx, dy = x2 - x1, y2 - y1
                length = math.sqrt(dx**2 + dy**2)
                if length == 0: continue
                
                ox, oy = (-dy / length) * 14, (dx / length) * 14
                
                Color(*get_color_from_hex("#4E342E"))
                Line(points=[x1 + ox, y1 + oy, x2 + ox, y2 + oy], width=7, cap='round')
                Line(points=[x1 - ox, y1 - oy, x2 - ox, y2 - oy], width=7, cap='round')
                
                steps = int(length / 22)
                Color(*get_color_from_hex("#8D6E63"))
                for s in range(1, max(steps, 2)):
                    t = s / steps
                    rx, ry = x1 + t * dx, y1 + t * dy
                    Line(points=[rx + ox, ry + oy, rx - ox, ry - oy], width=3.5)

            # 3. Draw Realistic Snakes
            for start, info in self.game.snakes_data.items():
                x1, y1, _, _ = self.get_cell_coordinates(start)
                x2, y2, _, _ = self.get_cell_coordinates(info["end"])
                main_color = info["main"]
                pattern_color = info["pattern"]
                wave_frequency = info["waves"]
                
                dx, dy = x2 - x1, y2 - y1
                length = math.sqrt(dx**2 + dy**2)
                if length == 0: continue
                
                num_segments = 60
                points = []
                for i in range(num_segments + 1):
                    t = i / num_segments
                    bx = x1 + t * dx
                    by = y1 + t * dy
                    wave = math.sin(t * math.pi * wave_frequency) * 15 * (1 - (t * 0.7))
                    ox, oy = (-dy / length) * wave, (dx / length) * wave
                    points.append((bx + ox, by + oy))
                
                # Draw Tapering Segments
                for i in range(num_segments):
                    t = i / num_segments
                    thick = max(13 * (1 - t * 0.75), 3)
                    x_start, y_start = points[i]
                    x_end, y_end = points[i+1]
                    
                    Color(*get_color_from_hex(main_color))
                    Line(points=[x_start, y_start, x_end, y_end], width=thick, cap='round', joint='round')
                    
                    # Diamond Skin Patterns
                    if i % 4 == 0 and 3 < i < num_segments - 3:
                        mid_x = (x_start + x_end) / 2
                        mid_y = (y_start + y_end) / 2
                        r = thick * 0.35
                        if r > 1.5:
                            Color(*get_color_from_hex(pattern_color))
                            Line(points=[mid_x, mid_y - r, mid_x + r, mid_y, mid_x, mid_y + r, mid_x - r, mid_y, mid_x, mid_y - r], width=1.5)

                # FIX: Explicit tuple element indexing mapping for head direction vectors
                hx, hy = points[0][0], points[0][1]
                nx, ny = points[1][0], points[1][1]
                head_angle = math.atan2(hy - ny, hx - nx)
                
                tx = hx + math.cos(head_angle) * 16
                ty = hy + math.sin(head_angle) * 16
                Color(*get_color_from_hex("#FF1744"))
                Line(points=[hx, hy, tx, ty], width=2.5)
                Line(points=[tx, ty, tx + math.cos(head_angle + 0.4) * 6, ty + math.sin(head_angle + 0.4) * 6], width=1.8)
                Line(points=[tx, ty, tx + math.cos(head_angle - 0.4) * 6, ty + math.sin(head_angle - 0.4) * 6], width=1.8)
                
                Color(*get_color_from_hex(main_color))
                Ellipse(pos=(hx - 14, hy - 14), size=(28, 28))
                Color(0.1, 0.1, 0.1, 1)
                Line(circle=(hx, hy, 14), width=1.5)
                
                ex1, ey1 = hx + math.cos(head_angle + 0.5) * 6, hy + math.sin(head_angle + 0.5) * 6
                ex2, ey2 = hx + math.cos(head_angle - 0.5) * 6, hy + math.sin(head_angle - 0.5) * 6
                
                Color(*get_color_from_hex("#FFEA00"))
                Ellipse(pos=(ex1 - 4, ey1 - 4), size=(8, 8))
                Ellipse(pos=(ex2 - 4, ey2 - 4), size=(8, 8))
                
                Color(0, 0, 0, 1)
                Line(points=[ex1, ey1 - 3, ex1, ey1 + 3], width=1.5)
                Line(points=[ex2, ey2 - 3, ex2, ey2 + 3], width=1.5)

            # 4. Draw Player Tokens
            p1_pos = self.game.players[1]["pos"]
            p2_pos = self.game.players[2]["pos"]
            for p_id, p_data in self.game.players.items():
                px, py, pw, ph = self.get_cell_coordinates(p_data["pos"])
                if self.game.animating_player_id == p_id and self.game.current_anim_coords:
                    px, py = self.game.current_anim_coords
                else:
                    if p1_pos == p2_pos:
                        offset_x = -pw * 0.2 if p_id == 1 else pw * 0.2
                        px += offset_x
                Color(*get_color_from_hex(p_data["color"]))
                Ellipse(pos=(px - pw*0.22, py - ph*0.22), size=(pw*0.44, ph*0.44))
                Color(0.13, 0.13, 0.13, 1)
                Line(circle=(px, py, pw*0.22), width=2)


class DiceWidget(Widget):
    def __init__(self, **kwargs):
        super(DiceWidget, self).__init__(**kwargs)
        self.value = 1
        self.bounce_y = 0      
        self.scale_mod = 1.0   
        self.bind(pos=self.draw_dice, size=self.draw_dice)

    def set_value(self, val, bounce_y=0, scale_mod=1.0):
        self.value = val
        self.bounce_y = bounce_y
        self.scale_mod = scale_mod
        self.draw_dice()

    def draw_dice(self, *args):
        self.canvas.clear()
        with self.canvas:
            side = min(self.width, self.height) * 0.65 * self.scale_mod
            cx = self.x + self.width / 2
            cy = self.y + self.height / 2 + self.bounce_y
            
            Color(1, 1, 1, 1)
            Rectangle(pos=(cx - side/2, cy - side/2), size=(side, side))
            Color(0.2, 0.2, 0.2, 1)
            Line(rectangle=(cx - side/2, cy - side/2, side, side), width=2)
            
            r = side * 0.08
            offset = side * 0.25
            
            pips_map = {
                1: [(0, 0)],
                2: [(-offset, -offset), (offset, offset)],
                3: [(-offset, -offset), (0, 0), (offset, offset)],
                4: [(-offset, -offset), (-offset, offset), (offset, -offset), (offset, offset)],
                5: [(-offset, -offset), (-offset, offset), (0, 0), (offset, -offset), (offset, offset)],
                6: [(-offset, -offset), (-offset, 0), (-offset, offset), (offset, -offset), (offset, 0), (offset, offset)]
            }
            
            Color(0.1, 0.1, 0.1, 1)
            for ox, oy in pips_map.get(self.value, [(0, 0)]):
                Ellipse(pos=(cx + ox - r, cy + oy - r), size=(r*2, r*2))


class JungleSnakeLadderGame(BoxLayout):
    def __init__(self, **kwargs):
        super(JungleSnakeLadderGame, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.tile_colors = ["#2E7D32", "#A1D6E2", "#EAE6CA", "#81C784", "#C8E6C9"]
        board_random = random.Random(42)
        self.board_layout = [board_random.choice(self.tile_colors) for _ in range(101)]
        self.snakes_data = {
            17: {"end": 7,  "main": "#D50000", "pattern": "#FFEA00", "waves": 2.5},
            33: {"end": 11, "main": "#00E676", "pattern": "#FF6D00", "waves": 2.0},
            39: {"end": 23, "main": "#AA00FF", "pattern": "#00E676", "waves": 1.5},
            54: {"end": 34, "main": "#00C853", "pattern": "#AA00FF", "waves": 3.0},
            62: {"end": 19, "main": "#2962FF", "pattern": "#FF6D00", "waves": 3.5},
            64: {"end": 60, "main": "#AA00FF", "pattern": "#00E676", "waves": 1.2},
            87: {"end": 36, "main": "#00B8D4", "pattern": "#FFFFFF", "waves": 4.0},
            93: {"end": 73, "main": "#FF6D00", "pattern": "#212121", "waves": 2.5},
            95: {"end": 75, "main": "#212121", "pattern": "#00E676", "waves": 2.5},
            98: {"end": 79, "main": "#FFD600", "pattern": "#D50000", "waves": 2.5}
        }
        self.ladders = {4: 14, 9: 31, 21: 42, 28: 84, 51: 67, 72: 91, 80: 99}
        self.players = {
            1: {"name": "Player 1", "pos": 1, "color": "#FF1744"},
            2: {"name": "Player 2", "pos": 1, "color": "#29B6F6"}
        }
        self.current_player = 1
        self.is_game_over = False
        self.is_animating = False
        self.rolled_six = False
        self.animating_player_id = None
        self.current_anim_coords = None
        self.setup_ui()

    def setup_ui(self):
        self.control_panel = BoxLayout(orientation='vertical', size_hint_x=0.3, padding=10, spacing=10)
        with self.control_panel.canvas.before:
            Color(*get_color_from_hex("#CFD8DC"))
            self.bg_rect = Rectangle(pos=self.control_panel.pos, size=self.control_panel.size)
        self.control_panel.bind(pos=self._update_bg, size=self._update_bg)

        self.title_label = Label(text="Snakes &\nLadders", font_size='22sp', color=get_color_from_hex("#1B5E20"), bold=True, halign='center')
        self.turn_label = Label(text="Player 1's Turn!", font_size='15sp', color=get_color_from_hex("#FF1744"), bold=True, halign='center')
        
        self.dice_view = DiceWidget(size_hint_y=0.3)
        
        self.roll_button = Button(
            text="ROLL DICE!", background_color=get_color_from_hex("#FF1744"), 
            background_normal='', font_size='16sp', bold=True, color=(1,1,1,1)
        )
        self.roll_button.bind(on_press=self.play_turn)
        self.win_banner = Label(text="Rules:\n• Reach 100 to Win\n• Roll 6 for Extra Turn", font_size='12sp', color=get_color_from_hex("#37474F"), halign='center')
        self.reset_button = Button(text="Restart Game", background_color=get_color_from_hex("#E65100"), background_normal='', size_hint_y=0.15, bold=True)
        self.reset_button.bind(on_press=self.reset_game)

        self.control_panel.add_widget(self.title_label)
        self.control_panel.add_widget(self.turn_label)
        self.control_panel.add_widget(self.dice_view)
        self.control_panel.add_widget(self.roll_button)
        self.control_panel.add_widget(self.win_banner)
        self.control_panel.add_widget(self.reset_button)

        self.board_view = GameBoardWidget(self, size_hint_x=0.7)
        self.add_widget(self.control_panel)
        self.add_widget(self.board_view)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def sync_turn_indicators(self):
        if self.is_game_over: return
        p_data = self.players[self.current_player]
        self.roll_button.background_color = get_color_from_hex(p_data["color"])
        
        name = "Player 1" if self.current_player == 1 else "Player 2"
        text_fg = "#FF1744" if self.current_player == 1 else "#0288D1"
        self.turn_label.color = get_color_from_hex(text_fg)
        self.turn_label.text = f"{name}'s Turn!"

    def play_turn(self, instance):
        if self.is_game_over or self.is_animating: return
        self.is_animating = True
        self.roll_button.background_color = get_color_from_hex("#9E9E9E")
        self.dice_bounce_count = 0
        Clock.schedule_interval(self.bounce_dice, 0.04)

    def bounce_dice(self, dt):
        self.dice_bounce_count += 1
        rand_val = random.randint(1, 6)
        
        max_frames = 12
        progress = self.dice_bounce_count / max_frames
        
        current_bounce = math.sin(progress * math.pi) * 45
        current_scale = 1.0 + (math.sin(progress * math.pi) * 0.25)
        
        self.dice_view.set_value(rand_val, bounce_y=current_bounce, scale_mod=current_scale)
        
        if self.dice_bounce_count >= max_frames:
            final_value = random.randint(1, 6)
            self.dice_view.set_value(final_value, bounce_y=0, scale_mod=1.0)
            Clock.unschedule(self.bounce_dice)
            
            self.rolled_six = (final_value == 6)
            player = self.players[self.current_player]
            if player["pos"] + final_value > 100:
                self.finalize_turn()
            else:
                self.animate_tile_steps(final_value)

    def animate_tile_steps(self, remaining_steps):
        if remaining_steps <= 0:
            self.process_object_collisions()
            return
        player = self.players[self.current_player]
        player["pos"] += 1
        self.board_view.draw_everything()
        Clock.schedule_once(lambda dt: self.animate_tile_steps(remaining_steps - 1), 0.22)

    def process_object_collisions(self):
        player = self.players[self.current_player]
        start_pos = player["pos"]
        if start_pos in self.ladders:
            self.start_path_animation(start_pos, self.ladders[start_pos])
        elif start_pos in self.snakes_data:
            self.start_path_animation(start_pos, self.snakes_data[start_pos]["end"])
        else:
            self.finalize_turn()

    def start_path_animation(self, start, end):
        self.animating_player_id = self.current_player
        x1, y1, _, _ = self.board_view.get_cell_coordinates(start)
        x2, y2, _, _ = self.board_view.get_cell_coordinates(end)
        steps = 15
        self.anim_path = []
        for i in range(steps + 1):
            t = i / steps
            bx = x1 + t * (x2 - x1)
            by = y1 + t * (y2 - y1)
            self.anim_path.append((bx, by))
        self.anim_step_idx = 0
        Clock.schedule_interval(self.frame_path_animation, 0.03)

    def frame_path_animation(self, dt):
        if self.anim_step_idx >= len(self.anim_path):
            Clock.unschedule(self.frame_path_animation)
            player = self.players[self.current_player]
            if player["pos"] in self.ladders:
                player["pos"] = self.ladders[player["pos"]]
            elif player["pos"] in self.snakes_data:
                player["pos"] = self.snakes_data[player["pos"]]["end"]
            self.animating_player_id = None
            self.current_anim_coords = None
            self.board_view.draw_everything()
            self.finalize_turn()
            return
        self.current_anim_coords = self.anim_path[self.anim_step_idx]
        self.board_view.draw_everything()
        self.anim_step_idx += 1

    def finalize_turn(self):
        player = self.players[self.current_player]
        if player["pos"] == 100:
            self.is_game_over = True
            self.is_animating = False
            self.turn_label.text = "WINNER!"
            self.win_banner.text = f"Player {self.current_player}\nWon the Match!"
            return
        if self.rolled_six:
            self.is_animating = False
            self.sync_turn_indicators()
            self.turn_label.text += "\nROLL AGAIN!"
            return
        self.current_player = 2 if self.current_player == 1 else 1
        self.is_animating = False
        self.sync_turn_indicators()

    def reset_game(self, instance):
        self.players[1]["pos"] = 1
        self.players[2]["pos"] = 1
        self.current_player = 1
        self.is_game_over = False
        self.is_animating = False
        self.rolled_six = False
        self.animating_player_id = None
        self.current_anim_coords = None
        self.dice_view.set_value(1, bounce_y=0, scale_mod=1.0)
        self.win_banner.text = "Rules:\n• Reach 100 to Win\n• Roll 6 for Extra Turn"
        self.sync_turn_indicators()
        self.board_view.draw_everything()

class JungleSnakeLadderApp(App):
    def build(self):
        self.title = "Snakes and Ladders"
        return JungleSnakeLadderGame()

if __name__ == "__main__":
    freeze_support()
    JungleSnakeLadderApp().run()
