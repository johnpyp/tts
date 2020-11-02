from os import path as pt
import os
import shutil

AUDIO_EXTS = [".opus", ".mp3", ".webm", ".wav"]


def safe_remove(*paths):
    for path in paths:
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)


def is_audio_path(path):
    for ext in AUDIO_EXTS:
        if path.endswith(ext):
            return True
    return False


def audio_gen_paths(path):
    ap = pt.normpath(path)
    base = pt.basename(ap)
    ext = get_audio_ext(ap)
    assert pt.exists(ap), "Expected audio path to exist"
    return ap, strip_audio_ext(ap), base, strip_audio_ext(base), ext


def strip(string, end_string):
    if string.end_string(end_string):
        return string[: -(len(end_string))]
    return string


def ensure_dirs(*dir_paths):
    for dir_path in dir_paths:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)


def string_to_ms(string):
    ftr = [3600000, 60000, 1000, 1]
    ms = sum(
        [a * b for a, b in zip(ftr, map(int, string.replace(".", ":").split(":")))]
    )
    return ms


def strip_audio_ext(string):
    for ext in AUDIO_EXTS:
        if string.endswith(ext):
            return strip(string, ext)
    raise Exception("Bad audio file extension")


def get_audio_ext(string):
    for ext in AUDIO_EXTS:
        if string.endswith(ext):
            return ext
    raise Exception("Bad audio file extension")
