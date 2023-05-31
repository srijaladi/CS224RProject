import torchimport torch.nn as nnimport randomimport numpy as npclass DQN(nn.Module):    def __init__(self, layers, learning_rate, total_actions):        super().__init__()        self.model = nn.Sequential(*layers)        self.optimizer = torch.optim.Adam(params = self.model.parameters(), lr = learning_rate)        self.total_actions = total_actions    def forward(self, input_state):        return self.model(input_state)        def backprop_single(self, state, action, true_value):        self.optimizer.zero_grad()        computed_value = torch.sum(self.model(state) * torch.nn.functional.one_hot(torch.tensor(action).to(torch.int64), self.total_actions))        mse_loss = (computed_value - true_value) ** 2        mse_loss.backward()        self.optimizer.step()        return mse_loss.item()            def backprop_batch(self, states, actions, true_values):        self.optimizer.zero_grad()        mask = torch.nn.functional.one_hot(actions.to(torch.int64), self.total_actions)        values = torch.sum(self.model(states) * mask, dim = 1)        mse_loss = torch.nn.functional.mse_loss(true_values.float(), values.float())        mse_loss.backward()        self.optimizer.step()        return mse_loss.item()