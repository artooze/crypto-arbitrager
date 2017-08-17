# Copyright (C) 2017, Philsong <songbohr@gmail.com>

from ._bittrex import Bittrex

class Bittrex_BCH_BTC(Bittrex):
    def __init__(self):
        super().__init__("BTC", "BCH", "BTC-BCC")

