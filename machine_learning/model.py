"""
Simple RNN-based classifier for syscall sequence classification.
- Uses torch.nn.RNN (NOT LSTM/GRU)
- Handles padding via pack_padded_sequence
- Saves trained model to disk

Assumptions:
- Dataset code provided by the user is available and importable as `syscall_dataset`
- PAD_VALUE is -1
- longest_elem_size is fixed and known
- Labels are binary (0: normal, 1: attack)
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.nn.utils.rnn import pack_padded_sequence

import syscall_dataset


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = 32
EPOCHS = 10
EMBED_DIM = 64
HIDDEN_DIM = 128
NUM_CLASSES = 2
MODEL_PATH = "rnn_syscall_classifier.pt"

PAD_VALUE = syscall_dataset.PAD_VALUE


def compute_lengths(batch, pad_value):
    # batch: (B, T)
    return (batch != pad_value).sum(dim=1)


class RNNClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_classes, pad_idx):
        super().__init__()

        self.embedding = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=embed_dim,
            padding_idx=pad_idx
        )

        self.rnn = nn.RNN(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            batch_first=True
        )

        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x, lengths):
        # x: (B, T)
        embedded = self.embedding(x)

        packed = pack_padded_sequence(
            embedded,
            lengths.cpu(),
            batch_first=True,
            enforce_sorted=False
        )

        _, h_n = self.rnn(packed)
        # h_n: (1, B, H)

        logits = self.fc(h_n.squeeze(0))
        return logits

def test_accuracy(model, dataloader, device, pad_value):
    model.eval()

    correct = 0
    total = 0

    with torch.no_grad():
        for sequences, lengths, labels in dataloader:
            # shift PAD_VALUE for embedding
            sequences = sequences + 1

            sequences = sequences.to(device)
            lengths = lengths.to(device)
            labels = labels.to(device)

            outputs = model(sequences, lengths)
            preds = torch.argmax(outputs, dim=1)

            correct += (preds == labels).sum().item()
            total += labels.size(0)

    accuracy = correct / total
    return accuracy

if __name__ == "__main__":

    def collate_fn(batch):
        sequences, labels = zip(*batch)
        sequences = torch.stack(sequences)
        labels = torch.tensor(labels, dtype=torch.long)

        lengths = compute_lengths(sequences, PAD_VALUE)
        return sequences, lengths, labels


    train_dataset = syscall_dataset.SyscallSequenceDataset(
        annotations_file="./labels_training.csv",
        syscall_seq_dir="./dataset/",
        train=True
    )

    test_dataset = syscall_dataset.SyscallSequenceDataset(
        annotations_file="./labels_testing.csv",
        syscall_seq_dir="./dataset/",
        train=False
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        collate_fn=collate_fn
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        collate_fn=collate_fn
        )

# Syscall numbers are >= 0, PAD_VALUE = -1 → shift by +1
    VOCAB_SIZE = int(torch.max(torch.cat([
        torch.stack([x for x, _ in train_dataset])
    ])).item()) + 2

    PAD_IDX = PAD_VALUE + 1

    model = RNNClassifier(
        vocab_size=VOCAB_SIZE,
        embed_dim=EMBED_DIM,
        hidden_dim=HIDDEN_DIM,
        num_classes=NUM_CLASSES,
        pad_idx=PAD_IDX
    ).to(DEVICE)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    model.train()

    for epoch in range(EPOCHS):
        print(epoch)
        total_loss = 0.0
        accuracy_list = []

        for sequences, lengths, labels in train_loader:
            # shift PAD_VALUE (-1) → 0 for embedding
            sequences = sequences + 1

            sequences = sequences.to(DEVICE)
            lengths = lengths.to(DEVICE)
            labels = labels.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(sequences, lengths)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            # compute accuracy
            pred = [ torch.argmax(x, dim=0) for x in outputs ]
            class_val = [ x.item() for x in pred ]
            accuracy_list += [ class_val[i] == labels[i] for i in range(len(labels)) ]

            total_loss += loss.item()

        accuracy = 0
        accuracy = sum(accuracy_list)
        accuracy = (accuracy / len(accuracy_list)) * 100
        model.eval()
        print(f"Epoch {epoch + 1}/{EPOCHS}, Loss: {total_loss:.4f}, Train Accuracy: {accuracy}, Test Accuracy: {test_accuracy(model, test_loader, DEVICE, PAD_VALUE) * 100}")
        model.train()


    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": {
                "vocab_size": VOCAB_SIZE,
                "embed_dim": EMBED_DIM,
                "hidden_dim": HIDDEN_DIM,
                "num_classes": NUM_CLASSES,
                "pad_idx": PAD_IDX,
            }
        },
        MODEL_PATH
    )

    print(f"Model saved to {MODEL_PATH}")

