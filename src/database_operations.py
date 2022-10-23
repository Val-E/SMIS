import re 

from database.models import User, Following, session

from src.tools import search_for_pronouns, sex_recognition, age_recognition, \
    sexual_classification,  political_classification, search_for_nationalities, \
    search_for_cities


async def create_user_entry(user_handle: str, username: str, profile: str, biography: str) -> None:
    """Format and filter text for information and write it into the database"""
    age: int = age_recognition(profile)

    # search for pronouns, before searching for name
    sex: str = search_for_pronouns(profile)
    if not sex:
        # search name in username, then in user handle
        sex = sex_recognition(username)
        if not sex:
            sex = sex_recognition(user_handle)


    # search for location
    nationalities: str = search_for_nationalities(profile)
    cities: str = search_for_cities(profile)

    # search for futher information
    sexual_orientations: str = sexual_classification(profile)
    political_classifications: str = political_classification(profile)

    user: User = User(
        user_handle = user_handle,
        username = username,
        biography = biography,
        age = age,
        sex = sex,
        cities = cities,
        nationalities = nationalities,
        sexual_orientations = sexual_orientations,
        political_classifications = political_classifications
    )
    session.add(user)
    session.commit()
    session.close()


async def create_following_relation(following_user_handle: str, followed_users: set) -> None:
    """create relationship between following user and followed users"""
    for followed_user_handle in followed_users:
        relationship: Following = Following(
            following_user = following_user_handle, 
            followed_user = followed_user_handle
        )
        session.add(relationship)

    session.commit()
    session.close()

