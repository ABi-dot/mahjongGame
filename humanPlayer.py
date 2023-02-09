from utils.player import Player

class HumanPlayer(Player):
    def __init__(self, nick="bot", score: int = 25000, isViewer: bool = False, viewerPosition: str = '东',
                 screen=None, clock=None):
        super().__init__(nick=nick, score=score, isViewer=isViewer, viewerPosition=viewerPosition,
                         screen=screen, clock=clock)
