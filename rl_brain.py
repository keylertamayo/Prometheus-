import random
from collections import deque

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import numpy as np
except ImportError:
    # RL libraries may not be installed yet
    torch = None
    nn = None
    optim = None
    np = None


class DQNNetwork(nn.Module):
    """Simple multilayer perceptron for value prediction."""
    def __init__(self, input_dim, output_dim, hidden_dims=(64, 64)):
        super().__init__()
        layers = []
        last = input_dim
        for h in hidden_dims:
            layers.append(nn.Linear(last, h))
            layers.append(nn.ReLU())
            last = h
        layers.append(nn.Linear(last, output_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


class ReplayBuffer:
    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return states, actions, rewards, next_states, dones

    def __len__(self):
        return len(self.buffer)


class RLAgent:
    def __init__(self, state_dim, action_dim, lr=1e-3, gamma=0.99):
        if torch is None:
            raise RuntimeError("PyTorch not available")
        self.device = torch.device("cpu")
        self.policy_net = DQNNetwork(state_dim, action_dim).to(self.device)
        self.target_net = DQNNetwork(state_dim, action_dim).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.replay = ReplayBuffer()
        self.gamma = gamma
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01

    def select_action(self, state):
        # state expected as numpy array or list
        if random.random() < self.epsilon:
            return random.randrange(self.policy_net.net[-1].out_features)
        state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(self.device)
        with torch.no_grad():
            qvals = self.policy_net(state_t)
        return int(qvals.argmax().item())

    def store_transition(self, state, action, reward, next_state, done):
        self.replay.push(state, action, reward, next_state, done)

    def update(self, batch_size):
        if len(self.replay) < batch_size:
            return
        states, actions, rewards, next_states, dones = self.replay.sample(batch_size)
        states = torch.tensor(states, dtype=torch.float32).to(self.device)
        actions = torch.tensor(actions, dtype=torch.long).unsqueeze(1).to(self.device)
        rewards = torch.tensor(rewards, dtype=torch.float32).unsqueeze(1).to(self.device)
        next_states = torch.tensor(next_states, dtype=torch.float32).to(self.device)
        dones = torch.tensor(dones, dtype=torch.float32).unsqueeze(1).to(self.device)

        q_values = self.policy_net(states).gather(1, actions)
        next_q = self.target_net(next_states).max(1)[0].unsqueeze(1)
        expected = rewards + (1 - dones) * self.gamma * next_q

        loss = nn.functional.mse_loss(q_values, expected)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # decay exploration
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def sync_target(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())
