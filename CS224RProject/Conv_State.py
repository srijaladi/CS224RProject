import torchimport torch.nn as nnimport randomimport numpy as npclass CONV_STATE:    def __init__(self,version, ENV):        self.TOTAL_OPTIONS = 20        self.version = version        self.ENV = ENV        allowed = ["base", "each", "alt", "old"]        if not(version in allowed):            print("ERROR: ILLEGAL CONV_STATE VERSION")    def conv_state_old(self, state_np):        return torch.flatten(torch.nn.functional.one_hot(torch.tensor(state_np).to(torch.int64), self.TOTAL_OPTIONS)).float()    def conv_state_base(self, state_np):        res = np.zeros((4, 4, 2, 3))        for r in range(4):            for c in range(4):                curr, lr, lc, done = state_np[r][c], [], [], False                for nr in range(4):                    if nr == r: continue                    if state_np[nr][c] == curr and not(done):                         lr.append(curr)                        done = True                    elif curr == 0 or state_np[nr][c] == 0 or done: lr.append(0)                    else:                         lr.append(-max(curr, state_np[nr][c]))                        done = True                done = False                for nc in range(4):                    if nc == c: continue                    if state_np[r][nc] == curr and not(done):                         lc.append(curr)                        done = True                    elif curr ==0 or state_np[r][nc] == 0 or done: lc.append(0)                    else:                         lc.append(-max(curr, state_np[r][nc]))                        done = True                for i, val in enumerate(lr):                    res[r][c][0][i] = val                for i, val in enumerate(lc):                    res[r][c][1][i] = val        input_tensor = torch.tensor(np.reshape(res, (-1,)))        return input_tensor.float()    def conv_state_each(self, state_np):        res = np.reshape(state_np, (-1,))        for a in range(4):            state_next_np, non_term, valid_move = self.ENV.transition(state_np, a)            if not(non_term) or not(valid_move):                res = np.append(res, np.reshape(np.zeros(state_np.shape) - 1, (-1,)))            else:                res = np.append(res, np.reshape(state_np, (-1,)))        input_tensor = torch.tensor(res).float()        return input_tensor    def conv_state_alt(self, state_np):        res = np.zeros(4)        for a in range(4):            state_next_np, non_term, valid_move = self.ENV.transition(state_np, a)            if not(non_term) or not(valid_move):                res[a] = -1            else:                res[a] = 1        input_tensor = torch.tensor(res).float()        return input_tensor        def convert(self, state_np):        if self.version == 'base':            return self.conv_state_base(state_np)        elif self.version == 'each':            return self.conv_state_each(state_np)        elif self.version == 'alt':            return self.conv_state_alt(state_np)        elif self.version == 'old':            return self.conv_state_old(state_np)        else:            print("ERROR: ILLEGAL CONV_STATE VERSION")        