import os

AUDIO_EXTS = [".opus", ".mp3", ".webm", ".wav"]


def create_dirs(*dir_paths):
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
            return string.rstrip(ext)
    raise Exception("Bad audio file extension: " + ext)
