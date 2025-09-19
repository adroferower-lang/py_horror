import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import threading
import time
import random
import pygame

# Файлы
GIF_FILE = "scary.gif"
MP3_FILE = "scary.mp3"
TIMER = 600  # 10 минут

class ScaryApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "black")
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+0+0")

        self.canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Загружаем gif
        self.frames = []
        gif = Image.open(GIF_FILE)
        for frame in ImageSequence.Iterator(gif):
            self.frames.append(ImageTk.PhotoImage(frame))
        self.gif_image = self.canvas.create_image(w//2, h//2, anchor="center", image=self.frames[0])

        # Таймер чуть ниже центра
        self.timer_text = self.canvas.create_text(
            w//2, h//2 + 100, text="", font=("Arial", 48, "bold"), fill="red", anchor="center"
        )

        self.frame_index = 0
        self.animate()

        # Кровь
        self.drops = []
        self.spawn_blood()
        self.move_drops()

        # Таймер и музыка
        threading.Thread(target=self.start_timer, daemon=True).start()
        threading.Thread(target=self.play_music, daemon=True).start()

        # Ловим попытку закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_attempt)

    def animate(self):
        self.canvas.itemconfig(self.gif_image, image=self.frames[self.frame_index])
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.root.after(100, self.animate)

    def start_timer(self):
        for i in range(TIMER, 0, -1):
            mins, secs = divmod(i, 60)
            self.canvas.itemconfig(self.timer_text, text=f"{mins:02}:{secs:02}")
            time.sleep(1)
        self.canvas.itemconfig(self.timer_text, text="😱 BOO! 😱")

    def play_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load(MP3_FILE)
        pygame.mixer.music.play(-1)

    # ---------------- Капли крови ----------------
    def spawn_blood(self):
        w = self.root.winfo_screenwidth()
        x = random.randint(0, w)
        size = 10
        drop = {
            "id": self.canvas.create_rectangle(x, 0, x+size, size, fill="red", outline=""),
            "x": x,
            "y": 0,
            "size": size
        }
        self.drops.append(drop)
        self.root.after(400, self.spawn_blood)

    def move_drops(self):
        h = self.root.winfo_screenheight()
        new_drops = []
        for drop in self.drops:
            drop["y"] += 3
            self.canvas.move(drop["id"], 0, 3)

            # След
            self.canvas.create_rectangle(
                drop["x"], drop["y"], drop["x"]+drop["size"], drop["y"]+3,
                fill="darkred", outline=""
            )

            if drop["y"] < h:
                new_drops.append(drop)
            else:
                self.canvas.delete(drop["id"])
        self.drops = new_drops
        self.root.after(50, self.move_drops)

    # ---------------- Попытка закрытия ----------------
    def on_close_attempt(self):
        # Меняем текст таймера на сообщение
        self.canvas.itemconfig(self.timer_text, text="поздно… слишком поздно…", fill="darkred")

root = tk.Tk()
app = ScaryApp(root)
root.mainloop()
