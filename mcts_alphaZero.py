"""
Monte Carlo Tree Search in AlphaGo Zero style, which uses a policy-value network
to guide the tree search and evaluate the leaf nodes

@author: Junxiao Song
"""
import copy

import numpy as np


def soft_max(x):
    probability = np.exp(x - np.max(x))
    probability /= np.sum(probability)
    return probability


class TreeNode:
    """A node in the MCTS tree. Each node keeps track of its own value Q, prior probability P, and
    its visit-count-adjusted prior score u.
    """

    def __init__(self, parent, prior_p):
        self._parent = parent
        self.children = {}  # a map from action to TreeNode
        self.n_visits = 0
        self._Q = 0
        self._u = 0
        self._P = prior_p

    def expand(self, action_priors):
        """Expand tree by creating new children.
        action_priors -- output from policy function - a list of tuples of actions
            and their prior probability according to the policy function.
        """
        for action, prob in action_priors:
            if action not in self.children:
                self.children[action] = TreeNode(self, prob)

    def select(self, c_puct):
        """Select action among children that gives maximum action value, Q plus bonus u(P).
        Returns:
        A tuple of (action, next_node)
        """
        return max(self.children.items(), key=lambda act_node: act_node[1].get_value(c_puct))

    def update(self, leaf_value):
        """Update node values from leaf evaluation.
        Arguments:
        leaf_value -- the value of subtree evaluation from the current player's perspective.        
        """
        # Count visit.
        self.n_visits += 1
        # Update Q, a running average of values for all visits.
        self._Q += 1.0 * (leaf_value - self._Q) / self.n_visits

    def update_recursive(self, leaf_value):
        """Like a call to update(), but applied recursively for all ancestors.
        """
        # If it is not root, this node's parent should be updated first.
        if self._parent:
            self._parent.update_recursive(-leaf_value)
        self.update(leaf_value)

    def get_value(self, c_puct):
        """Calculate and return the value for this node: a combination of leaf evaluations, Q, and
        this node's prior adjusted for its visit count, u
        c_puct -- a number in (0, inf) controlling the relative impact of values, Q, and
            prior probability, P, on this node's score.
        """
        self._u = c_puct * self._P * np.sqrt(self._parent.n_visits) / (1 + self.n_visits)
        return self._Q + self._u

    def is_leaf(self):
        """Check if leaf node (i.e. no nodes below this have been expanded).
        """
        return self.children == {}

    def is_root(self):
        return self._parent is None


class MCTS:
    """A simple implementation of Monte Carlo Tree Search.
    """

    def __init__(self, policy_value_func, c_puct=5, n_play_out=10000):
        """Arguments:
        policy_value_func -- a function that takes in a board state and outputs a list of (action, probability)
            tuples and also a score in [-1, 1] (i.e. the expected value of the end game score from 
            the current player's perspective) for the current player.
        c_puct -- a number in (0, inf) that controls how quickly exploration converges to the
            maximum-value policy, where a higher value means relying on the prior more
        """
        self._root = TreeNode(None, 1.0)
        self._policy = policy_value_func
        self._c_puct = c_puct
        self._n_play_out = n_play_out

    def _play_out(self, state):
        """Run a single play_out from the root to the leaf, getting a value at the leaf and
        propagating it back through its parents. State is modified in-place, so a copy must be
        provided.
        Arguments:
        state -- a copy of the state.
        """
        node = self._root
        while 1:
            if node.is_leaf():
                break
                # Greedily select next move.
            action, node = node.select(self._c_puct)
            x, y = state.move_to_location(action)
            state.add_move(x, y)

        # Evaluate the leaf using a network which outputs a list of (action, probability)
        # tuples p and also a score v in [-1, 1] for the current player.
        action_probability, leaf_value = self._policy(state)
        # Check for end of game.
        end, winner = state.has_ended()
        if not end:
            node.expand(action_probability)
        else:
            # for end state，return the "true" leaf_value
            if winner == -1:  # tie
                leaf_value = 0.0
            else:
                leaf_value = 1.0 if winner == state.get_current_player() else -1.0

        # Update value and visit count of nodes in this traversal.
        node.update_recursive(-leaf_value)

    def get_move_probability(self, state, temp=1e-3):
        """Runs all play_outs sequentially and returns the available actions and their corresponding probabilities
        Arguments:
        state -- the current state, including both game state and the current player.
        temp -- temperature parameter in (0, 1] that controls the level of exploration
        Returns:
        the available actions and the corresponding probabilities 
        """
        [self._play_out(copy.deepcopy(state)) for _ in range(self._n_play_out)]
        # calc the move probabilities based on the visit counts at the root node
        act_visits = [(act, node.n_visits) for act, node in self._root.children.items()]
        acts, visits = zip(*act_visits)
        act_probability = soft_max(1.0 / temp * np.log(np.array(visits) + 1e-10))

        return acts, act_probability

    def update_with_move(self, last_move: int):
        """Step forward in the tree, keeping everything we already know about the subtree.
        """
        if last_move in self._root.children:
            self._root = self._root.children[last_move]
            self._root._parent = None
        else:
            self._root = TreeNode(None, 1.0)


class MCTSPlayer:
    """AI player based on MCTS"""

    def __init__(self, policy_value_function, c_puct=5, n_play_out=2000, is_self_play=0):
        self.mcts = MCTS(policy_value_function, c_puct, n_play_out)
        self._is_self_play = is_self_play

    def reset_player(self):
        self.mcts.update_with_move(-1)

    def get_action(self, board, temp=1e-3, return_probability=0):
        move_probability = np.zeros(board.n * board.n)
        # the pi vector returned by MCTS as in the alphaGo Zero paper
        if len(board.move_list) < board.n * board.n:
            acts, probability = self.mcts.get_move_probability(board, temp)
            if return_probability == 2:
                return acts, probability
            move_probability[list(acts)] = probability
            if self._is_self_play:
                # add Dirichlet Noise for exploration (needed for self-play training)
                move = np.random.choice(acts, p=0.75 * probability + 0.25 * np.random.dirichlet(
                    0.3 * np.ones(len(probability))))
                self.mcts.update_with_move(move)  # update the root node and reuse the search tree
            else:
                # with the default temp, this is almost equivalent to choosing the move with the highest probability
                move = np.random.choice(acts, p=probability)
                # reset the root node
                self.mcts.update_with_move(-1)
            if return_probability == 1:
                return move, move_probability
            else:
                return move
