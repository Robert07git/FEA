# ui_modern.py
import customtkinter as ctk
from tkinter import messagebox

# === SETĂRI GLOBALE ===
ctk.set_appearance_mode("dark")      # "light" sau "dark"
ctk.set_default_color_theme("blue")  # "green", "dark-blue", etc.


class FEAQuizApp(ctk.CTk):
    """Aplicația principală FEA Quiz Trainer (interfață modernă)."""

    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer 2.0")
        self.geometry("900x600")
        self.resizable(False, False)

        # === CONTAINER PENTRU FRAME-URI ===
        self.container = ctk.CTkFrame(self, corner_radius=0)
        self.container.pack(fill="both", expand=True)

        # Dicționar pentru toate frame-urile
        self.frames = {}

        # Inițializăm frame-urile disponibile
        for F in (MainMenuFrame,):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Afișăm meniul principal
        self.show_frame("MainMenuFrame")

    def show_frame(self, frame_name):
        """Afișează un frame după nume."""
        frame = self.frames[frame_name]
        frame.tkraise()


class MainMenuFrame(ctk.CTkFrame):
    """Ecranul principal - hub-ul aplicației."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # === TITLU ===
        title = ctk.CTkLabel(self, text="FEA QUIZ TRAINER", font=("Poppins", 28, "bold"), text_color="#00E6E6")
        title.pack(pady=(40, 20))

        # === BUTOANE PRINCIPALE ===
        button_style = {"width": 250, "height": 45, "corner_radius": 10, "font": ("Poppins", 16, "bold")}

        ctk.CTkButton(self, text="🎯 TRAIN MODE", command=self.start_train, **button_style).pack(pady=10)
        ctk.CTkButton(self, text="🧾 EXAM MODE", command=self.start_exam, **button_style).pack(pady=10)
        ctk.CTkButton(self, text="📈 STATISTICI", command=self.open_stats, **button_style).pack(pady=10)
        ctk.CTkButton(self, text="📊 GRAFIC PROGRES", command=self.open_chart, **button_style).pack(pady=10)
        ctk.CTkButton(self, text="📚 LEARN MODE", command=self.learn_mode, **button_style).pack(pady=10)
        ctk.CTkButton(self, text="🏆 LEADERBOARD", command=self.leaderboard, **button_style).pack(pady=10)
        ctk.CTkButton(self, text="⚙️ SETĂRI", command=self.open_settings, **button_style).pack(pady=10)

        # === BUTON IEȘIRE ===
        ctk.CTkButton(self, text="⏻ Ieșire", fg_color="red", hover_color="#CC0000",
                      command=self.controller.destroy, width=200, height=40, font=("Poppins", 14, "bold")).pack(pady=30)

    # === FUNCȚII TEMPORARE ===
    def start_train(self):
        messagebox.showinfo("Train Mode", "Aici vom conecta modul TRAIN.")

    def start_exam(self):
        messagebox.showinfo("Exam Mode", "Aici vom conecta modul EXAM.")

    def open_stats(self):
        messagebox.showinfo("Statistici", "Aici vom deschide statistica utilizatorului.")

    def open_chart(self):
        messagebox.showinfo("Grafic progres", "Aici vom integra graficul matplotlib direct în UI.")

    def learn_mode(self):
        messagebox.showinfo("Learn Mode", "Aici va fi centrul de învățare FEA.")

    def leaderboard(self):
        messagebox.showinfo("Leaderboard", "Aici vom afișa topul scorurilor.")

    def open_settings(self):
        messagebox.showinfo("Setări", "Aici vor fi preferințele utilizatorului.")


if __name__ == "__main__":
    app = FEAQuizApp()
    app.mainloop()
