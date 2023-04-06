#!/usr/bin/env python3

# See:
# - https://www.programiz.com/python-programming/docstrings
# - https://blog.codacy.com/3-popular-python-style-guides/
# - https://docs.python-guide.org/writing/structure/
# - https://teclado.com/30-days-of-python/python-30-day-21-multiple-files/
# - https://snarky.ca/why-you-should-use-python-m-pip/

"""
This script generates PNG barcode images.

Usage : python barcode.py 1234 --type=upc --verbose
Lint  : pylint barcode.py && mypy barcode.py
"""

__version__ = "1.0.0"
__author__ = "rmkane"
__copyright__ = "Copyright 2023, rmkane"
__credits__ = ["rmkane"]
__license__ = "MIT"
__maintainer__ = "rmkane"
__email__ = "rmkane89@gmail.com"
__status__ = "Development"

from argparse import ArgumentParser, Namespace
from typing import Any, TypeVar
import os
import pathlib
import re
import matplotlib.pyplot as plt # type: ignore
import numpy as np

EXPORT_DIR = "export"

def add(one: int, two: int) -> bool:
    '''
    Add two numbers
    '''
    return one > two

foo: bool = add(1, 2)

def str_to_digits(value: str) -> list[int]:
    '''
    Converts a string of digits to a list of integers.

    Parameters
    ----------
        value : str
            A sequence of digits

    Returns
    -------
        list[int]
            The digits as integers
    '''
    return [int(digit) for digit in list(value)]

class Barcode:
    """
    A class that represents a barcode.

    Attributes
    ----------
        data : str
            data to encode
        options : dict[str, Any]
            barcode options
        name : str
            barcode name
    """

    def __init__(self, data: str, options: dict[str, Any], name: str):
        self._data = data
        self._options = options
        self._name = name

    @property
    def data(self) -> str:
        """
        The barcode data.

        Returns
        -------
            str
                The barcode data
        """
        return self._data

    @property
    def options(self) -> dict[str, Any]:
        """
        The barcode options.

        Returns
        -------
            dict[str, Any]
                The barcode options.
        """
        return self._options

    @property
    def name(self) -> str:
        """
        The barcode name.

        Returns
        -------
            str
                The barcode name.
        """
        return self._name

    @property
    def text(self) -> str:
        """
        The barcode text.

        Returns
        -------
            str
                The barcode text.
        """
        return self.options.get('text', self.data) # .replace(/[A-D]/g, '')

    def encode(self) -> str:
        '''
        Encodes the data into an array of binary digits.

        Returns
        -------
            str
                The encoded data
        '''
        return ""

# See:
# - https://lindell.me/JsBarcode/
# - https://github.com/lindell/JsBarcode/tree/master/src/barcodes

CODABAR_DICT = {
    '0': "101010011",
    '1': "101011001",
    '2': "101001011",
    '3': "110010101",
    '4': "101101001",
    '5': "110101001",
    '6': "100101011",
    '7': "100101101",
    '8': "100110101",
    '9': "110100101",
    '-': "101001101",
    '$': "101100101",
    ':': "1101011011",
    '/': "1101101011",
    '.': "1101101101",
    '+': "1011011011",
    'A': "1011001001",
    'B': "1001001011",
    'C': "1010010011",
    'D': "1010011001"
}

# See:
# - https://en.wikipedia.org/wiki/Codabar
# - https://www.dcode.fr/barcode-codabar
# - https://github.com/lindell/JsBarcode/blob/master/src/barcodes/codabar/index.js
class Codabar(Barcode):
    """
    A class that represents a Codabar barcode.

    ...

    Attributes
    ----------
        data : str
            data to encode
        options : dict[str, Any]
            barcode options

    Methods
    -------
        is_valid(data):
            Determines if the data is valid
        encode():
            Encodes the data into an array of binary digits.
    """

    def __init__(self, data: str, options: dict[str, Any]):
        if not self.is_valid(data):
            raise ValueError(f"Not a valid codabar value: {data}")
        super().__init__(f"A{data}A".upper(), options, 'codabar')

    def is_valid(self, data: str) -> bool:
        '''
        Determines if the data is valid.

        Parameters
        ----------
            data : str
                Barcode data

        Returns
        -------
            boolean
                The encoded data
        '''
        return re.search(r'^[0-9\-\$\:\.\+\/]+$', data) is not None

    # @override
    @property
    def text(self) -> str:
        """
        The barcode text.

        Returns
        -------
            str
                The barcode text.
        """
        return self.options.get('text', re.sub(r"[A-D]", "", self.data))

    # @override
    def encode(self) -> str:
        '''
        Encodes the data into an array of binary digits.

        Returns
        -------
            str
                The encoded data
        '''
        return '0'.join([CODABAR_DICT[token] for token in self.data])

