"""
Главный модуль приложения "Генератор цитат и фактов".
"""
import tkinter as tk
from gui import QuoteGeneratorGUI


def main():
    """Точка входа в приложение."""
    root = tk.Tk()
    app = QuoteGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

