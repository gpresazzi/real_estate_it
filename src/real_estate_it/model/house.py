from dataclasses import dataclass


@dataclass
class House:
    cost: float
    price_per_area: float
    floor: int
    area: str
    ultimo: bool
    url: str
    energy: str
    car_spot: str
    address: str
    lat: float
    lng: float

    def __repr__(self):
        return f"Url: {self.url} | address: {self.address} | cost: {self.cost} | floor: {self.floor} | " \
               f"last floor: {self.ultimo} | energy: {self.energy} | area: {self.area} | car_spot: {self.car_spot} " \
               f"| lat: {self.lat} | long: {self.lng} "
