import os
import asyncio

from settings import SITE, DATABASE_PATH

from src import driver
from database.models import base, engine


def check_for_database() -> None:
    if os.path.exists(DATABASE_PATH):
        decision: str = input("Database already exists. Continue with (o)ld or create (n)ew? [o/n]:")
    if decision == "n":
        os.remove(DATABASE_PATH)
        base.metadata.create_all(engine)
    elif decision == "o":
        pass
    else:
        print("unclear decision")
        exit()


def main():
    # check if a database already exists
    check_for_database()

    # start scraper
    if "instagram" in SITE:
        from src.instagram import login_handler, profile_scraper
        login_handler()
        asyncio.run(profile_scraper())

    driver.quit()



if __name__ == "__main__":
    main()

