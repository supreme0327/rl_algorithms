# -*- coding: utf-8 -*-
"""Abstract Agent used for all agents.

- Author: Curt Park
- Contact: curt.park@medipixel.io
"""

import argparse
import os
from abc import ABC, abstractmethod
from typing import Tuple

import git
import gym
import numpy as np
import torch


class AbstractAgent(ABC):
    """Abstract Agent used for all agents.

    Args:
        env (gym.Env): openAI Gym environment with discrete action space
        args (argparse.Namespace): arguments including hyperparameters and training settings

    Attributes:
        env (gym.Env): openAI Gym environment with discrete action space
        args (argparse.Namespace): arguments including hyperparameters and training settings
        state_dim (int): dimension of state space
        action_dim (int): dimension of action space
        action_low (float): lower bound of the action value
        action_high (float): upper bound of the action value

    """

    def __init__(self, env: gym.Env, args: argparse.Namespace):
        """Initialization."""
        self.args = args
        self.env = env
        self.state_dim = env.observation_space.shape[0]
        self.action_dim = env.action_space.shape[0]
        self.action_low = float(env.action_space.low[0])
        self.action_high = float(env.action_space.high[0])

    @abstractmethod
    def select_action(self, state: np.ndarray):
        pass

    @abstractmethod
    def step(self, action: torch.Tensor) -> Tuple[np.ndarray, np.float64, bool]:
        pass

    @abstractmethod
    def update_model(self):
        pass

    @abstractmethod
    def load_params(self):
        pass

    @abstractmethod
    def save_params(self, name: str, params: dict, n_episode: int):
        if not os.path.exists("./save"):
            os.mkdir("./save")

        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha

        path = os.path.join(
            "./save/" + name + "_" + sha[:7] + "_ep_" + str(n_episode) + ".pt"
        )
        torch.save(params, path)

        print("[INFO] Saved the model and optimizer to", path)

    @abstractmethod
    def train(self):
        pass

    def test(self):
        """Test the agent."""
        for i_episode in range(self.args.episode_num):
            state = self.env.reset()
            done = False
            score = 0

            while not done:
                if self.args.render and i_episode >= self.args.render_after:
                    self.env.render()

                action = self.select_action(state)
                next_state, reward, done = self.step(action)

                state = next_state
                score += reward

            print("[INFO] episode %d\ttotal score: %d" % (i_episode, score))

        # termination
        self.env.close()