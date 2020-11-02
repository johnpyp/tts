import math
from shutil import copyfile
import sox
from glob import glob
import subprocess
from os import path as pt
import os
from utils import audio_gen_paths, is_audio_path
import mutagen


IBM_LANG = "en-US_BroadbandModel"
MAX_SIZE = 90_000_000


def to_wav(audio_path):
    ap, ap_stripped, _, _ = audio_gen_paths(audio_gen_paths)
    wav_path = ap_stripped + ".wav"
    retcode = subprocess.call(["ffmpeg", "-8", "-i", ap, wav_path])
    assert pt.exists(wav_path), "wav output should exist"
    assert retcode != 1, "ffmpeg should not error"
    return audio_gen_paths(wav_path)


def list_audio_files(source_dir):
    assert pt.isdir(source_dir)
    return filter(is_audio_path, glob(pt.join(source_dir, "*")))


def shrink_audio_files(processed_paths, target_dir):
    for ap, ap_stripped, base, base_stripped, ext in processed_paths:
        first_tmp_output = pt.join(target_dir, base_stripped + "_0" + ext)
        if pt.exists(first_tmp_output):
            continue
        duration = mutagen.File(ap).info.length
        size = pt.getsize(ap)
        div = size / MAX_SIZE
        if div <= 1:
            copyfile(ap, first_tmp_output)
            continue
        new_duration = math.ceil(duration / div) * 0.9

        start = 0
        i = 0
        while start < duration:
            tmp_output = pt.join(target_dir, base_stripped + "_" + i + ext)
            subprocess.call(
                ["ffmpeg", "-8", "-i", ap, "-ss", start, "-t", new_duration, tmp_output]
            )
            assert pt.exists(tmp_output), "next output should exist"
            assert pt.getsize(tmp_output) < MAX_SIZE
            i += 1
            start += new_duration


def pv2(source_dir, output_dir):
    source_dir = pt.normpath(source_dir)
    output_dir = pt.normpath(output_dir)
    tmp_dir = pt.join(output_dir, "tmp")
    audio_files = map(audio_gen_paths, list_audio_files(source_dir))
    shrink_audio_files(audio_files, tmp_dir)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=str, help="Source dir")
    parser.add_argument("output_dir", type=str, help="Output dir")
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
    parser.add_argument(
        "--ibm_key", required=True, type=str, help="IBM Cloud speech to text API key"
    )
    parser.add_argument(
        "--ibm_url", required=True, type=str, help="IBM Cloud speech to text url"
    )
    assert pt.exists(args.source_dir), "Expected source directory to exist"
    assert pt.exists(args.output_dir), "Expected output directory to exist"
    args = parser.parse_args()
