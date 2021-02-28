import logging

from real_estate_it.scraper.immobiliare import Immobiliare
from real_estate_it.model.immobiliare_search import ImmobiliareSearch

log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)


def main():
    searcher = ImmobiliareSearch(zona="farini", min_area=60, max_area=150, min_price=200000, max_price=600000)
    imm_scraper = Immobiliare(searcher)
    houses = imm_scraper.get_all_houses()

    for house in houses:
        logger.info(house)
