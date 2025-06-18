"""Make audio clips from video subtitles using ChatterboxTTS. Then splice them together."""

import os
from pathlib import Path
from pydub import AudioSegment
from pydub.effects import speedup
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
import argparse

from tqdm import tqdm


def splice_audio(audio_clips, timestamps, output_path):
    
    """
    Splices together a sequence of audio clips at the specified timestamps.

    :param audio_clips: List of file paths to the audio clips.
    :param timestamps: List of tuples (start, stop) in milliseconds for each clip.
    :param output_path: Path to save the final spliced audio.
    """
    final_audio = AudioSegment.silent(duration=timestamps[0][0])

    for clip_path, (start, stop) in tqdm(zip(audio_clips, timestamps), total=len(timestamps), desc="Splicing audio clips"):
        audio = AudioSegment.from_file(clip_path)

        if int(final_audio.duration_seconds * 1000) < start:
            final_audio += AudioSegment.silent(duration=start - int(final_audio.duration_seconds * 1000))

        final_audio += audio

    final_audio.export(output_path)
    print(f"Spliced audio saved to {output_path}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert Genius subtitles to audio files using ChatterboxTTS.")
    parser.add_argument("--video", type=str, help="The path to the video to process.")
    parser.add_argument("--temp-dir", type=str, default="./temp", help="Temporary directory for processing audio clips.")
    parser.add_argument("--override", action="store_true", help="Overriding extracted audio and subtitles.")
    args = parser.parse_args()

    print("Processing video:", args.video)

    original_audio_path = os.path.join(args.temp_dir, 'original.mp3')
    if not os.path.exists(original_audio_path) or args.override:
        # Call ffmeg process to extract mp3 from args.video
        result = os.system(f"ffmpeg -y -i \"{args.video}\" -q:a 0 -map a \"{original_audio_path}\"")
        if result != 0:
            exit(f"Error extracting audio from video: {args.video}")
    subtitle_file = os.path.join(args.temp_dir, 'subs.ass')
    if not os.path.exists(subtitle_file) or args.override:
        # Call ffmpeg to extract subtitles from args.video
        os.system(f"ffmpeg -y -i \"{args.video}\" -map 0:s:0 \"{subtitle_file}\"")
        if result != 0:
            exit(f"Error extracting subtititles from video: {args.video}")

    this_audio_start, this_audio_end = 0,0 

    model = ChatterboxTTS.from_pretrained(device="cuda")

    # Load the audio file
    audio = AudioSegment.from_file(os.path.join(args.temp_dir, "original.mp3"))

    audio_clips = []
    timestamps = []
    with open(subtitle_file, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("Dialogue:"):
            dialogue = ",".join(line.split(",")[9:])
            subtitle_type = line.split(",")[3]
            if subtitle_type != "Default":
                continue
            dialogue = "".join([segment.split("}")[-1] for segment in dialogue.split("{")])

            t1, t2 = line.split(",")[1:3]
            time1, millisecond1 = t1.split(".")
            hour1, minute1, second1 = map(int, time1.split(":"))
            time2, millisecond2 = t2.split(".")
            hour2, minute2, second2 = map(int, time2.split(":"))
            this_audio_start = (hour1 * 3600 + minute1 * 60 + second1) * 1000 + int(millisecond1)
            this_audio_end = (hour2 * 3600 + minute2 * 60 + second2) * 1000 + int(millisecond2)
            timestamps.append((this_audio_start, this_audio_end))
            clip_filename = f"{subtitle_file.split('.ass')[0]}-{this_audio_start}-{this_audio_end}.wav"
            audio_clips.append(clip_filename)

            if not os.path.exists(clip_filename):
                # Extract the desired clip
                clip = audio[this_audio_start:this_audio_end]

                # Export the new clip
                clip.export(os.path.join(args.temp_dir, "original_clip.mp3"), format="mp3")
                try: 
                    print(f"processing: {dialogue}")
                    wav = model.generate(dialogue, audio_prompt_path=os.path.join(args.temp_dir, "original_clip.mp3"))
                    ta.save(clip_filename, wav, model.sr)
                except Exception as e:
                    if "cuda" in str(e).lower():
                        exit(1)
                    # TODO better dealing with exceptions
                    print(f"Can't figure out how to deal with error {e}, skipping {dialogue} and exporting originnal clip")
                    clip.export(clip_filename)
                    exit(1)

    # sort audio clips and timestamps based on start time
    output_path = args.video.split(".")[0] + ".mp3"
    print(f"processing done, saving to {output_path}")
    splice_audio(audio_clips, timestamps, output_path)
    # Clean up individual audio files
    for temp_file in os.listdir(args.temp_dir):
        if os.path.exists(os.path.join(args.temp_dir, temp_file)):
            os.remove(os.path.join(args.temp_dir, temp_file))
