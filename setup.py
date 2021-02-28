import sys
from pkg_resources import VersionConflict, require
from setuptools import setup, find_packages

try:
    require("setuptools>=38.3")
except VersionConflict:
    print("Error: version of setuptools is too old (<38.3)!")
    sys.exit(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="real_estate_it",
    version="0.0.1",
    author="Giulio Presazzi",
    author_email="gpresazzi@gmail.com",
    description="Simple real estate scraper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(where='src'),  # Required
    package_dir={'': 'src'},  # Optional
    python_requires='>=3.8',
    entry_points={  # Optional
        'console_scripts': [
            'real_estate_it = real_estate_it.main:main',
        ],
    }
)
