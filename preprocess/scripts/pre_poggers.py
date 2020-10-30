import csv
import os
import shutil
import subprocess
import webvtt
import srt
from datetime import timedelta
from glob import glob
from os import path as pt

from pydub import AudioSegment

AUDIO_EXTS = [".opus", ".webm", ".mp3"]
SUBTITLE_EXT = ".srt"  # Do not change
IGNORE_EXT = ".cut.txt"  # Do not change


def string_to_ms(string):
    ftr = [3600000, 60000, 1000, 1]
    ms = sum(
        [a * b for a, b in zip(ftr, map(int, string.replace(".", ":").split(":")))]
    )
    return ms


def process_cuts(cuts_path):
    if not pt.exists(cuts_path):
        return []
    with open(cuts_path, "r") as f:
        lines = f.readlines()
    res = []
    for line in lines:
        start, end = line.split("->")
        start = start.strip()
        end = end.strip()
        start = 0 if start == "start" else string_to_ms(start)
        end = 100000000 if end == "end" else string_to_ms(end)
        res.append([start, end])
    return res


def gen_subs(subtitle_path):
    if not pt.exists(subtitle_path):
        return []
    with open(subtitle_path) as f:
        raw = f.read()
    subs = srt.parse(raw)
    build_line = ""
    build_start = 0
    build_end = 0
    for sub in subs:

        ms1 = timedelta(milliseconds=1)
        start, end = sub.start / ms1, sub.end / ms1

        build_duration = build_end - build_start

        if build_duration > 5000:
            yield (build_line, build_start, build_end)
            build_line = ""

        if build_line == "":
            build_line = sub.content
            build_start = start
        else:
            build_line += " " + sub.content
        build_end = end


def create_dirs(*dir_paths):
    for dir_path in dir_paths:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)


def strip_audio(string):
    for ext in AUDIO_EXTS:
        if string.endswith(ext):
            return string.rstrip(ext)
    raise Exception("Bad file extension: " + ext)


def preprocess_zeta(source_dir, output_dir, include_path, metadata_filename):
    source_dir = pt.normpath(source_dir)
    output_dir = pt.normpath(output_dir)

    wavs_dir = pt.join(output_dir, "wavs")
    metadata_csv_path = pt.join(output_dir, metadata_filename)

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    create_dirs(source_dir, output_dir, wavs_dir)
    audio_paths = []
    for ext in AUDIO_EXTS:
        audio_paths.extend(glob(pt.join(source_dir, "*" + ext)))
    rows = []
    for ap in audio_paths:
        apb = pt.basename(ap)
        stripped = strip_audio(ap)
        stripped_apb = strip_audio(apb)
        big_wav_path = stripped + ".wav"

        sub_path = stripped + SUBTITLE_EXT
        cut_path = stripped + IGNORE_EXT

        if not pt.exists(sub_path):
            continue
        idx = 1
        cuts = process_cuts(cut_path)
        if not pt.exists(big_wav_path):
            subprocess.run(["ffmpeg", "-i", ap, big_wav_path])
            subprocess.run(
                [
                    "sox",
                    big_wav_path,
                    "-b",
                    "16",
                    "tmp.wav",
                    "rate",
                    "22050",
                    "channels",
                    "1",
                ]
            )
            os.remove(big_wav_path)
            os.rename("tmp.wav", big_wav_path)

        print(sub_path)
        for (line, start, end) in gen_subs(sub_path):
            in_cut = False
            for (cut_start, cut_end) in cuts:
                if cut_start < end < cut_end or cut_start < start < cut_end:
                    in_cut = True
                    break

            if not in_cut and 7000 > (end - start) > 100:
                if "[" in line and "]" in line:
                    continue
                p = pt.join(wavs_dir, stripped_apb + "_" + str(idx) + ".wav")
                print(p)
                subprocess.run(
                    [
                        "sox",
                        big_wav_path,
                        p,
                        "trim",
                        str(start / 1000),
                        "=" + str(end / 1000),
                        "silence",
                        "1",
                        "0.1",
                        "0.5%",
                        "reverse",
                        "silence",
                        "1",
                        "0.1",
                        "0.5%",
                        "reverse",
                    ]
                )
                if not pt.exists(p):
                    raise Exception("Clip wasn't made??")
                sound = AudioSegment.from_file(p)
                if len(sound) < 2000:
                    os.remove(p)
                    continue
                rows.append(
                    [p if include_path else pt.splitext(pt.basename(p))[0], line, line]
                )
                idx += 1
                print("Finished " + p)
    with open(metadata_csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter="|", quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--source_dir", default="source", type=str, help="Source dir")
    parser.add_argument("--output_dir", default="output", type=str, help="Output dir")
    parser.add_argument(
        "--include_path",
        default=False,
        type=bool,
        help="Include relative path in the metadata.csv (non-standard), rather than just filename",
    )
    parser.add_argument(
        "--metadata_filename",
        default="metadata.csv",
        type=str,
        help="The filename of the metadata csv file",
    )
    args = parser.parse_args()
    preprocess_zeta(
        args.source_dir, args.output_dir, args.include_path, args.metadata_filename
    )
