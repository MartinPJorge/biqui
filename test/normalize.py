import pandas as pd
import numpy as np
import os
import sys
import argparse
from matplotlib import pyplot as plt
import matplotlib as mpl
from math import ceil
import json

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, required=True,
                        help="CSV with results")
    parser.add_argument("--value", type=float, required=False,
                        help="normalization value",
                        default=1.001) # dedicated@Cloud
    args = parser.parse_args()


    df = pd.read_csv(args.csv, sep=' ').dropna()
    df['cost'] = pd.to_numeric(df['cost'].values) / args.value
    df.to_csv('/tmp/norm.csv', sep=' ', index=False)
    os.system('cat /tmp/norm.csv')

