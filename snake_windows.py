#!/usr/bin/env python3

# Snake game using tkinter which runs on Windows with zero external dependencies.
# Original curses version by EngineerMan (YouTube) / GithubYorkieWoW.
# Tkinter port preserves all original game logic with improved graphics and sprites.

# Play instructions:  Double click python file in download location OR navigate to game directory in terminal and run "python snake_windows.py"   
# no external dependencies needed — tkinter is a built in module

import tkinter as tk
import random

# Constants 
CELL    = 20        # pixel size of each grid cell
COLS    = 30        # number of columns
ROWS    = 25        # number of rows
WIDTH   = COLS * CELL
HEIGHT  = ROWS * CELL
SPEED   = 120       # milliseconds between ticks (lower = faster / harder)

# Retro grey & neon green colour palette
BG          = "#0d0d0d"
GRID        = "#1a1a1a"
SNAKE_HEAD  = "#39ff14"   # neon green
SNAKE_BODY  = "#1f8c0a"
FOOD_COL    = "#ff4136"
FOOD_SHINE  = "#ff8880"
SCORE_COL   = "#39ff14"
TITLE_COL   = "#39ff14"
DIM         = "#3a3a3a"
PANEL_BG    = "#111111"


# Game class 
class SnakeGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Py3Snake - Windows Edition")
        root.resizable(False, False)
        root.configure(bg=PANEL_BG)

        # Header
        header = tk.Frame(root, bg=PANEL_BG, pady=8)
        header.pack(fill="x")

        tk.Label(
            header, text="◈ Py3Snake - Windows Edition ◈",
            font=("Consolas", 16, "bold"),
            fg=TITLE_COL, bg=PANEL_BG
        ).pack(side="left", padx=16)

        self.score_var = tk.StringVar(value="Score  000")
        tk.Label(
            header, textvariable=self.score_var,
            font=("Consolas", 16, "bold"),
            fg=SCORE_COL, bg=PANEL_BG
        ).pack(side="right", padx=16)

        # game area (canvas)
        self.canvas = tk.Canvas(
            root,
            width=WIDTH, height=HEIGHT,
            bg=BG, highlightthickness=2,
            highlightbackground=SNAKE_HEAD
        )
        self.canvas.pack(padx=12, pady=(0, 4))

        # footer
        footer = tk.Frame(root, bg=PANEL_BG, pady=6)
        footer.pack(fill="x")
        tk.Label(
            footer,
            text="Controls = Arrow Keys / WASD  ·  R = Restart  ·  Q = Quit\n Original game by EngineerMan on YouTube, ported by Github.com/YorkieWoW",
            font=("Consolas", 9),
            fg=DIM, bg=PANEL_BG
        ).pack()

        # keybinds (arrow keys & WASD control movement)
        for key in ("<Up>","<Down>","<Left>","<Right>",
                    "w","a","s","d","W","A","S","D",
                    "r","R","q","Q"):
            root.bind(key, self.on_key)

        # Draw static grid once onto a background image
        self._draw_grid()

        # Start first game
        self.reset()

    # Grid (drawn once, reused every frame via tag)
    def _draw_grid(self):
        for c in range(COLS + 1):
            x = c * CELL
            self.canvas.create_line(x, 0, x, HEIGHT, fill=GRID, tags="grid")
        for r in range(ROWS + 1):
            y = r * CELL
            self.canvas.create_line(0, y, WIDTH, y, fill=GRID, tags="grid")

    # State reset
    def reset(self):
        self.score     = 0
        self.game_over = False
        self.paused    = False

        sc = COLS // 4
        sr = ROWS // 2
        self.snake     = [(sc, sr), (sc - 1, sr), (sc - 2, sr)]
        self.direction = (1, 0)   # (dc, dr) — moving right
        self.next_dir  = (1, 0)

        self.food = self._new_food()
        self.score_var.set(f"Score  {self.score:03d}")

        # Cancel any pending tick, then start fresh
        if hasattr(self, "_after_id"):
            self.root.after_cancel(self._after_id)
        self._tick()

    # Food placement
    def _new_food(self):
        snake_set = set(self.snake)
        while True:
            pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if pos not in snake_set:
                return pos

    # Key handler
    def on_key(self, event):
        k = event.keysym.lower()

        if k in ("r",):
            self.reset()
            return
        if k in ("q",):
            self.root.destroy()
            return

        dir_map = {
            "right": (1, 0), "d": (1, 0),
            "left":  (-1, 0), "a": (-1, 0),
            "down":  (0, 1),  "s": (0, 1),
            "up":    (0, -1), "w": (0, -1),
        }
        new_dir = dir_map.get(k)
        if new_dir and not self.game_over:
            # Block 180° reversal
            if (new_dir[0] != -self.direction[0] or
                    new_dir[1] != -self.direction[1]):
                self.next_dir = new_dir

    # game loop / main tick
    def _tick(self):
        if not self.game_over:
            self.direction = self.next_dir
            self._update()
            self._draw()
        self._after_id = self.root.after(SPEED, self._tick)

    # update logic
    def _update(self):
        hc, hr = self.snake[0]
        dc, dr = self.direction
        new_head = ((hc + dc) % COLS, (hr + dr) % ROWS)

        # Self collision causes game over
        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.score_var.set(f"Score  {self.score:03d}")
            self.food = self._new_food()
        else:
            self.snake.pop()

    # Rendering
    def _draw(self):
        c = self.canvas
        c.delete("dynamic")   # clear last frame's sprites; grid stays

        # Food is a red circle with small shine effect
        fx, fy = self.food
        px, py = fx * CELL, fy * CELL
        c.create_oval(
            px + 3, py + 3, px + CELL - 3, py + CELL - 3,
            fill=FOOD_COL, outline="", tags="dynamic"
        )
        c.create_oval(
            px + 6, py + 5, px + 10, py + 8,
            fill=FOOD_SHINE, outline="", tags="dynamic"
        )

        # Snake body (draw tail → head so head renders on top)
        for i, (sc, sr) in enumerate(reversed(self.snake)):
            idx   = len(self.snake) - 1 - i
            is_head = (idx == 0)
            colour  = SNAKE_HEAD if is_head else SNAKE_BODY
            inset   = 2 if is_head else 3
            bx, by  = sc * CELL, sr * CELL
            c.create_rectangle(
                bx + inset, by + inset,
                bx + CELL - inset, by + CELL - inset,
                fill=colour, outline="", tags="dynamic"
            )
            # Eyes on head
            if is_head:
                dc_, dr_ = self.direction
                # Choose eye positions relative to travel direction
                if dc_ == 1:    # right
                    eyes = [(bx+14, by+5), (bx+14, by+13)]
                elif dc_ == -1: # left
                    eyes = [(bx+4,  by+5), (bx+4,  by+13)]
                elif dr_ == -1: # up
                    eyes = [(bx+5,  by+4), (bx+13, by+4)]
                else:           # down
                    eyes = [(bx+5,  by+14),(bx+13, by+14)]
                for ex, ey in eyes:
                    c.create_oval(ex, ey, ex+3, ey+3,
                                  fill=BG, outline="", tags="dynamic")

        # Game over overlay
        if self.game_over:
            # Semi transparent dark panel
            c.create_rectangle(
                WIDTH//2 - 140, HEIGHT//2 - 70,
                WIDTH//2 + 140, HEIGHT//2 + 80,
                fill="#0d0d0d", outline=SNAKE_HEAD, width=2, tags="dynamic"
            )
            c.create_text(
                WIDTH//2, HEIGHT//2 - 38,
                text="GAME OVER!",
                font=("Consolas", 22, "bold"),
                fill=FOOD_COL, tags="dynamic"
            )
            c.create_text(
                WIDTH//2, HEIGHT//2 + 4,
                text=f"Score: {self.score}",
                font=("Consolas", 16),
                fill=SCORE_COL, tags="dynamic"
            )
            c.create_text(
                WIDTH//2, HEIGHT//2 + 46,
                text="R = Restart   Q = Quit",
                font=("Consolas", 11),
                fill=DIM, tags="dynamic"
            )


# Entry point
if __name__ == "__main__":
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()
