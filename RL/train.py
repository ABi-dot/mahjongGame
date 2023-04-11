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
from env import Env

class QNet(nn.Module):
    """QNet.
    Input: feature
    Output: num_act of values
    """

    def __init__(self, dim_state, num_action):
        super().__init__()
        self.fc1 = nn.Linear(dim_state, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, num_action)

    def forward(self, state):
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class DQN:
    def __init__(self, dim_state=None, num_action=None, discount=0.9):
        self.discount = discount
        self.Q = QNet(dim_state, num_action)
        self.target_Q = QNet(dim_state, num_action)
        self.target_Q.load_state_dict(self.Q.state_dict())

    def get_qvals(self, state):
        return self.Q(state)

    def get_action(self, state):
        qvals = self.Q(state)
        return qvals.argmax()

    def compute_loss(self, s_batch, a_batch, r_batch, d_batch, next_s_batch):
        # 计算s_batch，a_batch对应的值。
        qvals = self.Q(s_batch).gather(1, a_batch.unsqueeze(1)).squeeze()
        # 使用target Q网络计算next_s_batch对应的值。
        next_qvals, _ = self.target_Q(next_s_batch).detach().max(dim=1)
        # 使用MSE计算loss。
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


def eval(args, agent):
    agent = DQN(args.dim_state, args.num_action)
    model_path = os.path.join(args.output_dir, "model.bin")
    agent.Q.load_state_dict(torch.load(model_path))

    episode_length = 0
    episode_reward = 0
    state, _ = env.reset()
    for i in range(5000):
        episode_length += 1
        action = agent.get_action(torch.from_numpy(state)).item()
        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
        env.render()
        episode_reward += reward

        state = next_state
        if done is True:
            print(f"episode reward={episode_reward}, episode length{episode_length}")
            state, _ = env.reset()
            episode_length = 0
            episode_reward = 0


def main():
    parser = argparse.ArgumentParser()
    #parser.add_argument("--env", default="CartPole-v1", type=str, help="Environment name.")
    parser.add_argument("--dim_state", default=34*4, type=int, help="Dimension of state.")
    parser.add_argument("--num_action", default=34, type=int, help="Number of action.")
    parser.add_argument("--discount", default=0.9, type=float, help="Discount coefficient.")
    parser.add_argument("--max_steps", default=100_000, type=int, help="Maximum steps for interaction.")
    parser.add_argument("--lr", default=1e-3, type=float, help="Learning rate.")
    parser.add_argument("--batch_size", default=32, type=int, help="Batch size.")
    parser.add_argument("--no_cuda", action="store_true", help="Avoid using CUDA when available")
    parser.add_argument("--seed", default=42, type=int, help="Random seed.")
    parser.add_argument("--warmup_steps", default=2000, type=int, help="Warmup steps without training.")
    parser.add_argument("--output_dir", default="output", type=str, help="Output directory.")
    parser.add_argument("--epsilon_decay", default=1 / 3000, type=float, help="Epsilon-greedy algorithm decay coefficient.")
    parser.add_argument("--do_train", action="store_true", help="Train policy.")
    parser.add_argument("--do_eval", action="store_true", help="Evaluate policy.")
    args = parser.parse_args()

    args.device = torch.device("cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu")

    set_seed(args)
    agent = DQN(dim_state=args.dim_state, num_action=args.num_action, discount=args.discount)
    agent.Q.to(args.device)
    agent.target_Q.to(args.device)

    train(args, agent)

    if args.do_eval:
        eval(args, agent)


if __name__ == "__main__":
    main()
