import re
import time
import requests
import logging
import googlemaps

from io import BytesIO
from bs4 import BeautifulSoup
from typing import List, Tuple
from real_estate_it.model.search import Search
from real_estate_it.model.house import House

logger = logging.getLogger(__name__)


class Immobiliare:

    def __init__(self,
                 search: Search,
                 enable_multipages: bool = True,
                 max_pages: int = 100,
                 enrich_geolocation: bool = True,
                 google_maps_key: str = None):
        """
        Get all the the houses that match the search conditions
        """

        self.search_data = search
        self.urls_ = None
        self.verbose = True
        self.url = self.search_data.get_url_immobiliare()
        self.wait = 0.001  # waiting time in seconds
        self.max_pages = max_pages
        self.enable_multipages = enable_multipages
        self.min_acceptable_price = 1000  # houses less than 1k will probably have wrong price
        self.enrich_geolocation = enrich_geolocation
        self.maps_key = google_maps_key

        if self.enrich_geolocation:
            logger.info(f"Requiring geolocalitaion. Using Google key: {self.maps_key}")
        else:
            logger.info(f"Skipping geolocalization enrichment")

    def get_all_houses(self, limit: None) -> List:
        """
        Get all the info for each of the parsed houses
        :return: list of houses
        """
        if not self.urls_:
            self.urls_ = self.get_all_urls(limit)

        all_results = []
        for url in self.urls_:
            try:
                logger.info(f"Getting data  from '{url}'")
                all_results.append(self._get_data(url))

            except Exception as e:
                logger.warning(f"offending_url='%s' [%s]", url, e)

        return all_results

    def get_all_urls(self, limit: int = None) -> List[str]:
        """
        Retrieve all the houses links parsing all the pages
        :return: List of urls
        """
        urls_ = []

        # first page
        logger.info(f"Processing page 1: {self.url}")
        urls_ += self.parse_single_page(self.url, limit)

        if len(urls_) >= limit:
            return urls_

        if self.enable_multipages:
            # trying other pages
            logger.debug("Processing further pages")

            for i in range(2, self.max_pages):  # that's enough of pages
                logger.info(f"Processing page {i}")
                curr_url = self.url + f"&pag={i}"

                t = self._get_text(curr_url).lower()

                if "404 not found" in t:
                    # no more pages found
                    break

                urls_ += self.parse_single_page(curr_url)

                if len(urls_) > limit:
                    return urls_

        logger.info("All retrieved urls in attribute 'urls_'")
        logger.info(f"Found {len(urls_)} houses matching criteria.")
        return urls_

    def parse_single_page(self, curr_url: str, limit: int = None) -> List[str]:
        """
        Identify ads from single page
        :param curr_url: Url
        :param limit
        :return: List of urls
        """
        url_list = []
        pattern = re.compile(r"\d+\/$")
        page = self._get_page(curr_url)
        page.seek(0)
        soup = BeautifulSoup(page, "html.parser")

        for link in soup.find_all("a"):
            time.sleep(self.wait)
            l = link.get("href")

            if l is None:
                continue

            if "https" in l and "annunci" in l:
                if pattern.search(l):
                    url_list.append(l)

                    if limit and len(url_list) >= limit:
                        return url_list

        return url_list

    @staticmethod
    def _get_page(url):

        req = requests.get(url, allow_redirects=False)
        page = BytesIO()
        page.write(req.content)

        return page

    @staticmethod
    def _get_text(sub_url):

        req = requests.get(sub_url, allow_redirects=False)
        page = BytesIO()
        page.write(req.content)

        page.seek(0)
        soup = BeautifulSoup(page, "html.parser")

        text = soup.get_text()  # ?? OK on Mac, mayhem on Windows

        # compacting text
        t = text.replace("\n", "")
        for _ in range(50):  # that would be sufficient..
            t = t.replace("  ", " ")

        return t

    def _get_data(self, sub_url: str):
        """
        This gets data from *one* of the sub-urls
        """
        car_not_found = "n/a"
        t = self._get_text(sub_url).lower()

        address = self.parse_address(t)
        cost = self.parse_cost(t, sub_url)
        floor, ultimo = self.parse_floor(t)
        area = self.parse_area(t, sub_url)
        energy = self.parse_energetic_class(t, sub_url)
        car = self.parse_car_spot(t, sub_url)
        lat = 0
        lng = 0

        if self.enrich_geolocation:
            lat, lng = self.get_geolocation(address)

        # €/m²
        try:
            price_per_area = round(int(cost) / int(area), 1)
        except Exception:
            price_per_area = "n/a"

        # Generate result
        res = House(cost, price_per_area, floor, area, ultimo, sub_url, energy, car, address, lat, lng)

        return res

    def parse_address(self, t: str) -> str:
        # address
        address = "n/d"
        address_patterns = (
            r"((via|viale|piazza|corso|piazzale) \w+(\s\w+){1,}(.|,))",
        )

        for pattern in address_patterns:
            add_pattern = re.compile(pattern)
            address = add_pattern.search(t)

            if address is not None:
                return address.group(1)

        return address

    def parse_cost(self, t: str, sub_url: str) -> str:
        price_not_found = -1

        # price
        cost_patterns = (
            "€ (\d+\.\d+\.\d+)",  # if that's more than 1M €
            "€ (\d+\.\d+)"
        )

        for pattern in cost_patterns:
            cost_pattern = re.compile(pattern)

            try:
                cost = cost_pattern.search(t)
                cost = cost.group(1).replace(".", "")
                break

            except AttributeError:
                continue

        if cost is None:
            if "prezzo su richiesta" in t:
                logger.info(f"Price available upon request for {sub_url}")
                cost = price_not_found
            else:
                logger.info(f"Can't get price for {sub_url}")
                cost = price_not_found

        if cost is not None and cost is not price_not_found:
            # wrong house cost - price is too low
            if int(cost) < self.min_acceptable_price:
                if "prezzo su richiesta" in t:
                    logger.info(f"Price available upon request for {sub_url}")
                    cost = price_not_found
                else:
                    logger.info(f"Too low house price: {int(cost)}? for {sub_url}")
                    cost = price_not_found
        return cost

    def parse_floor(self, t: str) -> str:
        floor_patterns = (
            r"piano (\d{1,2})",
            r"(\d{1,2}) piano",
            # if ultimo piano, floor number can be left out
            r"(\d{1,2}) piani"
        )

        for pattern in floor_patterns:
            floor_pattern = re.compile(pattern)
            floor = floor_pattern.search(t)

            if floor is not None:
                floor = floor.group(1)
                break

        if "piano terra" in t:
            floor = 1

        if "ultimo" in t:
            ultimo = True
        else:
            ultimo = False

        return floor, ultimo

    def parse_area(self, t: str, sub_url: str) -> str:
        area_not_found = "n/a"

        # Square meters
        area_pattern = re.compile(r"superficie (\d{1,4}) m")

        try:
            area = area_pattern.search(t)
            area = area.group(1)
        except AttributeError:
            area = area_not_found

            if "asta" in t:
                logger.info(f"Auction house: no area info {sub_url}")
            else:
                logger.info(f"Can't get area info from url {sub_url}")
        return area

    def parse_energetic_class(self, t: str, sub_url: str) -> str:
        energy_not_found = "n/a"

        # Energetic class
        energy_patterns = (
            r"energetica (\D{1,2}) ",
            r"energetica(\S{1,2})",
        )

        for i, pattern in enumerate(energy_patterns):
            energy_pattern = re.compile(pattern)
            energy = energy_pattern.search(t)

            if energy is not None:
                energy = energy.group(1).upper()
                if self.energy_acceptable(energy):
                    break

        if energy is None or not self.energy_acceptable(energy):  # in case everything fails
            if "in attesa di certificazione" in t:
                logger.info(f"Energy efficiency still pending for {sub_url} ")
                energy = energy_not_found
            else:
                logger.info(f"Can't get energy efficiency from {sub_url}")
                energy = energy_not_found
        return energy

    def parse_car_spot(self, t: str, sub_url: str) -> str:
        car_not_found = "n/a"
        # Car spot
        car_patterns = (r"post\S auto (\d{1,2})",)

        for pattern in car_patterns:
            car_pattern = re.compile(pattern)
            car = car_pattern.search(t)

            if car is not None:
                car = car.group(1)
                break

            if car is None:
                available_upon_request = re.compile(r"possibilit\S.{0,10}auto")
                if available_upon_request.search(t) is not None:
                    logger.info(f"Car spot/box available upon request for {sub_url}")
                    car = 0
                else:
                    car = car_not_found
        return car

    def get_geolocation(self, address: str) -> Tuple[float, float]:
        lat = 0.0
        long = 0.0
        address += f" {self.search_data.city}"
        try:
            gmaps = googlemaps.Client(key=self.maps_key)

            # Geocoding an address
            geocode_result = gmaps.geocode(address)
            if isinstance(geocode_result, list):
                lat = geocode_result[0]["geometry"]["location"]["lat"]
                long = geocode_result[0]["geometry"]["location"]["lng"]
        except Exception as ex:
            logger.warning(f"unable to get location from {address}. [Exception: {ex}]")

        return lat, long

    def energy_acceptable(self, stringlike):

        if not stringlike.startswith(("A", "B", "C", "D", "E", "F", "G")):
            return False
        else:
            if len(stringlike) == 1:
                return True
            else:
                if not stringlike.endswith(
                        ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+")
                ):
                    return False
                else:
                    return True
