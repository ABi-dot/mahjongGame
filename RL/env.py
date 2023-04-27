from setting import Setting
from utils.tile import Tile
from utils.aiPlayer import AIPlayer
from RL.agent import AgentPlayer
from random import shuffle
from utils.suit import Suit
from utils.hand import Hand
from utils.rule import Rule
import numpy as np
import os
import matplotlib.pyplot as plt
import collections
import torch


# 万0-8 筒9-17 条 18-26 白发中27-29 东南西北30-33
class Env(object):
    def __init__(self, agent, args):
        self.opposites = Setting.gameOpposites[0:3]
        self.args = args
        self.player = AgentPlayer(score=0, isViewer=True, env=self, agent=agent, args=args)
        self.players = []
        self.hand = None
        #self.state = np.zeros((34, 4), dtype=int)
        self.card_encoding_dict = {}
        self._init_card_encoding()
        self.action_id = self.card_encoding_dict
        self.de_action_id = {self.action_id[key]: key for key in self.action_id.keys()}
        self.prepare()
        self.agent = agent
        self.totalvalue = 0
        self.values = []
        self.avgvalues = []
        self.winrate = []
        self.maxavgvalues = float("-inf")
        self.win = 0
        self.lose = 0
        self.p = 10000


    def _init_card_encoding(self):
        for i in range(101, 110):
            self.card_encoding_dict[i] = i - 101
        for i in range(201, 210):
            self.card_encoding_dict[i] = i - 192
        for i in range(301, 310):
            self.card_encoding_dict[i] = i - 283
        for i in range(410, 435, 10):
            self.card_encoding_dict[i] = (i // 10) % 10 + 26
        for i in range(510, 545, 10):
            self.card_encoding_dict[i] = (i // 10) % 10 + 29
        self.card_encoding_dict['pong'] = 34
        self.card_encoding_dict['chow'] = 35
        self.card_encoding_dict['kong'] = 36
        self.card_encoding_dict['riichi'] = 37
        self.card_encoding_dict['stand'] = 38


    def prepare(self):
        self.players.append(self.player)
        for name in self.opposites:
            ai = AIPlayer(nick=name, score=0)
            self.players.append(ai)



    #排座
    def circle(self):
        shuffle(self.players)
        self.hand = Hand(players=self.players)
        self.hand.prepare()
        self.hand.deal()

    def play_game(self):
        while self.player.step < self.args.max_steps:
            self.circle()
            self.hand.play()
            done = True
            reward = 0
            self.player.next_state = self.generate_status()
            if self.hand.winner == self.player:
                reward = 200
                self.win += 1
            elif self.hand.firer == self.player:
                reward = -30
                self.lose += 1
            elif self.hand.winner != None:
                reward = -20
                self.lose += 1
            if self.win + self.lose > 0:
                self.winrate.append(self.win / (self.win + self.lose))
            self.player.episode_reward += reward
            self.player.episode_length += 1
            if self.player.state is not None and self.player.next_state is not None:
                self.player.replay_buffer.push(self.player.state[:], self.player.action, reward, done, self.player.next_state[:])

            if done is True:
                self.player.log_ep_rewards.append(self.player.episode_reward)
                self.player.log_ep_length.append(self.player.episode_length)
                self.values.append(self.player.episode_reward)
                self.totalvalue += self.player.episode_reward
                if len(self.values) > 100:
                    a = self.values[0]
                    self.values.pop(0)
                    self.totalvalue -= a
                avg = self.totalvalue / len(self.values)
                self.avgvalues.append(avg)

                if self.win + self.lose > 0:
                    print(
                        f"i={self.player.step}, reward={self.player.episode_reward:.0f}, avg_reward={avg:.2f}, length={self.player.episode_length},"
                        f" loss={self.player.log_losses[-1]:.1e}, epsilon={self.player.epsilon:.3f}, win_rate={self.win / (self.win + self.lose) :.4f}")

                # 如果得分更高，保存模型。
                if avg > self.maxavgvalues:
                    save_path = os.path.join(self.player.args.output_dir, "model.bin")
                    torch.save(self.player.agent.model.state_dict(), save_path)
                    #self.player.max_episode_reward = self.player.episode_reward
                    self.maxavgvalues = avg

                self.player.shanten = -1
                self.player.episode_reward = 0
                self.player.episode_length = 0
                self.player.epsilon = max(self.player.epsilon - (self.player.epsilon_max - self.player.epsilon_min) * self.player.args.epsilon_decay, 1e-1)
                self.player.state = None
                self.player.next_state = None

            if self.player.step > self.args.warmup_steps:
                bs, ba, br, bd, bns = self.player.replay_buffer.sample(n=self.args.batch_size)
                bs = torch.tensor(bs, dtype=torch.float32)
                ba = torch.tensor(ba, dtype=torch.long)
                br = torch.tensor(br, dtype=torch.float32)
                bd = torch.tensor(bd, dtype=torch.float32)
                bns = torch.tensor(bns, dtype=torch.float32)

                loss = self.agent.compute_loss(bs, ba, br, bd, bns)
                loss.backward()
                self.player.optimizer.step()
                self.player.optimizer.zero_grad()

                self.player.log_losses.append(loss.item())

                def soft_update(target, source, tau=0.01):
                    """
                    update target by target = tau * source + (1 - tau) * target.
                    """
                    for target_param, param in zip(target.parameters(), source.parameters()):
                        target_param.data.copy_(target_param.data * (1.0 - tau) + param.data * tau)

                soft_update(self.agent.target_model, self.agent.model)
            if self.player.step > self.p:
                self.p += 10000
                # 3. 画图。
                plt.plot(self.player.log_losses)
                plt.yscale("log")
                plt.savefig(f"{self.args.output_dir}/loss.png", bbox_inches="tight")
                plt.close()

                # plt.plot(np.cumsum(self.player.log_ep_length), self.player.log_ep_rewards)
                # plt.savefig(f"{self.args.output_dir}/episode_reward.png", bbox_inches="tight")
                # plt.close()
                plt.plot(self.winrate)
                plt.yscale("linear")
                plt.xlabel("episode")
                plt.ylabel("winning rate")
                plt.savefig(f"{self.args.output_dir}/winning_rate.png", bbox_inches="tight")
                plt.close()


                plt.plot(self.avgvalues)
                plt.yscale("linear")
                plt.xlabel("episode")
                plt.ylabel("average reward / per 100 episodes")
                plt.savefig(f"{self.args.output_dir}/avg_reward.png", bbox_inches="tight")
                plt.close()
        # 3. 画图。
        plt.plot(self.player.log_losses)
        plt.yscale("log")
        plt.savefig(f"{self.args.output_dir}/loss.png", bbox_inches="tight")
        plt.close()

        #plt.plot(np.cumsum(self.player.log_ep_length), self.player.log_ep_rewards)
        #plt.savefig(f"{self.args.output_dir}/episode_reward.png", bbox_inches="tight")
        #plt.close()

        plt.plot(self.avgvalues)
        plt.yscale("linear")
        plt.xlabel("episode")
        plt.ylabel("average reward / per 100 episodes")
        plt.savefig(f"{self.args.output_dir}/avg_reward.png", bbox_inches="tight")
        plt.close()



    def convert_arr_to_index(self, arr):
        d = []
        for num in arr:
            if num < 200:
                d.append(num-101)
            elif num < 300:
                d.append(num - 192)
            elif num < 400:
                d.append(num - 283)
            elif num < 500:
                d.append((num // 10) % 10 + 26)
            else:
                d.append((num // 10) % 10 + 29)
        return d

    def generate_status(self):
        arr = self.convert_arr_to_index(Rule.convert_tiles_to_arr(self.player.concealed))
        c = collections.Counter(arr)
        state = np.zeros((4, 34), dtype=float)
        #print(Rule.convert_tiles_to_arr(self.player.concealed))
        for k, v in c.items():
            for i in range(v):
                state[i][k] = 1
        return state

    def get_de_action_id(self, action):
        return self.de_action_id[action]

    def get_action_id(self, action):
        return self.action_id[action]

    def get_legal_action_hand(self):
        arr = set()
        for t in self.player.concealed:
            arr.add(self.get_action_id(t.key))
        return list(arr)


def main():
    env = Env()

if __name__ == '__main__':
    main()





