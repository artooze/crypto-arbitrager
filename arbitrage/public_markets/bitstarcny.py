from ._bitstar import Bitstar

class BitstarCNY(Bitstar):
    def __init__(self):
        super().__init__("CNY", "swap-btc-cny")
