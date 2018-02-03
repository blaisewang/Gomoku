"""
A pure implementation of the Monte Carlo Tree Search (MCTS)

@author: Junxiao Song
"""
import numpy as np
import copy
from operator import itemgetter

from game import Board


def roll_out_policy_func(board: 'Board'):
    """roll_out_policy_func -- a coarse, fast version of policy_fn used in the roll out phase."""
    # roll out randomly
    return zip(board.get_available_moves(), np.random.rand(len(board.get_available_moves())))


def policy_value_func(board: 'Board'):
    """a function that takes in a state and outputs a list of (action, probability)
    tuples and a score for the state"""
    # return uniform probabilities and 0 score for pure MCTS
    return zip(board.get_available_moves(),
               np.ones(len(board.get_available_moves())) / len(board.get_available_moves())), 0


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
        return max(iter(self.children.items()), key=lambda act_node: act_node[1].get_value(c_puct))

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


class MCTS(object):
    """A simple implementation of Monte Carlo Tree Search.
    """

    def __init__(self, policy_value_function, c_puct=5, n_play_out=10000):
        """Arguments:
        policy_value_func -- a function that takes in a board state and outputs a list of (action, probability)
            tuples and also a score in [-1, 1] (i.e. the expected value of the end game score from 
            the current player's perspective) for the current player.
        c_puct -- a number in (0, inf) that controls how quickly exploration converges to the
            maximum-value policy, where a higher value means relying on the prior more
        """
        self._root = TreeNode(None, 1.0)
        self._policy = policy_value_function
        self._c_puct = c_puct
        self._n_play_out = n_play_out

    def _play_out(self, state: 'Board'):
        """Run a single play out from the root to the leaf, getting a value at the leaf and
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

        action_probability, _ = self._policy(state)
        # Check for end of game
        end, winner = state.has_ended()
        if not end:
            node.expand(action_probability)
        # Evaluate the leaf node by random roll out
        leaf_value = self._evaluate_roll_out(state)
        # Update value and visit count of nodes in this traversal.
        node.update_recursive(-leaf_value)

    @staticmethod
    def _evaluate_roll_out(state: 'Board', limit=1000):
        """Use the roll out policy to play until the end of the game, returning +1 if the current
        player wins, -1 if the opponent wins, and 0 if it is a tie.
        """
        winner = -1
        player = state.get_current_player()
        for i in range(limit):
            end, winner = state.has_ended()
            if end:
                break
            max_action = max(roll_out_policy_func(state), key=itemgetter(1))[0]
            x, y = state.move_to_location(max_action)
            state.add_move(x, y)
        else:
            # If no break from the loop, issue a warning.
            print("WARNING: roll out reached move limit")
        if winner == -1:  # tie
            return 0
        else:
            return 1 if winner == player else -1

    def get_move(self, state: 'Board'):
        """Runs all play outs sequentially and returns the most visited action.
        Arguments:
        state -- the current state, including both game state and the current player.
        Returns:
        the selected action
        """
        for n in range(self._n_play_out):
            state_copy = copy.deepcopy(state)
            self._play_out(state_copy)
        return max(iter(self._root.children.items()), key=lambda act_node: act_node[1].n_visits)[0]

    def update_with_move(self, last_move):
        """Step forward in the tree, keeping everything we already know about the subtree.
        """
        if last_move in self._root.children:
            self._root = self._root.children[last_move]
            self._root._parent = None
        else:
            self._root = TreeNode(None, 1.0)


class MCTSPlayer(object):
    """AI player based on MCTS"""

    def __init__(self, c_puct=5, n_play_out=2000):
        self.mcts = MCTS(policy_value_func, c_puct, n_play_out)

    def reset_player(self):
        self.mcts.update_with_move(-1)

    def get_action(self, board: 'Board'):
        if len(board.move_list) < board.n * board.n:
            move = self.mcts.get_move(board)
            self.mcts.update_with_move(-1)
            return move
