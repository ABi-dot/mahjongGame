from utils.mjSet import MjSet
from utils.suit import Suit
from transitions import Machine
from utils.mjSet import MjSet
from utils.mjMath import MjMath
from utils.player import Player
from utils.aiPlayer import AIPlayer
from utils.rule import Rule
import itertools

class HandStateMachine(object):
    pass

class Hand(object):
    def __init__(self, players: list = None, prevailingWind: str = '东'):
        if not players:
            raise ValueError("Need players!")
        self._mjSet = MjSet()
        self._players = players
        self.out_of_tiles = False
        self._positions = dict()
        for idx, player in enumerate(self._players):
            wind = Suit.getWindByIndex(idx)
            player.position = wind
            self._positions[wind] = player
        self._dealer: Player = self._players[0]
        self._prevailingWind = prevailingWind


        self._winner = None
        self.firer = None
        self.robbing_a_kong = False
        self.mahjong_on_kong = False

        self._stateMachine = HandStateMachine()
        self._states = ["begin", "prepared", "playing", "scoring", "end"]
        self._transitions = [
            {'trigger': 'prepare', 'source': 'begin', 'dest': 'prepared'},  # 准备
            {'trigger': 'deal', 'source': 'prepared', 'dest': 'playing'},  # 拿四张
            {'trigger': 'mahjong', 'source': 'playing', 'dest': 'scoring'},  # 胡牌
            {'trigger': 'withdraw', 'source': 'playing', 'dest': 'scoring'},  # 流局
            {'trigger': 'score', 'source': 'scoring', 'dest': 'end'},  # 算分
        ]
        Machine(model=self._stateMachine, states=self._states, transitions=self._transitions, initial="begin")

    def __str__(self):
        return '\r\n'.join([f'{x.position}:{x}' for x in self._players])

    def _resetPlayers(self):
        for player in self.players:
            player.reset()

    @property
    def positions(self):
        return self._positions

    @property
    def mjSet(self):
        return self._mjSet

    @property
    def winner(self):
        return self._winner

    @property
    def players(self):
        return self._players

    @property
    def leftTiles(self):
        return self._leftTiles

    @leftTiles.setter
    def leftTiles(self, value):
        self.leftTiles = value

    def _get_next_player(self, current):
        ok = False
        for player in itertools.cycle(self.players):
            if ok:
                return player
            if player == current:
                ok = True

    def prepare(self):
        self._resetPlayers()
        self._stateMachine.prepare()
        self._shuffle()

    def deal(self):
        for _ in range(max(MjMath.concealed_count) // 4):
            for player in self.players:
                player.drawstack(self.mjSet)
        for player in self.players:
            player.draw(self.mjSet)
            player.sortconcealed()

        self._stateMachine.deal()

    def play(self):
        current = self._dealer
        before = None
        currentDiscard = None

        haveWinner = False
        while not haveWinner:
            if currentDiscard:
                wind = current.position
                player = current
                for idx in range(3):
                    test = player.concealed[:]
                    test.append(currentDiscard)
                    if Rule.is_rong(test):
                        player.concealed.append(currentDiscard)
                        print(f"winner is {player}, by {before}")
                        self._winner = player
                        self._stateMachine.mahjong()
                        haveWinner = True
                        break
                    wind = Suit.getNextWind(wind)
                    player = self.positions[wind]
            if haveWinner:
                break

            # interrupted by exposed kong / pong / chow
            interrupted = False
            if currentDiscard:
                player = None
                # try kong ( must have tiles ):
                if self.mjSet.get_left_tiles_cnt():
                    wind = current.position
                    player = current
                    for idx in range(3):
                        if player.try_exposed_kong(tile=currentDiscard, owner=before, mjSet=self.mjSet):
                            interrupted = True
                            break
                        wind = Suit.getNextWind(wind)
                        player = self.positions[wind]

                # try pong:
                if not interrupted:
                    wind = current.position
                    player = current
                    for idx in range(3):
                        if player.try_exposed_pong(tile=currentDiscard, owner=before):
                            interrupted = True
                            break
                        wind = Suit.getNextWind(wind)
                        player = self.positions[wind]

                #try chow
                if not interrupted:
                    wind = current.position
                    player = current
                    if player.try_exposed_chow(tile=currentDiscard, owner=before):
                        interrupted = True

                if not interrupted:
                    before.put_on_desk(currentDiscard)
            #end if currentDiscard

            if interrupted:
                current = player
            else:
                if self.mjSet.get_left_tiles_cnt() == 0:
                    print("out of tiles!!!")
                    self._winner = None
                    self._stateMachine.withdraw()
                    break

                # draw
                current.draw(self.mjSet)
                #test by hu
                if Rule.is_rong(current.concealed):
                    print(f"winner is {current}, by self!")
                    self._winner = current
                    self._stateMachine.mahjong()
                    break

                # self kong
                current.try_conceal_kong(mjSet=self.mjSet)

            tile = current.decide_discard()
            print(current, 'discard', tile)
            current.discard(tile)
            current.sortconcealed()
            currentDiscard = tile

            #next player
            nextPlayer = self._get_next_player(current)
            before = current
            current = nextPlayer
        #end while

        print("tiles left :", self.mjSet.get_left_tiles_cnt())
        for player in self.players:
            if player == self.winner:
                print(f"winner {player}: ", Rule.convert_tiles_to_str(player.concealed))
            else:
                print(f"{player}: ", Rule.convert_tiles_to_str(player.concealed))



    def _shuffle(self):
        self._mjSet.shuffle()

    def score(self):
        # score the play result
        self._stateMachine.score()
        pass

def test_play_once():
    players = [
        AIPlayer('Eric'),
        AIPlayer('Nana'),
        AIPlayer('Sister'),
        AIPlayer('Brother'),
    ]
    prevailing_wind = '东'
    hand = Hand(players=players, prevailingWind=prevailing_wind)
    hand.prepare()
    hand.deal()
    hand.play()
    print(hand.winner)
    hand.score()
    return hand.winner

def main():
    test_play_once()

if __name__ == '__main__':
    main()