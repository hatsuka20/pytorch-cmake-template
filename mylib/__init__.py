import torch
import os

torch.classes.load_library(os.path.join(os.path.dirname(__file__), "libcustom_class.so"))
