import tkinter as tk
import time
from gui import FEATrainerApp

class SplashScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("500x300")
        self.configure(bg="#111")
        self.overrideredirect(True)

        tk.Label(self, text="FEA Quiz Trainer",
                 font=("Segoe UI", 22, "bold"),
                 fg="#00FFFF", bg="#111").pack(pady=60)
        self.status = tk.Label(self, text="Se încarcă aplicația...",
                               font=("Segoe UI", 11),
                               fg="white", bg="#111")
        self.status.pack(pady=10)

        self.progress = tk.Frame(self, bg="#222", width=350, height=20)
        self.progress.pack(pady=15)
        self.progress.pack_propagate(False)
        self.progress_bar = tk.Frame(self.progress, bg="#00FFFF", width=0, height=20)
        self.progress_bar.pack(side="left", fill="y")

        self.animate()

    def animate(self):
        for i in range(0, 351, 7):
            self.progress_bar.config(width=i)
            self.status.config(text=f"Se încarcă aplicația... {int(i/3.5)}%")
            self.update()
            time.sleep(0.03)
        self.destroy()


if __name__ == "__main__":
    splash = SplashScreen()
    splash.after(100, splash.animate)
    splash.mainloop()

    app = FEATrainerApp()
    app.mainloop()
