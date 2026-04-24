from app.config.settings import settings
from app.config.database import init_db

def main():
    print("Hello from finance-tracker-api!")
    init_db(cfg=settings)

if __name__ == "__main__":
    main()
