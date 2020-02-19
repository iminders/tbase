# -*- coding:utf-8 -*-
import os
from datetime import datetime

import torch
from torch.utils.tensorboard import SummaryWriter

from tbase.agents.base.base_agent import BaseAgent
from tbase.common.optimizers import get_optimizer_func
from tbase.network.polices import get_policy_net
from tbase.network.values import get_value_net


# Actor Critic Agent
class ACAgent(BaseAgent):
    def __init__(self, env, args, *other_args):
        super(ACAgent, self).__init__(env, args, other_args)
        optimizer_fn = get_optimizer_func(args.opt_fn)()
        # policy net
        self.policy = get_policy_net(env, args)
        self.target_policy = get_policy_net(env, args)
        self.policy_opt = optimizer_fn(
            params=filter(lambda p: p.requires_grad, self.policy.parameters()),
            lr=self.policy.learning_rate)
        # value net
        self.value = get_value_net(env, args)
        self.target_value = get_value_net(env, args)
        self.value_opt = optimizer_fn(
            params=filter(lambda p: p.requires_grad, self.value.parameters()),
            lr=self.args.lr)
        TIMESTAMP = "{0:%Y-%m-%dT%H-%M-%S/}".format(datetime.now())
        log_dir = os.path.join(args.tensorboard_dir, TIMESTAMP)
        self.writer = SummaryWriter(log_dir)
        self.best_portfolio = -1.0
        self.run_id = args.run_id

    def save(self, dir):
        torch.save(
            self.policy.state_dict(),
            '{}/{}.{}.policy.pkl'.format(dir, self.name, self.run_id)
        )
        torch.save(
            self.value.state_dict(),
            '{}/{}.{}.value.pkl'.format(dir, self.name, self.run_id)
        )

    def load(self, dir):
        if dir is None or not os.path.exist(dir):
            raise ValueError("dir is invalid")
        self.policy.load_state_dict(
            torch.load('{}/{}.{}.policy.pkl'.format(
                dir, self.name, self.run_id))
        )
        self.value.load_state_dict(
            torch.load('{}/{}.{}.value.pkl'.format(
                dir, self.name, self.run_id))
        )

    # 探索与搜集samples
    def explore(self, explore_size, sample_size):
        raise NotImplementedError

    def learn(*args):
        raise NotImplementedError

    def save_best_portofolio(self, dir):
        best_portfolio_path = os.path.join(dir, "best_portfolios.txt")
        f = open(best_portfolio_path, "a")
        msg = "=" * 80 + "\n"
        msg += "best_portfolio: " + str(self.best_portfolio) + "\n"
        msg += str(self.args) + "\n"
        msg += datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"

        f.write(msg)
        f.close()

    def print_net(self, net):
        for param_tensor in net.state_dict():
            print(param_tensor, "\t", net.state_dict()[param_tensor].size())