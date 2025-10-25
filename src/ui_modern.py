# ui_modern.py
import customtkinter as ctk
from tkinter import messagebox

# === SETĂRI GLOBALE ===
ctk.set_appearance_mode("dark")      # Poți schimba în "light"
ctk.set_default_color_theme("blue")  # Variante: "blue", "green", "dark-blue"


class FEAQuizApp(ctk.CTk):
    """Aplicația principală FEA Quiz Trainer (interfață modernă)."""

    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer 2.0")
        self.geometry("900x600")
        self.resizable(False, False)

        # === CONTAINER PRINCIPAL ===
        self.container = ctk.CTkFrame(self, corner_radius=0)
        self.container.pack(fill="both", expand=True)

        # === FRAME-URI (ecrane) ===
        self.frames = {}
        for F in (MainMenuFrame,):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # === Afișăm meniul principal ===
        self.show_frame("MainMenuFrame")

    def show_frame(self, frame_name):
        """Afișează un frame după nume."""
        frame = self.frames[frame_name]
        frame.tkraise()


# ==============================================================
#                    MENIU PRINCIPAL MODERN
# ==============================================================

class MainMenuFrame(ctk.CTkFrame):
    """Ecranul principal - hub-ul aplicației modernizat."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # === CONTAINER CENTRAL ===
        main_container = ctk.CTkFrame(self)
        main_container.pack(expand=True)  # Centrează pe ambele axe (x și y)

        # === TITLU ===
        title = ctk.CTkLabel(
            main_container,
            text="FEA QUIZ TRAINER",
            font=("Poppins", 32, "bold"),
            text_color="#00E6E6"
        )
        title.pack(pady=(10, 30))

        # === GRUP DE BUTOANE ===
        button_style = {
            "width": 260,
            "height": 45,
            "corner_radius": 12,
            "font": ("Poppins", 16, "bold")
        }

        # Lista de butoane și acțiunile lor
        buttons = [
            ("🎯 TRAIN MODE", self.start_train),
            ("🧾 EXAM MODE", self.start_exam),
            ("📈 STATISTICI", self.open_stats),
            ("📊 GRAFIC PROGRES", self.open_chart),
            ("📚 LEARN MODE", self.learn_mode),
            ("🏆 LEADERBOARD", self.leaderboard),
            ("⚙️ SETĂRI", self.open_settings),
        ]

        for text, command in buttons:
            ctk.CTkButton(main_container, text=text, command=command, **button_style).pack(pady=8)

        # === BUTON IEȘIRE ===
        ctk.CTkButton(
            main_container,
            text="⏻ IEȘIRE",
            fg_color="#CC0000",
            hover_color="#990000",
            command=self.controller.destroy,
            width=180,
            height=40,
            font=("Poppins", 14, "bold")
        ).pack(pady=(35, 10))

    # === FUNCȚII TEMPORARE (vor fi conectate ulterior) ===
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


# ==============================================================
#                     RULARE APLICAȚIE
# ==============================================================

if __name__ == "__main__":
    app = FEAQuizApp()
    app.mainloop()
