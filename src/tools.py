import re

from functools import lru_cache

from src import FEMALE_NAMES, MALE_NAMES, AGE_INDICATOR_PATTERN, \
    AGE_INDICATOR_PATTERN_SIZE, PRONOUNS_DICTIONARY, PRONOUNS_DICTIONARY_KEYS, \
    SEXUAL_ORIENTATION_PATTERN, POLITICAL_DICTIONARY, POLITICAL_DICTIONARY_KEYS, \
    NATIONS, NATION_SYMBOLS_DICTIONARY, NATION_SYMBOLS_DICTIONARY_KEYS, CITY_LIST


# search for keywords based on text
def search(text: str, keywords: set, dictionary: dict) -> set:
    classifications: set = {}
    for keyword in keywords:
        if keyword in text:
            classifications = set(classifications) | set({dictionary[keyword]})

    return classifications
    

# detect sex of user based on pronouns in profile
@lru_cache
def search_for_pronouns(profile: str) -> str:
    sex: set = search(profile, PRONOUNS_DICTIONARY_KEYS, PRONOUNS_DICTIONARY)

    # check if information are injective
    if len(sex) == 1:
        return str(*sex)
    else:
        return None


# detect sex of user based on username
@lru_cache
def sex_recognition(username) -> str:
    """username: set or str"""
    male: bool = False
    female: bool = False

    for name in MALE_NAMES:
        if name in username:
            male = True
            break
    
    for name in FEMALE_NAMES:
        if name in username:
            female = True
            break

    if female and male:
        return None
    elif male:
        return "male"
    elif female:
        return "female"
    else:
        return None


# detect age of user based on keywords in biography
INTEGER_PATTERN = re.compile(r"\d\d")
@lru_cache
def age_recognition(profile: str) -> int:
    # look for any integers in profile
    search: set = set(re.findall(INTEGER_PATTERN, profile))
    if len(search) == 0:
        # Return None if age is unkown
        return None
    elif len(search) == 1:
        return int(*search)

    # if multiple integers, were found use pattern to find the correct number
    for pattern, pattern_size in zip(AGE_INDICATOR_PATTERN, AGE_INDICATOR_PATTERN_SIZE):
        search = re.search(pattern, profile)
        if search:
            age_string = search.group()
            return int(age_string[:len(age_string) - pattern_size])

    return None


# detect sexual orientation based on biography
@lru_cache
def sexual_classification(profile: str) -> str:
    sexual_orientation: set = set(re.findall(SEXUAL_ORIENTATION_PATTERN, profile))
    if sexual_orientation:
        return "; ".join(sexual_orientation)
    return None


# detect political ideology/party membership/political group based on profile
@lru_cache
def political_classification(profile: str) -> str:
    classifications: set = search(
        profile, 
        POLITICAL_DICTIONARY_KEYS, 
        POLITICAL_DICTIONARY
    )

    if classifications:
        return "; ".join(classifications)
    return None
    
    
# detect nationality based on keywords and symbols in profile
@lru_cache
def search_for_nationalities(profile: str) -> str:
    # search for nation symbols
    nationalities: set = set(search(
        profile, 
        NATION_SYMBOLS_DICTIONARY_KEYS, 
        NATION_SYMBOLS_DICTIONARY
    ))

    # search for country name
    for nation_name in NATIONS:
        if nation_name in profile.split():
            nationalities = nationalities | {nation_name}

    if nationalities:
        return "; ".join(nationalities)
    return None


# detect city based on profile
@lru_cache
def search_for_cities(profile: str) -> str:
    cities: set = {}
    for region in CITY_LIST:
        if region[0].lower() in profile.split():
            cities = set(cities) | {(region[0], region[1], region[2])}

    if cities:
        city_list: str = ""
        for city in cities:
            city_list += f"{str(city)}; "

        return city_list[:-2]

    return None
