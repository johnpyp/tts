## Pre Poggers (preprocessing script)

Requirements:

- Python 3.7 recommended

pip install -r requirements.txt

Usage:

Create a source directory with media in the format:

```
source/media.opus
source/media.srt
source/media.cut.txt (optional)
```

\*.cut.txt files should have lines in in the format:

```
hh:mm:ss.ms -> hh:mm:ss.ms
hh:mm:ss.ms -> hh:mm:ss.ms
hh:mm:ss.ms -> hh:mm:ss.ms

start -> hh:mm:ss.ms
hh:mm:ss.ms -> end
```

with "start" and "end" being special keywords for convenience.

NOTE: the ms section can be excluded if not needed.

#### Example

This represents segment of the audio file to not include in the final sample,
for example if you have a 30m audio file this .cut.txt would exclude the first 5 minutes and the last 5 minutes:

```
start -> 00:05:00
00:25:00 -> end
```

Then, use the script like this:

`python scripts/pre_poggers.py --source_dir my_source_dir --output_dir my_output_dir`

which will read all the files in the source dir and convert it to an LJSpeech dataset in the output dir.

#### Args:

**--source_dir**: directory with the source files
default: source

**--output_dir**: directory for the output files, anything in it will be deleted and overwritten
default: output

**--include_path**: include the relative to output-dir path of files, for example `output/wavs/filename_1.wav` instead of the standard `filename`
default: False

**--metadata_filename**: alternative metadata filename
default: metadata.csv
