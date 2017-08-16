from ._btccpro import BtccPro

class BtccProCNY(BtccPro):
    def __init__(self):
        super().__init__("CNY")
