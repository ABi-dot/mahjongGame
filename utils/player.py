class Player(object):
    def __init__(self, nick="bot", score: int = 25000, isViewer: bool = False, viewerPosition: str = '东',
                 screen=None, clock=None):
        self._nick = nick
        self._concealed = []
        self._meld = []
        self._discarded = []
        self._position = ''

        self._score = score
        self._isViewer = isViewer
        self.viewerPosition = viewerPosition
        self._screen = screen
        self._clock = clock
        self.currentTiles = []

    @property
    def position(self):
        return self._position
