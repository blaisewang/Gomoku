"""
@author: Junxiao Song
"""

import theano
import theano.tensor as t
import lasagne

from game import Board


class PolicyValueNet:
    """policy-value network """

    def __init__(self, n: int, net_params=None):
        self.n = n
        self.learning_rate = t.scalar('learning_rate')
        self.l2_const = 1e-4  # coefficient of l2 penalty
        """create the policy value network """
        self.state_input = t.tensor4('state')
        self.winner = t.vector('winner')
        self.mcts_probability = t.matrix('mcts_probability')
        network = lasagne.layers.InputLayer(shape=(None, 4, self.n, self.n),
                                            input_var=self.state_input)
        # convolutional layers
        network = lasagne.layers.Conv2DLayer(network, num_filters=32, filter_size=(3, 3), pad='same')
        network = lasagne.layers.Conv2DLayer(network, num_filters=64, filter_size=(3, 3), pad='same')
        network = lasagne.layers.Conv2DLayer(network, num_filters=128, filter_size=(3, 3), pad='same')
        # action policy layers
        policy_net = lasagne.layers.Conv2DLayer(network, num_filters=4, filter_size=(1, 1))
        self.policy_net = lasagne.layers.DenseLayer(policy_net, num_units=self.n * self.n,
                                                    nonlinearity=lasagne.nonlinearities.softmax)
        # state value layers
        value_net = lasagne.layers.Conv2DLayer(network, num_filters=2, filter_size=(1, 1))
        value_net = lasagne.layers.DenseLayer(value_net, num_units=64)
        self.value_net = lasagne.layers.DenseLayer(value_net, num_units=1, nonlinearity=lasagne.nonlinearities.tanh)
        # get action probability and state score value
        self.action_probability, self.value = lasagne.layers.get_output([self.policy_net, self.value_net])
        self.policy_value = theano.function([self.state_input], [self.action_probability, self.value],
                                            allow_input_downcast=True)
        """
        Three loss terms：
        loss = (z - v)^2 - pi^T * log(p) + c||theta||^2
        """
        params = lasagne.layers.get_all_params([self.policy_net, self.value_net], trainable=True)
        value_loss = lasagne.objectives.squared_error(self.winner, self.value.flatten())
        policy_loss = lasagne.objectives.categorical_crossentropy(self.action_probability, self.mcts_probability)
        l2_penalty = lasagne.regularization.apply_penalty(params, lasagne.regularization.l2)
        self.loss = lasagne.objectives.aggregate(value_loss + policy_loss, mode='mean') + self.l2_const * l2_penalty
        # policy entropy，for monitoring only
        self.entropy = -t.mean(t.sum(self.action_probability * t.log(self.action_probability + 1e-10), axis=1))
        # get the train op
        updates = lasagne.updates.adam(self.loss, params, learning_rate=self.learning_rate)
        self.train_step = theano.function([self.state_input, self.mcts_probability, self.winner, self.learning_rate],
                                          [self.loss, self.entropy], updates=updates, allow_input_downcast=True)
        if net_params:
            lasagne.layers.set_all_param_values([self.policy_net, self.value_net], net_params)

    def policy_value_func(self, board: 'Board'):
        """
        input: board
        output: a list of (action, probability) tuples for each available action and the score of the board state
        """
        legal_positions = board.get_available_moves()
        current_state = board.get_current_state()
        act_probability, value = self.policy_value(current_state.reshape(-1, 4, self.n, self.n))
        act_probability = zip(legal_positions, act_probability.flatten()[legal_positions])
        return act_probability, value[0][0]

    def get_policy_parameter(self):
        net_params = lasagne.layers.get_all_param_values([self.policy_net, self.value_net])
        return net_params
