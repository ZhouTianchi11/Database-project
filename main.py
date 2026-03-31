from config import set_theme
from app import ECommerceApp

if __name__ == "__main__":
    set_theme()
    app = ECommerceApp()
    app.mainloop()