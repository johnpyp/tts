from os import path as pt
import random
import math
import os


def ensure_dirs(*dir_paths):
    for dir_path in dir_paths:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)


def data_split(
    dataset_dir, train_percent, valid_percent, filelists_dir, train_file, valid_file
):
    ensure_dirs(filelists_dir)
    dataset_file = pt.join(dataset_dir, "metadata.csv")
    wavs_dir = pt.join(dataset_dir, "wavs")
    train_filepath = pt.join(filelists_dir, train_file)
    valid_filepath = pt.join(filelists_dir, valid_file)

    data = [l for l in open(dataset_file, "r")]

    train_file = open(train_filepath, "w")
    valid_file = open(valid_filepath, "w")

    num_of_data = len(data)
    num_train = int((train_percent / 100.0) * num_of_data)
    num_valid = int((valid_percent / 100.0) * num_of_data)

    data_fractions = [num_train, num_valid]
    split_data = [[], [], []]

    rand_data_ind = 0

    for split_ind, fraction in enumerate(data_fractions):
        for _i in range(fraction):
            rand_data_ind = random.randint(0, len(data) - 1)
            file, text = data[rand_data_ind].split("|")[:2]
            file = pt.splitext(pt.basename(file))[0]
            l = pt.join(wavs_dir, file + ".wav") + "|" + text.strip() + "\n"
            split_data[split_ind].append(l)
            data.pop(rand_data_ind)

    for l in split_data[0]:
        train_file.write(l)

    for l in split_data[1]:
        valid_file.write(l)

    train_file.close()
    valid_file.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "dataset_dir",
        type=str,
        help="LJSpeech-like dataset directory",
    )
    parser.add_argument("--train_percent", default=85, type=int, help="Train %%")
    parser.add_argument("--valid_percent", default=15, type=int, help="Validation %%")
    parser.add_argument(
        "--filelists_dir",
        default="filelists",
        type=str,
        help="Filelists output directory",
    )
    parser.add_argument(
        "--train_file", default="train.txt", type=str, help="Training output file"
    )
    parser.add_argument(
        "--valid_file",
        default="validation.txt",
        type=str,
        help="Validation output file",
    )
    args = parser.parse_args()
    data_split(
        args.dataset_dir,
        args.train_percent,
        args.valid_percent,
        args.filelists_dir,
        args.train_file,
        args.valid_file,
    )
