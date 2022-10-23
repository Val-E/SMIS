# SMIS - Social Media Intelligence Software



## Description 

The following software was developed with the aim to evaluated filter bubbles and connections between different social and political groups.
Currently, the scraper only works on Instagram.



## Installation

### Requirements 

The software was written and tested with Python3.9.

The software uses Chromium Webdriver. Make sure to install it on your system. [Link](https://chromedriver.chromium.org/)

Further, the software requires the libraries in the requirements.txt. Install them with
`python -m pip install -r requirements.txt --user`.

## Configuration 

You need to configure the software before using it.

In order to do that, open settings.py.

There you have to enter which site you want to use the scraper. 

### Login Configuration
Example For Instagram: `SITE: str = "instagram.com"`

Then you have to tell the software your username and password for the platform you have entered. You should also select option for technical cookies by the Text. The default text selects only necessary technical cookies for instagram.

### Target Configuration 
All targets are safed in a set of 2-tuples. The tuple contains the user handler of the target user and the depth.
The depth specifies how many levels the program has to run down recursively. **DO NOT PUT THE VALUE TOO HIGH**, especially if you know the users in the bubble follow a lot of people, because the number grows exponentially. 

Example: `ROOT_PROFILES: str = {('first_target', 1), ('second_target', 2), ('last_target', 0)}`

If you wanne avoid to evalute data from some accounts put their user handle into the blacklist.

# Usage 
After the installation and configuration is finished, you can start the scraper with `python scraper.py`. 
 
