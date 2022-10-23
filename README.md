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

Example For Instagram: `SITE: str = "instagram.com"`