# See:
# - https://en.wikipedia.org/wiki/Universal_Product_Code
# - https://github.com/lindell/JsBarcode/blob/master/src/barcodes/EAN_UPC/UPC.js
class Upc(Barcode):
    """
    A class that represents a UPC barcode.

    ...

    Attributes
    ----------
        data : str
            data to encode
        options : dict[str, Any]
            barcode options

    Methods
    -------
        is_valid(data):
            Determines if the data is valid
        encode():
            Encodes the data into an array of binary digits.
    """

    def __init__(self, data: str, options: dict[str, Any]):
        if not self.is_valid(data):
            raise ValueError(f"Not a valid UPC value: {data}")
        super().__init__(data, options, 'codabar')

    def is_valid(self, data: str) -> bool:
        '''
        Determines if the data is valid.

        Parameters
        ----------
            data : str
                Barcode data

        Returns
        -------
            boolean
                The encoded data
        '''
        return re.search(r'^[0-9]{11,12}$', data) is not None

    # @override
    def encode(self) -> str:
        '''
        Encodes the data into an array of binary digits.

        Returns
        -------
            str
                The encoded data
        '''
        return "" # implement

U = TypeVar('U', bound=Barcode)

# See: https://matplotlib.org/stable/gallery/images_contours_and_fields/barcode_demo.html
def create_barcode(barcode: U, filename: str, dpi: int) -> list[int]:
    '''
    Returns the encoded barcode data and saves an image.

    Parameters
    ----------
        barcode : Barcode
            An instance of a Barcode
        filename : str
            Filename of image
        dpi : int
            DPI or dots per inch

    Returns
    -------
        encoded : list[int]
            The encoded data
    '''
    encoded = str_to_digits(barcode.encode())
    pixel_per_bar = 4
    fig = plt.figure(figsize=(len(encoded) * pixel_per_bar / dpi, 2), dpi=dpi)
    ax = fig.add_axes([0.1, 0.25, 0.8, 0.5])  # span the whole figure
    plt.xticks([])
    plt.yticks([])
    ax.spines[['top', 'right', 'bottom', 'left']].set_visible(False)
    ax.set_xlabel(barcode.text, fontsize='large', fontweight='bold')
    ax.imshow(np.array(encoded).reshape(1, -1),
                cmap='binary',
                aspect='auto',
                interpolation='nearest')
    export_path = filename or os.path.join(EXPORT_DIR, f"{barcode.name}-{barcode.data}.png")
    pathlib.Path(EXPORT_DIR).mkdir(parents=True, exist_ok=True)
    plt.savefig(export_path)
    print(f"Successfully created barcode: {export_path}")
    return encoded

def main(args: Namespace) -> None:
    '''
    Main entry point.

    Parameters
    ----------
        args : Namespace
            Parsed arguments from ArgumentParser
    '''
    if args.verbose:
        print(f"Generating a {args.type} barcode from the value: {args.value}")
    create_barcode(Codabar(args.value, {}), args.filename, args.dpi)

def parse_arguments() -> Namespace:
    '''
    Returns parsed arguments using ArgumentParser.

    Returns
    -------
        Namespace
            Parsed arguments
    '''
    parser = ArgumentParser(prog='Barcode Generator',
                            description='Generates Barcodes',
                            epilog='<EOL>')
    parser.add_argument('value')
    parser.add_argument('-d', '--dpi', default=100)
    parser.add_argument('-f', '--filename')
    parser.add_argument('-t', '--type', choices=['codabar', 'ean', 'upc'], default='codabar')
    parser.add_argument('-v', '--verbose', action='store_true')

    return parser.parse_args()

if __name__ == '__main__':
    main(parse_arguments())
