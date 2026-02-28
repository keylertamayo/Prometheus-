import os
import subprocess
import time
import json
from pathlib import Path

import torch

from rl_brain import RLAgent
from the_hunter import TheHunter
from prometeo_core import ACTIONS


class RLEngine:
    def __init__(self, episodes=100, base_sandbox="./rl_sandbox", model_path="./model.pth"):
        self.episodes = episodes
        self.base_sandbox = base_sandbox
        self.model_path = model_path
        os.makedirs(self.base_sandbox, exist_ok=True)
        self.agent = None

    def _init_agent(self, state_dim, action_dim):
        self.agent = RLAgent(state_dim, action_dim)

    def run_episode(self, episode_id):
        """Run a single episode and collect experience from Prometeo container."""
        ep_dir = os.path.join(self.base_sandbox, f"ep_{episode_id}")
        logs_dir = os.path.join(ep_dir, "logs")
        sandbox_dir = os.path.join(ep_dir, "sandbox")
        os.makedirs(logs_dir, exist_ok=True)
        os.makedirs(sandbox_dir, exist_ok=True)

        # start Prometeo container with current model
        # NOTE: the model file must be copied into sandbox or mounted
        cmd = [
            "docker", "run", "--rm",
            "--name", f"prometeo-rl-{episode_id}",
            "--read-only", "--network", "none",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true",
            "--pids-limit", "100", "--memory", "512m",
            "--volume", f"{os.path.abspath(logs_dir)}:/app/logs",
            "--volume", f"{os.path.abspath(sandbox_dir)}:/app/sandbox",
            "--env", f"MODEL_PATH=/app/logs/model.pth",
            "prometeo-core:latest"
        ]
        # copy the current model file to logs so container can read it
        if os.path.exists(self.model_path):
            try:
                Path(logs_dir).joinpath("model.pth").write_bytes(Path(self.model_path).read_bytes())
            except Exception:
                pass

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # wait for container to finish (max 30s)
        try:
            proc.wait(timeout=35)
        except subprocess.TimeoutExpired:
            proc.kill()

        # after episode, read experience log and hunter report
        exp_file = os.path.join(logs_dir, "experience.log")
        experiences = []
        if os.path.exists(exp_file):
            with open(exp_file) as f:
                for line in f:
                    try:
                        experiences.append(json.loads(line))
                    except Exception:
                        continue
        # convert experiences to training data (placeholder)
        # TODO: compute rewards and push into agent.replay
        return experiences

    def train(self):
        """High-level training loop over episodes."""
        # initialize agent with assumed dimensions
        # state vector currently length 4, action space size = len(ACTIONS)
        self._init_agent(state_dim=4, action_dim=len(ACTIONS))

        for ep in range(self.episodes):
            exps = self.run_episode(ep)
            # placeholder: process experiences and update agent
            # for now simply sync target network periodically
            self.agent.sync_target()
            # save model
            torch.save(self.agent.policy_net.state_dict(), self.model_path)

        print("Training complete. Model saved to", self.model_path)


if __name__ == '__main__':
    engine = RLEngine(episodes=10)
    engine.train()
