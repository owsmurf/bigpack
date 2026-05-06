"""
Удобный лаунчер для запуска приложения из корня проекта:

    python run.py
"""

from app.views.main_window import MainWindow


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
