#tutorial: https://blog.roboflow.com/pytorch-custom-dataset/
import torch
from numpy.dtypes import LongDType
from torch.utils.data import Dataset
from torchvision import datasets
import pandas as pd
import os
import numpy as np

from syscall_nr_to_str import syscall_name_to_nr_standard_linux, dataset_syscall_id_map, PAD_VALUE

labels_map = {
    0: "normal",
    1: "attack"
}

longest_elem_size = int( open('./longest_elem', 'r').read() )

class SyscallSequenceDataset(Dataset):
    def __init__(self, annotations_file, syscall_seq_dir, train: bool, target_transform=None):
        self.syscall_seq_labels = pd.read_csv(annotations_file)
        if train:
            self.syscall_seq_dir = syscall_seq_dir + "/training"
        else:
            self.syscall_seq_dir = syscall_seq_dir + "/testing"
        #self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.syscall_seq_labels)

    def __getitem__(self, idx):
        syscall_seq_path = os.path.join(self.syscall_seq_dir, self.syscall_seq_labels.iloc[idx, 0])
        syscall_seq = [ int(x) for x in open(syscall_seq_path).read().split() ]
        syscall_seq += ( [PAD_VALUE] * (longest_elem_size - len(syscall_seq)) ) # pad the dataset
        label = self.syscall_seq_labels.iloc[idx, 1]
        syscall_seq = np.array(syscall_seq)
        syscall_seq = torch.from_numpy(syscall_seq)
        syscall_seq = syscall_seq.to(torch.long)
        if self.target_transform:
            label = self.target_transform(label)
        return syscall_seq, label

def repr_single_sequence(syscall_sequence, map = dataset_syscall_id_map) -> str:
    ret : str = ""
    for syscall in syscall_sequence:
        try:
            ret += map[syscall]
        except:
            ret += "unknown"
        ret += ", "

    return ret
