"""Translate .srt subtitles from English to Italian using Google Translate API."""

import argparse
import os
from googletrans import Translator

translator = Translator()

parser = argparse.ArgumentParser(description="Convert Genius subtitles to audio files using ChatterboxTTS.")
parser.add_argument("--base-path", type=str, help="The path where the subtitle files are.")
parser.add_argument("--out-path", type=str, help="The path where the translated subtitles should be saved to.")
args = parser.parse_args()


for file in os.listdir(args.base_path):
    if file.startswith("it"):
        continue
    if file.endswith(".srt"):
        path_to_new_file = os.path.join(args.out_path, "it-" + file)
        path_to_file = os.path.join(args.base_path, file)
        if os.path.exists(path_to_new_file):
            continue
        with open(path_to_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        print("now working on " + file)
        for i, line in enumerate(lines):
            if len(line) == 1 or ("-->" in line):
                continue
            translated = translator.translate(line, src='en', dest='it')
            lines[i] = translated.text + "\n"
        with open(path_to_new_file, "w", encoding="utf-8") as f:
            f.writelines(lines)
