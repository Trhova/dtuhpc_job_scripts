#!/usr/bin/env python3
"""
Quick helper script: plot read quality distribution from a FASTQ file.
"""

import gzip
import matplotlib.pyplot as plt
import numpy as np
from itertools import islice

# Path to a cleaned FASTQ file (you can replace this later)
fastq_path = "/work3/trhova/kneaddata_project/SA_24_09/kneaddata_output/Sample1/Sample1_1_kneaddata_paired_1.fastq"


# -------------------------------------------------------------
# Read PHRED quality scores
# -------------------------------------------------------------
def read_qualities(path, max_reads=50000):
    quals = []
    open_func = gzip.open if path.endswith(".gz") else open
    with open_func(path, "rt") as fh:
        for i, line in enumerate(fh):
            if (i % 4) == 3:  # quality line
                quals.extend([ord(c) - 33 for c in line.strip()])
            if max_reads and i > 4 * max_reads:
                break
    return np.array(quals)

qualities = read_qualities(fastq_path)

# -------------------------------------------------------------
# Plot histogram
# -------------------------------------------------------------
plt.figure(figsize=(7,4))
plt.hist(qualities, bins=np.arange(0, 45), color="skyblue", edgecolor="black")
plt.title("Read Quality Distribution")
plt.xlabel("PHRED Quality Score")
plt.ylabel("Count")
plt.grid(alpha=0.2)
plt.show()

