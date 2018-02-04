"""
An implementation of the training pipeline of AlphaZero for Gomoku

@author: Junxiao Song
"""

import pickle
import random
import sys
from collections import defaultdict, deque

import numpy as np
import time

from game import Board, Game
from mcts_alphaZero import MCTSPlayer
from mcts_pure import MCTSPlayer as MCTS_Pure
from policy_value_net_pytorch import PolicyValueNet


def print_log(string: str):
    with open("log", 'a') as file:
        file.write(string + "\n")
    file.close()


class TrainPipeline:
    def __init__(self, n, init_model=None):
        # params of the board and the game
        self.n = n
        self.board = Board(self.n)
        self.game = Game(self.board)
        # training params 
        self.learn_rate = 5e-3
        self.lr_multiplier = 1.0  # adaptively adjust the learning rate based on KL
        self.temp = 1.0  # the temperature param
        self.n_play_out = 400  # num of simulations for each move
        self.c_puct = 5
        self.buffer_size = 10000
        self.batch_size = 512  # mini-batch size for training
        self.data_buffer = deque(maxlen=self.buffer_size)
        self.play_batch_size = 1
        self.epochs = 5  # num of train_steps for each update
        self.kl_target = 0.025
        self.check_freq = 50
        self.game_batch_num = 10000
        self.best_win_ratio = 0.0
        self.episode_length = 0
        # num of simulations used for the pure mcts, which is used as the opponent to evaluate the trained policy
        self.pure_mcts_play_out_number = 1000
        if init_model:
            # start training from an initial policy-value net
            policy_param = pickle.load(open(init_model, 'rb'))
            self.policy_value_net = PolicyValueNet(self.n, net_params=policy_param)
        else:
            # start training from a new policy-value net
            self.policy_value_net = PolicyValueNet(self.n)
        self.mcts_player = MCTSPlayer(self.policy_value_net.policy_value_fn, c_puct=self.c_puct,
                                      n_play_out=self.n_play_out, is_self_play=1)

    def get_equal_data(self, play_data):
        """
        augment the data set by rotation and flipping
        play_data: [(state, mcts_probability, winner_z), ..., ...]"""
        extend_data = []
        for state, mcts_probability, winner in play_data:
            for i in [1, 2, 3, 4]:
                # rotate counterclockwise 
                equal_state = np.array([np.rot90(s, i) for s in state])
                equal_mcts_prob = np.rot90(np.flipud(mcts_probability.reshape(self.n, self.n)), i)
                extend_data.append((equal_state, np.flipud(equal_mcts_prob).flatten(), winner))
                # flip horizontally
                equal_state = np.array([np.fliplr(s) for s in equal_state])
                equal_mcts_prob = np.fliplr(equal_mcts_prob)
                extend_data.append((equal_state, np.flipud(equal_mcts_prob).flatten(), winner))
        return extend_data

    def collect_self_play_data(self, n_games=1):
        """collect self-play data for training"""
        for i in range(n_games):
            winner, play_data = self.game.start_self_play(self.mcts_player, temp=self.temp)
            self.episode_length = len(list(play_data))
            # augment the data
            play_data = self.get_equal_data(play_data)
            self.data_buffer.extend(play_data)

    def policy_update(self):
        """update the policy-value net"""
        kl = 0
        new_v = 0

        mini_batch = random.sample(self.data_buffer, self.batch_size)
        state_batch = [data[0] for data in mini_batch]
        mcts_probability_batch = [data[1] for data in mini_batch]
        winner_batch = [data[2] for data in mini_batch]
        old_probability, old_v = self.policy_value_net.policy_value(state_batch)
        for i in range(self.epochs):
            self.policy_value_net.train_step(state_batch, mcts_probability_batch, winner_batch,
                                             self.learn_rate * self.lr_multiplier)
            new_probability, new_v = self.policy_value_net.policy_value(state_batch)
            kl = np.mean(
                np.sum(old_probability * (np.log(old_probability + 1e-10) - np.log(new_probability + 1e-10)), axis=1))
            if kl > self.kl_target * 4:  # early stopping if D_KL diverges badly
                break
        # adaptively adjust the learning rate
        if kl > self.kl_target * 2 and self.lr_multiplier > 0.1:
            self.lr_multiplier /= 1.5
        elif kl < self.kl_target / 2 and self.lr_multiplier < 10:
            self.lr_multiplier *= 1.5

        explained_var_old = 1 - np.var(np.array(winner_batch) - old_v.flatten()) / np.var(np.array(winner_batch))
        explained_var_new = 1 - np.var(np.array(winner_batch) - new_v.flatten()) / np.var(np.array(winner_batch))
        print("kl:{:.5f},lr_multiplier:{:.3f},explained_var_old:{:.3f},explained_var_new:{:.3f}".
              format(kl, self.lr_multiplier, explained_var_old, explained_var_new))

    def policy_evaluate(self, n_games=10):
        """
        Evaluate the trained policy by playing games against the pure MCTS player
        Note: this is only for monitoring the progress of training
        """
        current_mcts_player = MCTSPlayer(self.policy_value_net.policy_value_fn, c_puct=self.c_puct,
                                         n_play_out=self.n_play_out)
        pure_mcts_player = MCTS_Pure(c_puct=5, n_play_out=self.pure_mcts_play_out_number)
        win_cnt = defaultdict(int)
        for i in range(n_games):
            if i % 2:
                winner = self.game.start_play(current_mcts_player, pure_mcts_player)
            else:
                winner = self.game.start_play(pure_mcts_player, current_mcts_player)
                if winner == 1:
                    winner = 2
                elif winner == 2:
                    winner = 1
            win_cnt[winner] += 1
        win_ratio = 1.0 * (win_cnt[1] + 0.5 * win_cnt[-1]) / n_games
        print("number_play_outs:{}, win: {}, lose: {}, tie:{}".
              format(self.pure_mcts_play_out_number, win_cnt[1], win_cnt[2], win_cnt[-1]))
        print_log("number_play_outs:{}, win: {}, lose: {}, tie:{}".
                  format(self.pure_mcts_play_out_number, win_cnt[1], win_cnt[2], win_cnt[-1]))
        return win_ratio

    def run(self):
        """run the training pipeline"""
        try:
            for i in range(self.game_batch_num):
                start_time = time.time()
                self.collect_self_play_data(self.play_batch_size)
                print("batch i:{}, episode_len:{}".format(i + 1, self.episode_length))
                print_log(
                    "batch i:{}, episode_len:{}, in:{}".format(i + 1, self.episode_length, time.time() - start_time))
                start_time = time.time()
                if len(self.data_buffer) > self.batch_size:
                    self.policy_update()
                    # check the performance of the current model，and save the model params
                if (i + 1) % self.check_freq == 0:
                    print("current self-play batch: {}".format(i + 1))
                    print_log("current self-play batch: {}".format(i + 1))
                    win_ratio = self.policy_evaluate()
                    net_params = self.policy_value_net.get_policy_param()  # get model params
                    pickle.dump(net_params, open('current_policy.model', 'wb'), pickle.HIGHEST_PROTOCOL)
                    if win_ratio > self.best_win_ratio:
                        print("\nNew best policy defeated MCTS player with " + str(
                            self.pure_mcts_play_out_number) + " play-out")
                        print_log("\nNew best policy defeated MCTS player with " + str(
                            self.pure_mcts_play_out_number) + " play-out")
                        self.best_win_ratio = win_ratio
                        pickle.dump(net_params, open('best_policy.model', 'wb'), pickle.HIGHEST_PROTOCOL)
                        if self.best_win_ratio == 1.0 and self.pure_mcts_play_out_number < 10000:
                            self.pure_mcts_play_out_number += 1000
                            self.best_win_ratio = 0.0
                print_log(str(time.time() - start_time))
        except KeyboardInterrupt:
            print("\n\rquit")
        except InterruptedError:
            print("\n\rquit")


if __name__ == '__main__':
    length = sys.argv[1]
    if length.isdigit():
        training_pipeline = TrainPipeline(int(length))
        training_pipeline.run()