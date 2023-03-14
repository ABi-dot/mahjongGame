import copy
import pickle
from utils.player import Player

class Saving:
    def __init__(self, filename):
        self.filename = filename
        self.data = dict()
        self.info = dict()
        self.seq = list()

    def load_data(self):
        with open(self.filename, 'rb') as f:
            self.data = pickle.load(f)
        return self.data

    def save_info(self, players: list = None, prevailingWind: str = '东',
                 number = 1, viewer=None):
        self.info['players'] = list()
        for player in players:
            self.info['players'].append(self.save_player_info_data(player))
        self.info['prevailingWind'] = prevailingWind
        self.info['number'] = number
        #self.info['viewer'] = self.save_player_info_data(viewer)
        self.data['info'] = self.info

        #output = open(self.filename, 'wb')
        #pickle.dump(self.data, output)

    def save_player_info_data(self, player: Player):
        a = dict()
        a['nick'] = player.nick
        a['score'] = player.score
        a['isviewer'] = player.isViewer
        a['viewerposition'] = player.viewerPosition
        return a

    def save_player_play_data(self, player: Player):
        a = dict()
        a['nick'] = player.nick
        a['concealed'] = player.concealed[:]
        a['exposed'] = player.exposed[:]
        a['discarded'] = player.discarded[:]
        a['desk'] = player.desk[:]
        a['discarding'] = player.discarding
        a['position'] = player.position
        return a

    def add_status(self, players, mjSet):
        stat = dict()
        stat['players'] = list()
        stat['mjSet'] = copy.deepcopy(mjSet)
        for player in players:
            stat['players'].append(self.save_player_play_data(player))
        self.seq.append(stat)


    def save_status(self):
        self.data['seq'] = self.seq

    def save(self):
        with open(self.filename, 'wb') as output:
            pickle.dump(self.data, output)
