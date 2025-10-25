import tkinter as tk
from gui import FEAGui

def main():
    """
    Punctul principal de intrare al aplicației FEA QUIZ.
    Lansează interfața grafică definită în gui.py.
    """
    root = tk.Tk()
    app = FEAGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
