import os
import requests
# helpers dependencies
import string
import random

# scraper dependencies
from bs4 import BeautifulSoup

# Own directory
from helpers import Helpers
from config import get_keys
from scraper import ScheduleScraper

settings = get_keys(os)

helpers_dependencies = dict(random=random, string=string)
helpers = Helpers(settings, **helpers_dependencies)

scraper_dependencies = {"get": requests.get, "BeautifulSoup": BeautifulSoup}
scraper = ScheduleScraper(**scraper_dependencies)

if __name__ == '__main__':
    class_list = scraper.get_courses_by_major("GEN", "DSSP")
    scraper.add_grades_to_classes(class_list)
    class_list = sorted(class_list, key=lambda x: x.get("Grades").get("Average"), reverse=True)
    print(class_list)
