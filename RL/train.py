"""4.3节DQN算法实现。
"""
import argparse
from collections import defaultdict
import os
import random
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from RL.env import Env

class QNet(nn.Module):
    """QNet.
    Input: feature
    Output: num_act of values
    """

    def __init__(self, dim_obs, num_act):
        super().__init__()
        self.fc1 = nn.Linear(dim_obs, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, num_act)

    def forward(self, obs):
        x = F.relu(self.fc1(obs))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x

class CNN(nn.Module):
    def __init__(self, in_channels=1, num_action=34):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=in_channels, out_channels=2, kernel_size=(3,3), stride=(1,1), padding=(1,1))
        self.conv2 = nn.Conv2d(in_channels=2,out_channels=4, kernel_size=(3,3), stride=(1,1),padding=(1,1))
        self.fc1 = nn.Linear(34*4*4, num_action)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(-1, 4*4*34)
        x = self.fc1(x)
        return x


class DoubleDQN:
    def __init__(self, dim_obs=None, num_act=None, discount=0.9):
        self.discount = discount
        #self.model = QNet(dim_obs, num_act)
        self.model = CNN(in_channels=1, num_action=34)
        #self.target_model = QNet(dim_obs, num_act)
        self.target_model = CNN(in_channels=1, num_action=34)
        self.target_model.load_state_dict(self.model.state_dict())

    def get_qvals(self, obs):
        return self.model(obs)


    def get_action(self, obs):
        qvals = self.model(obs)
        return qvals.argmax()

    def trans(self, s_batch):
        return torch.reshape(torch.tensor(s_batch), (32, 1, 4, 34))

    def compute_loss(self, s_batch, a_batch, r_batch, d_batch, next_s_batch):
        # Compute current Q value based on current states and actions.
        qvals = self.model(self.trans(s_batch)).gather(1, a_batch.unsqueeze(1)).squeeze()
        # next state的value不参与导数计算，避免不收敛。
        next_qvals, _ = self.target_model(self.trans(next_s_batch)).detach().max(dim=1)
        loss = F.mse_loss(r_batch + self.discount * next_qvals * (1 - d_batch), qvals)
        return loss



def soft_update(target, source, tau=0.01):
    """
    update target by target = tau * source + (1 - tau) * target.
    """
    for target_param, param in zip(target.parameters(), source.parameters()):
        target_param.data.copy_(target_param.data * (1.0 - tau) + param.data * tau)


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


def set_seed(args):
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if not args.no_cuda:
        torch.cuda.manual_seed(args.seed)


def train(args, agent):

    env = Env(agent, args)
    env.play_game()



def main():
    parser = argparse.ArgumentParser()
    #parser.add_argument("--env", default="CartPole-v1", type=str, help="Environment name.")
    parser.add_argument("--dim_state", default=34*4, type=int, help="Dimension of state.")
    parser.add_argument("--num_action", default=34, type=int, help="Number of action.")
    parser.add_argument("--discount", default=0.9, type=float, help="Discount coefficient.")
    parser.add_argument("--max_steps", default=300_000, type=int, help="Maximum steps for interaction.")
    parser.add_argument("--lr", default=1e-4, type=float, help="Learning rate.")
    parser.add_argument("--batch_size", default=32, type=int, help="Batch size.")
    parser.add_argument("--no_cuda", action="store_true", help="Avoid using CUDA when available")
    parser.add_argument("--seed", default=42, type=int, help="Random seed.")
    parser.add_argument("--warmup_steps", default=5_000, type=int, help="Warmup steps without training.")
    parser.add_argument("--output_dir", default="output", type=str, help="Output directory.")
    parser.add_argument("--epsilon_decay", default=1 / 5000, type=float, help="Epsilon-greedy algorithm decay coefficient.")
    parser.add_argument("--do_train", action="store_true", help="Train policy.")
    parser.add_argument("--do_eval", action="store_true", help="Evaluate policy.")
    args = parser.parse_args()

    args.device = torch.device("cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu")

    set_seed(args)
    agent = DoubleDQN(dim_obs=args.dim_state, num_act=args.num_action, discount=args.discount)
    agent.model.to(args.device)
    agent.target_model.to(args.device)

    train(args, agent)

    if args.do_eval:
        eval(args, agent)


if __name__ == "__main__":
    main()
