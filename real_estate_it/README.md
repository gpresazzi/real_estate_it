### Description
Simple python package intended to be used as automated way to scrape real estate website and extract homogeneous dataset.
This currently support _immobiliare.it_, but the intent is to extend it to support _idealista.it_

### Requirements
- Python39

```
python3 -m venv venv && source venv/bin/activate && pip3 install -r requirements.txt
```

### Run
```bash
python3 setup.py install
./real_estate_it
```

### Instructions
The intent of this package is to be reusable
```python
    searcher = ImmobiliareSearch(zona="farini", min_area=60, max_area=150, min_price=200000, max_price=600000)
    imm_scraper = Immobiliare(searcher)
    houses = imm_scraper.get_all_houses()
```

### Next steps

- Extend the hous fields (number of rooms, bathrooms etc.)
- Parse the house geolocation
- Add support idealista.it

**Disclaimer**
some of the parsing logic has been extracted form: https://github.com/Stemanz/immobiscraper