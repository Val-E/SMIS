"""Software Configurations and Settings"""

ENCODING: str = "utf-8"

# Paths
DATABASE_PATH: str ="database/database.db"
LOG_FILE: str ="log.log"

# logging settings
FORMAT: str = "%(asctime)s - %(levelname)s - %(message)s"
LEVEL: int = 10 # 10 - 40; DEBUG - ERROR


# Login Settings
SITE: str = ""
USERNAME: str = ""
PASSWORD: str = ""
COOKIE_OPTION: str = "Only allow essential cookies"


# targets settings
ROOT_PROFILES: set = {}
BLACKLIST: set = {}


# addition dictionaries and wordlists for different regions can be added to the set
# expected format: .txt; words separated by newline
FEMALE_NAMES_WORDLISTS: set = {"dictionaries/female_names_west.txt"}
MALE_NAMES_WORDLISTS: set = {"dictionaries/male_names_west.txt"}
AGE_INDICATORS_WORDLISTS: set = {"dictionaries/age_indicators.txt"}

# expected format: JSON; {"symbol/phrase/icon": "group/meaning/party"}
POLITICAL_DICTIONARIES: set = {"dictionaries/political_symbols.json"}

# expected format: JSON; {"pronoun": "sex"}
PRONOUNS_DICTIONARIES: set = {"dictionaries/pronouns.json"}

# expected format: JSON; {"symbol": "nation"}
COUNTRY_SYMBOLS_DICTIONARIES: set = {"dictionaries/country_symbols.json"}

# expected format: .csv; comma separated; name, country, subcountry
CITY_DICTIONARIES: set = {"dictionaries/world-cities.csv"}

# Performance Settings
TIMEOUT: int = 30 # in seconds
TIMEOUT_FOLLOWER_LOADING: int = 1000 # in ms

