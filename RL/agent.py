from utils.player import Player
import random
import numpy as np
from utils.tile import Tile
from dataclasses import dataclass, field
import torch
from mahjong.shanten import Shanten
from mahjong.tile import TilesConverter
from collections import defaultdict
from utils.rule import Rule

@dataclass
class ReplayBuffer:
    maxsize: int
    size: int = 0
    state: list = field(default_factory=list)
    action: list = field(default_factory=list)
    next_state: list = field(default_factory=list)
    reward: list = field(default_factory=list)
    done: list = field(default_factory=list)

    def push(self, state, action, reward, done, next_state):
        if self.size < self.maxsize:
            self.state.append(state)
            self.action.append(action)
            self.reward.append(reward)
            self.done.append(done)
            self.next_state.append(next_state)
        else:
            position = self.size % self.maxsize
            self.state[position] = state
            self.action[position] = action
            self.reward[position] = reward
            self.done[position] = done
            self.next_state[position] = next_state
        self.size += 1

    def sample(self, n):
        total_number = self.size if self.size < self.maxsize else self.maxsize
        indices = np.random.randint(total_number, size=n)
        state = [self.state[i] for i in indices]
        action = [self.action[i] for i in indices]
        reward = [self.reward[i] for i in indices]
        done = [self.done[i] for i in indices]
        next_state = [self.next_state[i] for i in indices]
        return state, action, reward, done, next_state



class AgentPlayer(Player):
    def __init__(self, nick="agent", score: int = 0, isViewer: bool = True, viewerPosition: str = '东',
                 screen=None, clock=None, env=None, agent=None, args=None):
        super().__init__(nick=nick, score=score, isViewer=isViewer, viewerPosition=viewerPosition,
                         screen=screen, clock=clock)
        self.env = env
        self.agent = agent
        self.step = 0
        self.action_space = []
        self.args = args
        self.replay_buffer = ReplayBuffer(10_0000)
        self.optimizer = torch.optim.Adam(agent.model.parameters(), lr=args.lr)
        self.optimizer.zero_grad()
        self.state = None
        self.action = None
        self.next_state = None
        self.shanten = -1

        self.epsilon = 1
        self.epsilon_max = 1
        self.epsilon_min = 0.1
        self.episode_reward = 0
        self.episode_length = 0
        self.max_episode_reward = -float("inf")
        self.log_ep_length = []
        self.log_ep_rewards = []
        self.log_losses = [0]

        self.agent.model.train()
        self.agent.target_model.train()
        self.agent.model.zero_grad()
        self.agent.target_model.zero_grad()

    def action_sample(self):
        p = random.choice(self.action_space)
        return p

    def decide_discard(self) -> Tile:
        self.action_space = self.env.get_legal_action_hand()
        shanten = Shanten()
        m, p, s, h = Rule.convert_arr_to_mpsh(Rule.convert_tiles_to_arr(self.concealed))
        tiles = TilesConverter.string_to_34_array(man=m, sou=s, pin=p, honors=h)
        result = shanten.calculate_shanten(tiles)
        if self.state is None:
            self.state = self.env.generate_status()
        else:
            self.next_state = self.env.generate_status()
            reward = 0
            if result < self.shanten:
                reward = 50
            elif result > self.shanten:
                reward = -60
            else:
                if result == 0:
                    reward = 30
                else:
                    reward = -5
            done = False
            self.episode_reward += reward
            self.episode_length += 1

            self.replay_buffer.push(self.state, self.action, reward, done, self.next_state)
            self.state = self.next_state

            if self.step > self.args.warmup_steps:
                bs, ba, br, bd, bns = self.replay_buffer.sample(n=self.args.batch_size)
                bs = torch.tensor(bs, dtype=torch.float32)
                ba = torch.tensor(ba, dtype=torch.long)
                br = torch.tensor(br, dtype=torch.float32)
                bd = torch.tensor(bd, dtype=torch.float32)
                bns = torch.tensor(bns, dtype=torch.float32)

                loss = self.agent.compute_loss(bs, ba, br, bd, bns)
                loss.backward()
                self.optimizer.step()
                self.optimizer.zero_grad()

                self.log_losses.append(loss.item())

                def soft_update(target, source, tau=0.01):
                    """
                    update target by target = tau * source + (1 - tau) * target.
                    """
                    for target_param, param in zip(target.parameters(), source.parameters()):
                        target_param.data.copy_(target_param.data * (1.0 - tau) + param.data * tau)

                soft_update(self.agent.target_model, self.agent.model)

        self.shanten = result
        if np.random.rand() < self.epsilon or self.step < self.args.warmup_steps:
            action = self.action_sample()
        else:
            #qvals = self.agent.get_qvals(torch.from_numpy(self.state).float())
            qvals = self.agent.get_qvals(self.transfer(self.state))
            for i in range(34):
                tile = Rule.convert_key_to_tile(self.env.get_de_action_id(i))
                if tile not in self.concealed:
                    qvals[0][i] = float("-inf")
            action = qvals.argmax()
            action = action.item()
        self.action = action
        #self.print_concealed()
        self.step += 1
        return Rule.convert_key_to_tile(self.env.get_de_action_id(self.action))

    def transfer(self, state):
        return torch.reshape(torch.from_numpy(state).float(), (1, 34, 4))

    def print_concealed(self):
        p = []
        for tile in self.concealed:
            p.append(tile.face)
        print(p)