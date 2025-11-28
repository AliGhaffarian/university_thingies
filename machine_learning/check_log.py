import model
import torch
import sys
import numpy as np
import syscall_dataset
from syscall_nr_to_str import standard_linux_to_dataset_map

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_PATH = "rnn_syscall_classifier.pt"

# Load checkpoint
checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)

config = checkpoint["config"]

# Recreate model
model = model.RNNClassifier(
    vocab_size=config["vocab_size"],
    embed_dim=config["embed_dim"],
    hidden_dim=config["hidden_dim"],
    num_classes=config["num_classes"],
    pad_idx=config["pad_idx"],
).to(DEVICE)

# Load weights
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

# Load syscall sequence
sequence = open(sys.argv[1]).read().strip().split()
sequence = [ standard_linux_to_dataset_map[int(x)] for x in sequence ]
sequence = torch.tensor([int(x) for x in sequence], dtype=torch.long)

# Add batch dimension and shift padding
sequence = sequence.unsqueeze(0) + 1   # shape: (1, T)
lengths = torch.tensor([sequence.size(1)])

sequence = sequence.to(DEVICE)
lengths = lengths.to(DEVICE)

with torch.no_grad():
    logits = model(sequence, lengths)
    prediction = torch.argmax(logits, dim=1)

vote = prediction.item()
print(syscall_dataset.labels_map[int(vote)])
