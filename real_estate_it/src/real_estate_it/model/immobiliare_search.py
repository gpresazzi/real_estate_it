from dataclasses import dataclass


@dataclass
class ImmobiliareSearch:
    zona: str
    min_price: int = None
    max_price: int = None
    min_area: int = None
    max_area: int = None

    def get_url(self):
        url = f"https://www.immobiliare.it/vendita-case/milano/{self.zona}/?criterio=rilevanza"

        if self.min_price:
            url += f"&prezzoMinimo={self.min_price}"
        if self.min_price:
            url += f"&prezzoMassimo={self.max_price}"
        if self.min_area:
            url += f"&superficieMinima={self.min_area}"
        if self.max_area:
            url += f"&superficieMassima={self.max_area}"

        return url
