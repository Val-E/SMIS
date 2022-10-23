import re
import json
import pandas as pd
import numpy as np

from selenium import webdriver

from settings import ENCODING, FEMALE_NAMES_WORDLISTS, MALE_NAMES_WORDLISTS, \
    AGE_INDICATORS_WORDLISTS, PRONOUNS_DICTIONARIES, CITY_DICTIONARIES, \
    POLITICAL_DICTIONARIES, COUNTRY_SYMBOLS_DICTIONARIES


# create driver
PATH: str = "chromedriver-bin"
driver = webdriver.Chrome(PATH)


# regex pattern to find the sexual orientation of users
SEXUAL_ORIENTATION_PATTERN: str = r"[a-z]+sexual"


"""merge word lists together"""
# sets with male and female names used for sex sex recognition
# expected format: .txt;  words separated by newline
FEMALE_NAMES: set = {}
MALE_NAMES: set = {}

for wordlist_path in FEMALE_NAMES_WORDLISTS:
    with open(wordlist_path, "r") as wordlist:
        FEMALE_NAMES = set(FEMALE_NAMES) | set(wordlist.read().lower().split())

for wordlist_path in MALE_NAMES_WORDLISTS:
    with open(wordlist_path, "r") as wordlist:
        MALE_NAMES = set(MALE_NAMES) | set(wordlist.read().lower().split())

# lists with phrases, which indicate age
# expected format: .txt;  words separated by newline
AGE_INDICATOR_PATTERN: np.array = np.array([])
AGE_INDICATOR_PATTERN_SIZE: np.array = np.array([], dtype=int)

phrases: np.array = np.array([])
for wordlist_path in AGE_INDICATORS_WORDLISTS:
    with open(wordlist_path, "r") as wordlist:
        phrases = np.concatenate((phrases, wordlist.read().lower().split()))

for phrase in set(phrases):
    AGE_INDICATOR_PATTERN = np.concatenate((AGE_INDICATOR_PATTERN, [re.compile(r"\d+[^\\s]" + phrase)]))
    AGE_INDICATOR_PATTERN_SIZE = np.concatenate((AGE_INDICATOR_PATTERN_SIZE, [len(phrase)]))


# dictionary with pronouns
# expected format: JSON; {"pronoun": "sex"}
PRONOUNS_DICTIONARY: dict = {}
for dictionary_path in PRONOUNS_DICTIONARIES:
    with open(dictionary_path, "r") as dictionary:
        PRONOUNS_DICTIONARY.update(json.loads(dictionary.read().lower()))

PRONOUNS_DICTIONARY_KEYS: set = set(PRONOUNS_DICTIONARY.keys()) 


# dictionary with political symbols
# expected format: JSON; {"symbol": "group/meaning/party"}
POLITICAL_DICTIONARY: dict = {}
for dictionary_path in POLITICAL_DICTIONARIES:
    with open(dictionary_path, "r") as dictionary:
        POLITICAL_DICTIONARY.update(json.loads(dictionary.read().lower()))

POLITICAL_DICTIONARY_KEYS: set = set(POLITICAL_DICTIONARY.keys())


# dictionary with country symbols
# expected format: JSON; {"symbol": "nation"}
NATION_SYMBOLS_DICTIONARY: dict = {}
for dictionary_path in COUNTRY_SYMBOLS_DICTIONARIES:
    with open(dictionary_path, "r") as dictionary:
        NATION_SYMBOLS_DICTIONARY.update(json.loads(dictionary.read().lower()))

NATION_SYMBOLS_DICTIONARY_KEYS: set = set(NATION_SYMBOLS_DICTIONARY.keys())
NATIONS: set = set(NATION_SYMBOLS_DICTIONARY.values())


# list with cities
# expected format: .csv; comma separated; name, country, subcountry
CITY_LIST: list = np.array([["", "", ""]])
for dictionary_path in CITY_DICTIONARIES:
    CITY_LIST = np.concatenate((
        CITY_LIST, 
        pd.read_csv(dictionary_path, encoding=ENCODING, dtype=str).to_numpy()
    ))
CITY_LIST = np.delete(CITY_LIST, 0, axis=0)

