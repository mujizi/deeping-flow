import numpy as np
import torch

import const


class DataLoader(object):
    def __init__(self, src_texts, src_turn, tgt_indexs, tgt_texts, eos_indexs, src_context, tgt_context, batch_size):
        self.sents_size = len(src_texts)
        self._step = 0
        self.stop_step = self.sents_size // batch_size
        self.batch_size = batch_size
        self.src_texts = src_texts.tolist()
        self.src_turn = src_turn
        self.tgt_indexs = tgt_indexs
        self.tgt_texts = tgt_texts
        self.eos_indexs = eos_indexs
        self.src_context = src_context
        self.tgt_context = tgt_context

    def __iter__(self):
        return self

    def __next__(self):
        def pad_to_longest(insts):
            max_len = max(len(inst) for inst in insts)
            inst_data = np.array(
                [inst + [const.PAD] * (max_len - len(inst)) for inst in insts])
            inst_position = np.array(
                [[pos_i+1 if w_i != const.PAD else 0 for pos_i, w_i in enumerate(inst)] for inst in inst_data])

            return inst_data, inst_position, max_len

        def index_pairs(t_indexs, tgt_len):
            indexs = np.array([inst.tolist() + [const.PAD]
                               * (tgt_len - len(inst)) for inst in t_indexs])
            return indexs

        if self._step == self.stop_step:
            self._step = 0
            raise StopIteration()

        _start = self._step*self.batch_size
        _bsz = self.batch_size
        self._step += 1

        src_tensor, src_postion, src_max_len = pad_to_longest(
            self.src_texts[_start:_start+_bsz])
        tgt_tensor, tgt_postion, tgt_max_len = pad_to_longest(
            self.tgt_texts[_start:_start+_bsz])
        tgt_indexs_tensor = index_pairs(
            self.tgt_indexs[_start:_start+_bsz], tgt_max_len)
        turns_tensor, _, _ = pad_to_longest(self.src_turn[_start:_start+_bsz])
        eos_indexs = self.eos_indexs[_start:_start+_bsz]
        src_context = self.src_context[_start:_start+_bsz]
        tgt_context = self.tgt_context[_start:_start+_bsz]

        return (src_tensor, src_postion, turns_tensor), (tgt_tensor, tgt_postion), tgt_indexs_tensor, src_max_len, eos_indexs, tgt_max_len, src_context, tgt_context


if __name__ == "__main__":
    from common import middle_load, middle_save, set_logger

    data = middle_load("data/corpus")

    training_data = DataLoader(
        data["train"]["src_texts"],
        data["train"]["src_turn"],
        data["train"]["tgt_indexs"],
        data["train"]["tgt_texts"],
        data["train"]["eos_indexs"],
        data["train"]["src_context"],
        data["train"]["tgt_context"],
        batch_size=8)

    (src_tensor, src_postion, turns_tensor), (tgt_tensor,
                                              tgt_postion), tgt_indexs_tensor, src_max_len, eos_indexs, tgt_max_len, src_context, tgt_context = next(training_data)

    print(turns_tensor.shape)
