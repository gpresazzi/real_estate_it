import os
import logging

from real_estate_it.scraper.immobiliare import Immobiliare
from real_estate_it.model.search import Search

log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)


def main():
    google_key = os.environ.get('GOOGLEMAPS_KEY')

    searcher = Search(city="milano",
                      zona="farini",
                      min_area=60, max_area=150, min_price=200000, max_price=600000)
    imm_scraper = Immobiliare(searcher, enrich_geolocation=False, google_maps_key=google_key)
    houses = imm_scraper.get_all_houses(20)

    for house in houses:
        logger.info(house)
