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
    posto_auto: str

    def __repr__(self):
        return f"Url: {self.url} | cost: {self.cost} | floor: {self.floor} | ultimo: {self.ultimo} | energy: {self.energy} | area: {self.area} | posto_auto: {self.posto_auto}"
