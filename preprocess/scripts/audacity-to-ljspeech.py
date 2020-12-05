from num2words import num2words
import unicodedata
import argparse
import subprocess
import csv
import os
import re
import shutil
import sys
from os import path as pt

import inflect
import srt
from pydub import AudioSegment

# Regex pattern to find numbers in strings.
# Accounts for possible commas and decimals
# Not perfect but 'hopefully' transciptions
# shouldn't have that bad of formatting errors
num_pattern = r"[\d]+(?:,?[\d]{3})*(?:\.[\d]+)?"


#
titles = {
    r"Mr\.": "Mister",
    r"Mrs\.": "Misess",
    r"Dr\.": "Doctor",
    r"No\.": "Number",
    r"St\.": "Saint",
    r"Co\.": "Company",
    r"Jr\.": "Junior",
    r"Maj\.": "Major",
    r"Gen\.": "General",
    r"Drs\.": "Doctors",
    r"Rev\.": "Reverend",
    r"Lt\.": "Lieutenant",
    r"Hon\.": "Honorable",
    r"Sgt\.": "Sergeant",
    r"Capt\.": "Captain",
    r"Esq\.": "Esquire",
    r"Ltd\.": "Limited",
    r"Col\.": "Colonel",
    r"Ft\.": "Fort",
}

# Do these manually? Also roman numerals are tricky too
# There are obviously more currency symbols. Add more as needed.
troublesome = ["$", "£", "€", "§"]


def dollar_repl(match):
    if int(match.group(1)) == 1:
        return f"1 dollar"
    return f"{match.group(1)} dollars"


def date_repl(match):
    text = match.group(1)
    n = int(text)
    if not 1800 <= n <= 2100:
        return text
    return num2words(n, to="year")


def ordinal_repl(match):
    n = int(match.group(1))
    return num2words(n, to="ordinal")


def acronym_repl(match):
    text = match.group(1)
    interspersed = " ".join(list(text))
    if bool(match.group(2)):
        interspersed += " "
    return interspersed


def num_range_repl(match):
    return f"{match.group(1)} through {match.group(2)}"


replacement_map = [
    [r"\$(\d*)", dollar_repl],
    [r"(\d{4})", date_repl],
    [r"([A-Z]{2,})(\w)?", acronym_repl],
    [r"(\d+)-(\d+)", num_range_repl],
    [r"(\d+)(st|nd|rd|th)", ordinal_repl],
]

simple_replacement_map = [
    ["…", "..."],
    ["‘", "'"],
    ["’", "'"],
    ["“", '"'],
    ["”", '"'],
    ["—", "--"],
    ["﹘", "_"],
]


def normalize_unicode(text):
    return unicodedata.normalize("NFKD", text)


def normalize_replacements(text):
    for (reg, repl) in replacement_map:
        text = re.sub(reg, repl, text)
    for (old, new) in simple_replacement_map:
        text = text.replace(old, new)
    return text


engine = inflect.engine()


def normalize_numbers(text):
    """
    Normalize a string of text by spelling out numbers.
    """
    slices = [(m.start(), m.end()) for m in re.finditer(num_pattern, text)]
    normalizations = [engine.number_to_words(text[slice(*s)]) for s in slices]
    normalized = text
    for s, norm in zip(slices, normalizations):
        normalized = normalized.replace(text[slice(*s)], norm, 1)
    return normalized


def normalize_titles(text):
    """
    Normalize a string of text by spelling out common titles/abbreviations
    """
    for pattern, replacement in titles.items():
        text = re.sub(pattern, replacement, text)
    return text


def troublesome_log(text, idx):
    """
    Log to file if a troublesome character is found.
    This lines likely will require manual trancription.
    """
    for c in troublesome:
        if c in text:
            with open(args.log_name, "a") as f:
                f.write("Troublesome character {c} on line {idx}", "\n")


def process_aud_sub(file_path):
    out = []
    with open(file_path, "r") as f:
        for line in f.readlines():
            s, e, content = line.split(None, 2)
            out.append((s, e, content.strip()))
    return out


def ensure_dirs(*dir_paths):
    for dir_path in dir_paths:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)


def safe_remove(*paths):
    for path in paths:
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)


def normalize(text):
    norm_funcs = [
        normalize_unicode,
        normalize_replacements,
        normalize_numbers,
        normalize_titles,
    ]

    for func in norm_funcs:
        text = func(text)
    return text


def create_csv_writer(file):
    return csv.writer(
        file, delimiter="|", quoting=csv.QUOTE_MINIMAL, lineterminator="\n"
    )


def run(input_dir, output_dir):

    safe_remove(output_dir)

    wavs_dir = pt.join(output_dir, "wavs")
    ensure_dirs(input_dir, output_dir, wavs_dir)
    csvfile = open(pt.join(output_dir, "metadata.csv"), "w", newline="")
    norm_csvfile = open(pt.join(output_dir, "metadata_norm_only.csv"), "w", newline="")
    writer = create_csv_writer(csvfile)
    norm_writer = create_csv_writer(norm_csvfile)
    files = os.listdir(input_dir)
    for file in files:
        if not file.endswith("wav"):
            continue

        name = file[:-4]
        filepath = pt.join(input_dir, file)
        subpath = pt.join(input_dir, name + ".aud")
        subs = process_aud_sub(subpath)
        # audio = AudioSegment.from_wav(file)
        tmp_wav_path = "tmp.wav"
        subprocess.run(
            [
                "sox",
                filepath,
                "-b",
                "16",
                tmp_wav_path,
                "rate",
                "22050",
                "channels",
                "1",
            ]
        )
        for idx, (s, e, text) in enumerate(subs):
            clip_output_path = pt.join(wavs_dir, f"{name}_{idx}.wav")
            print(f"Processing  {clip_output_path} - {s} -> {e}")
            # clip = audio[s:e]
            # clip.export(tmp_wav_path, format="wav")

            subprocess.run(
                [
                    "sox",
                    tmp_wav_path,
                    clip_output_path,
                    "trim",
                    s,
                    "=" + e,
                ]
            )
            ntext = normalize(text)
            writer.writerow([clip_output_path, text, ntext])
            norm_writer.writerow([clip_output_path, ntext])
        safe_remove(tmp_wav_path)
    csvfile.close()


def build_parser():
    """
    Creates an argparse parser
    """
    parser = argparse.ArgumentParser(
        description="Segment .wav files according to a provided .srt closed caption file",
        prog="srt-parse",
    )

    parser.add_argument(
        "input_dir", type=str, help="Dir of .wav and .srt files to be processed"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Directory for processed files to be saved to",
        default="out",
    )
    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    run(args.input_dir, args.output_dir)
