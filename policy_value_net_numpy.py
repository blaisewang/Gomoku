"""
Implement the policy value network using numpy, so that we can play with the
trained AI model without installing any DL framework

@author: Junxiao Song
"""
import numpy as np

from game import Board


def soft_max(x):
    probability = np.exp(x - np.max(x))
    probability /= np.sum(probability)
    return probability


def rectified_linear_unit(x):
    out = np.maximum(x, 0)
    return out


def convolutional_forward(x, w, b, stride=1, padding=1):
    n_filters, d_filter, h_filter, w_filter = w.shape
    w = w[:, :, ::-1, ::-1]
    n_x, d_x, h_x, w_x = x.shape
    h_out = (h_x - h_filter + 2 * padding) / stride + 1
    w_out = (w_x - w_filter + 2 * padding) / stride + 1
    h_out, w_out = int(h_out), int(w_out)
    x_col = im2col_indices(x, h_filter, w_filter, padding=padding, stride=stride)
    w_col = w.reshape(n_filters, -1)
    out = (np.dot(w_col, x_col).T + b).T
    out = out.reshape(n_filters, h_out, w_out, n_x)
    out = out.transpose(3, 0, 1, 2)
    return out


def fc_forward(x, w, b):
    out = np.dot(x, w) + b
    return out


def get_im2col_indices(x_shape, field_height, field_width, padding=1, stride=1):
    n, c, h, w = x_shape
    assert (h + 2 * padding - field_height) % stride == 0
    assert (w + 2 * padding - field_height) % stride == 0
    out_height = int((h + 2 * padding - field_height) / stride + 1)
    out_width = int((w + 2 * padding - field_width) / stride + 1)

    i0 = np.repeat(np.arange(field_height), field_width)
    i0 = np.tile(i0, c)
    i1 = stride * np.repeat(np.arange(out_height), out_width)
    j0 = np.tile(np.arange(field_width), field_height * c)
    j1 = stride * np.tile(np.arange(out_width), out_height)
    i = i0.reshape(-1, 1) + i1.reshape(1, -1)
    j = j0.reshape(-1, 1) + j1.reshape(1, -1)

    k = np.repeat(np.arange(c), field_height * field_width).reshape(-1, 1)

    return k.astype(int), i.astype(int), j.astype(int)


def im2col_indices(x, field_height, field_width, padding=1, stride=1):
    """ An implementation of im2col based on some fancy indexing """
    # Zero-pad the input
    p = padding
    x_padded = np.pad(x, ((0, 0), (0, 0), (p, p), (p, p)), mode='constant')

    k, i, j = get_im2col_indices(x.shape, field_height, field_width, padding, stride)

    cols = x_padded[:, k, i, j]
    c = x.shape[1]
    cols = cols.transpose(1, 2, 0).reshape(field_height * field_width * c, -1)
    return cols


class PolicyValueNetNumpy:
    """policy-value network in numpy """

    def __init__(self, n: int, net_params):
        self.n = n
        self.params = net_params

    def policy_value_func(self, board: 'Board'):
        """
        input: board
        output: a list of (action, probability) tuples for each available action and the score of the board state
        """
        legal_positions = board.get_available_moves()
        current_state = board.get_current_state()

        # first 3 convolutional layers with ReLU nonlinear
        x = current_state.reshape(-1, 4, self.n, self.n)
        for i in [0, 2, 4]:
            x = rectified_linear_unit(convolutional_forward(x, self.params[i], self.params[i + 1]))
        # policy head
        x_p = rectified_linear_unit(convolutional_forward(x, self.params[6], self.params[7], padding=0))
        x_p = fc_forward(x_p.flatten(), self.params[8], self.params[9])
        act_probability = soft_max(x_p)
        # value head
        x_v = rectified_linear_unit(convolutional_forward(x, self.params[10], self.params[11], padding=0))
        x_v = rectified_linear_unit(fc_forward(x_v.flatten(), self.params[12], self.params[13]))
        value = np.tanh(fc_forward(x_v, self.params[14], self.params[15]))[0]

        act_probability = zip(legal_positions, act_probability.flatten()[legal_positions])
        return act_probability, value
