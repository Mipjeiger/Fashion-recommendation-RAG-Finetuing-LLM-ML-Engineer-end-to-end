import mlflow
import torch
from torch import nn
import pandas as pd
import os
from dotenv import load_dotenv
from pathlib import Path

# Create BASE_DIR and .env path
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
# Load environment variables from .env file
load_dotenv(ENV_PATH)

# Set MLflow experiment
mlflow.set_experiment("fashion-embedding")

# Create class refactor for the model
class Embedder(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 128)
        )

    def forward(self, x):
        return self.net(x)
    
# Define dataframe
df = pd.read_parquet(os.path.join(BASE_DIR, "data", "training", "fashion_items.parquet"))
X = torch.randn(len(df), 512) # Dummy data for illustration

model = Embedder()
opt = torch.optim.Adam(model.parameters(),
                       lr=1e-3,
                       weight_decay=1e-5)

# MLflow start run
with mlflow.start_run(run_name="embedding_training"):
    for _ in range(5):
        out = model(X)
        loss = out.norm(dim=1).mean()
        loss.backward()
        opt.step()
        opt.zero_grad()

    mlflow.pytorch.log_model(model, "embedding_model")