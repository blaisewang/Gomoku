"""
An implementation of the policyValueNet in PyTorch (tested in PyTorch 0.2.0 and 0.3.0)

@author: Junxiao Song
"""
import torch
import torch.nn as nn
import torch.optim as optimal
import torch.nn.functional as f
from torch.autograd import Variable
import numpy as np

from game import Board


def set_learning_rate(optimizer, lr):
    """Sets the learning rate to the given value"""
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr


class Net(nn.Module):
    """policy-value network module"""

    def __init__(self, n):
        super(Net, self).__init__()
        self.n = n
        # common layers
        self.conv1 = nn.Conv2d(4, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        # action policy layers
        self.act_conv1 = nn.Conv2d(128, 4, kernel_size=1)
        self.act_fc1 = nn.Linear(4 * self.n * self.n, self.n * self.n)
        # state value layers
        self.val_conv1 = nn.Conv2d(128, 2, kernel_size=1)
        self.val_fc1 = nn.Linear(2 * self.n * self.n, 64)
        self.val_fc2 = nn.Linear(64, 1)

    def forward(self, state_input):
        # common layers     
        x = f.relu(self.conv1(state_input))
        x = f.relu(self.conv2(x))
        x = f.relu(self.conv3(x))
        # action policy layers
        x_act = f.relu(self.act_conv1(x))
        x_act = x_act.view(-1, 4 * self.n * self.n)
        x_act = f.log_softmax(self.act_fc1(x_act), dim=1)
        # state value layers
        x_val = f.relu(self.val_conv1(x))
        x_val = x_val.view(-1, 2 * self.n * self.n)
        x_val = f.relu(self.val_fc1(x_val))
        x_val = f.tanh(self.val_fc2(x_val))
        return x_act, x_val


class PolicyValueNet:
    """policy-value network """

    def __init__(self, n, net_params=None, use_gpu=False):
        self.n = n
        self.use_gpu = use_gpu
        self.l2_const = 1e-4  # coefficient of l2 penalty
        # the policy value net module
        if self.use_gpu:
            self.policy_value_net = Net(self.n).cuda()
        else:
            self.policy_value_net = Net(self.n)
        self.optimizer = optimal.Adam(self.policy_value_net.parameters(), weight_decay=self.l2_const)

        if net_params:
            self.policy_value_net.load_state_dict(net_params)

    def policy_value(self, state_batch):
        """
        input: a batch of states
        output: a batch of action probabilities and state values 
        """
        if self.use_gpu:
            state_batch = Variable(torch.FloatTensor(state_batch).cuda())
            log_act_probability, value = self.policy_value_net(state_batch)
            act_probability = np.exp(log_act_probability.data.cpu().numpy())
            return act_probability, value.data.cpu().numpy()
        else:
            state_batch = Variable(torch.FloatTensor(state_batch))
            log_act_probability, value = self.policy_value_net(state_batch)
            act_probability = np.exp(log_act_probability.data.numpy())
            return act_probability, value.data.numpy()

    def policy_value_fn(self, board: 'Board'):
        """
        input: board
        output: a list of (action, probability) tuples for each available action and the score of the board state
        """
        legal_positions = board.get_available_moves()
        current_state = np.ascontiguousarray(board.current_state().reshape(-1, 4, self.n, self.n))
        if self.use_gpu:
            log_act_probability, value = self.policy_value_net(Variable(torch.from_numpy(current_state)).cuda().float())
            act_probability = np.exp(log_act_probability.data.cpu().numpy().flatten())
        else:
            log_act_probability, value = self.policy_value_net(Variable(torch.from_numpy(current_state)).float())
            act_probability = np.exp(log_act_probability.data.numpy().flatten())
        act_probability = zip(legal_positions, act_probability[legal_positions])
        value = value.data[0][0]
        return act_probability, value

    def train_step(self, state_batch, mcts_probability, winner_batch, lr):
        """perform a training step"""
        # wrap in Variable
        if self.use_gpu:
            state_batch = Variable(torch.FloatTensor(state_batch).cuda())
            mcts_probability = Variable(torch.FloatTensor(mcts_probability).cuda())
            winner_batch = Variable(torch.FloatTensor(winner_batch).cuda())
        else:
            state_batch = Variable(torch.FloatTensor(state_batch))
            mcts_probability = Variable(torch.FloatTensor(mcts_probability))
            winner_batch = Variable(torch.FloatTensor(winner_batch))

        # zero the parameter gradients
        self.optimizer.zero_grad()
        # set learning rate
        set_learning_rate(self.optimizer, lr)

        # forward
        log_act_probability, value = self.policy_value_net(state_batch)
        # define the loss = (z - v)^2 - pi^T * log(p) + c||theta||^2 (Note: the L2 penalty is incorporated in optimizer)
        value_loss = f.mse_loss(value.view(-1), winner_batch)
        policy_loss = -torch.mean(torch.sum(mcts_probability * log_act_probability))
        loss = value_loss + policy_loss
        # backward and optimize
        loss.backward()
        self.optimizer.step()

    def get_policy_param(self):
        net_params = self.policy_value_net.state_dict()
        return net_params
