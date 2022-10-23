import re
import logging
import asyncio

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import TimeoutException, JavascriptException

from src import driver
from src.database_operations import create_user_entry, create_following_relation

from database.models import session, User

from settings import SITE, TIMEOUT, USERNAME, PASSWORD, \
    COOKIE_OPTION, BLACKLIST, ROOT_PROFILES, TIMEOUT_FOLLOWER_LOADING

from settings import ENCODING, LOG_FILE, FORMAT, LEVEL


logging.basicConfig(
    format=FORMAT,
    filename=LOG_FILE,
    encoding=ENCODING,
    level=LEVEL
)


def login_handler() -> None:
    """accept cookies and execute login"""
    # open site
    driver.delete_all_cookies()
    driver.get(f"{SITE}")

    # accept_cookies
    WebDriverWait(driver, TIMEOUT).until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//*[contains(text(), '{COOKIE_OPTION}')]")
        )
    ).click()

    # wait for CSRF cookie to be set
    WebDriverWait(driver, TIMEOUT).until(
        EC.invisibility_of_element_located((
            By.XPATH, 
            f"//*[contains(text(), '{COOKIE_OPTION}')]"
        ))
    )

    # find username and password field
    (username_field, password_field) = WebDriverWait(driver, TIMEOUT).until(
        lambda driver: 
            (
                driver.find_element(By.NAME, "username"),
                driver.find_element(By.NAME, "password")
            )
    )

    # type in credential and login
    username_field.clear()
    username_field.send_keys(USERNAME)
    password_field.clear()
    password_field.send_keys(PASSWORD + Keys.RETURN)


def open_user_profile(user_handle: str) -> None:
    """open user profile using search bar"""
    # remove content from old profile
    driver.execute_script("""document.getElementsByTagName("main")[0].innerHTML='';""")

    # find search bar
    search_bar = WebDriverWait(driver, TIMEOUT).until(
        lambda driver: 
            driver.find_element(
                By.XPATH, 
                "//input[@placeholder='Search']"
            )
    )

    # clear search bar
    for _ in range(10):
        search_bar.clear()

    # search for user by user handle
    search_bar.send_keys(user_handle)

    # open profile
    WebDriverWait(driver, TIMEOUT).until(
        EC.element_to_be_clickable(
            (By.XPATH,f"//a[@href='/{user_handle}/?next=%2F']")
        )
    ).click()


def get_followers(user_handle: str) -> set:
    """create a list of users the current user is following"""
    # open modal with followers
    WebDriverWait(driver, TIMEOUT).until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//a[@href='/{user_handle}/following/?next=%2F']")
        )
    ).click()

    # wait until modal with followers appears
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.CLASS_NAME, "_aano"))
    )

    # scroll script
    driver.execute_script("""
        var obj = document.getElementsByClassName('_aano')[0];
        /* variables to keep track, if end is reached */
        var counter = 0;
        var height2 = 0;

        const inverval = setInterval(() => {
            /* scroll command */
	        obj.scrollTop = obj.scrollHeight;

            /* check if height has changed */
	        if (obj.scrollHeight == height2) {
		        counter++;
		        if (counter > 10) {
			        /* tell selenium to load user handles */
			        window.alert("finished");
			        clearInterval(inverval);
		        }
	        } else {
		        counter = 0;
	        }

	        height2 = obj.scrollHeight;
        }, 1000);
    """)

    # wait for end signifal from script
    WebDriverWait(driver, TIMEOUT_FOLLOWER_LOADING).until(
        EC.alert_is_present()
    )
    alert = Alert(driver)
    alert.accept()

    # remove suggestions
    driver.execute_script("""
        var objects = document.querySelectorAll('div[class=" _ab8s _ab8w  _ab94 _ab99 _ab9f _ab9m _ab9p  _aba8 _abcm"]');
        for (object of objects) {
            object.innerHTML="";
        }
    """)
    
    # get followers user handle
    followers = driver.find_elements(
        By.XPATH,
        "//span[@class='_aacl _aaco _aacw _aacx _aad7 _aade']"
    )
    followers: set = {re.sub("Verified", "", follower.text).strip() for follower in followers}

    # close modal before leaving profile
    driver.execute_script("""document.getElementsByClassName("_abl-")[3].click();""")

    return followers


async def profile_scraper() -> None:
    profiles = ROOT_PROFILES
    counter: int = 0
    create_profile_task = None
    create_following_relation_task = None

    # work through all profiles
    logging.info("START SCRAPING")
    while profiles:
        (user_handle, depth) = profiles.pop()

        # inform user about progress
        logging.info(f"Profiles finished: {counter}")
        logging.debug(f"Profiles in Queue: {profiles}")
        counter += 1

        try:
            # go to profile page
            open_user_profile(user_handle)

            # get profile data
            profile_data = WebDriverWait(driver, TIMEOUT).until(
                lambda driver: driver.find_element(By.CLASS_NAME, "_aa_c")
                    .text
                    .lower()
                    .splitlines()
            )

            # format data
            # TODO test thsi ll190-200
            username = profile_data[0]
            if "followed by" in profile_data[-1]:
                profile_data.pop(-1)
            profile: str = "\n".join(profile_data)
            
            profile_data.pop(0)
            biography: str = "\n".join(profile_data)

            # create entry from data
            if create_profile_task:
                await create_profile_task
            create_profile_task = asyncio.create_task(
                create_user_entry(user_handle, username, profile, biography)
            )
        except (TimeoutException, JavascriptException, IndexError):
            logging.error(f"Failed to file User. USERHANDLE: {user_handle}; DEPTH: {depth}")
            continue

        try:
            # log users which user is following
            followers: set = get_followers(user_handle)
            if create_following_relation_task:
                await create_following_relation_task
            create_following_relation_task = asyncio.create_task(create_following_relation(user_handle, followers))

            # add followed users to profile set
            if depth == 0:
                continue
            else:
                for follower_handle in followers:
                    if follower_handle in BLACKLIST:
                        continue
                    elif session.query(User).filter(User.user_handle == follower_handle).first():
                        continue
                    else:
                        profiles = profiles | {(follower_handle, depth - 1)}

        except (TimeoutException, JavascriptException, TypeError):
            # except if user account is private or the user followes nobody
            logging.warning(f"Failed to file following relationship of user. USER: {user_handle}.")
            continue


    if create_following_relation_task:
        await create_following_relation_task
    if create_profile_task:
        await create_profile_task

    logging.info("FINISHED SCRAPING")

