# ConvertSubtitles

This project processes video subtitles, translates them using Google Translate API, and generates audio clips using ChatterboxTTS. It also splices the audio clips together to create a complete audio file.

## Features
- Extract subtitles and audio from video files.
- Translate subtitles from English to Italian.
- Generate audio clips for subtitles using ChatterboxTTS.
- Splice audio clips into a single audio file.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/convert_subtitles.git
   cd convert_subtitles
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure `ffmpeg` is installed and available in your system's PATH.

## Usage

### Translate Subtitles
Run the `translate_srt.py` script to translate `.srt` subtitle files:
```bash
python translate_srt.py --base-path <path_to_subtitles> --out-path <path_to_save_translated_subtitles>
```

### Process Video

```bash
python video_to_audio.py --video example.mp4 --temp-dir ./temp --override
```

This will extract subtitles and audio from `example.mp4`, generate audio clips, and save the final audio file.

## Requirements
- Python 3.8+
- `ffmpeg` installed
- CUDA-enabled GPU for ChatterboxTTS (optional but recommended)

## License
This project is licensed under the MIT License.
