class OutOfTilesError(Exception):
    def __init__(self, message='out of tiles', *args):
        self.args = args
        self.message = message


class HaveWinnerError(Exception):
    def __init__(self, winner=None, *args):
        self.args = args
        self.winner = winner