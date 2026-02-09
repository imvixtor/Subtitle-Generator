import argparse
import os
from src.alignment import align_audio_lyrics
from src.segmentation import segment_results, save_to_srt

def main():
    parser = argparse.ArgumentParser(description="Forced Alignment and Subtitle Generator")
    parser.add_argument("--audio", required=True, help="Path to the audio file")
    parser.add_argument("--lyrics", required=True, help="Path to the lyrics text file")
    parser.add_argument("--output", required=True, help="Path to audio output SRT file")
    parser.add_argument("--max_len", type=int, default=40, help="Maximum characters per line")
    parser.add_argument("--language", default="vi", help="Language code (default: vi)")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large"], 
                        help="Whisper model size (default: base)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audio):
        print(f"Error: Audio file not found: {args.audio}")
        return
        
    if not os.path.exists(args.lyrics):
        print(f"Error: Lyrics file not found: {args.lyrics}")
        return
        
    # Validate lyrics file extension
    if not args.lyrics.lower().endswith(('.txt', '.lrc', '.srt')):
        print(f"Warning: Lyrics file '{args.lyrics}' does not have a standard text extension (.txt, .lrc, .srt).")
        print("Please ensure this is a text file containing the lyrics.")

    # Read lyrics
    try:
        with open(args.lyrics, 'r', encoding='utf-8') as f:
            lyrics_text = f.read()
    except UnicodeDecodeError:
        print(f"Error: Could not read lyrics file '{args.lyrics}'.")
        print("It appears to be a binary file or not UTF-8 encoded.")
        print("Please provide a valid text file (e.g. .txt) containing the lyrics.")
        return
    except Exception as e:
        print(f"Error reading lyrics file: {e}")
        return
        
    print(f"Aligning audio: {args.audio} with lyrics using model '{args.model}'...")
    try:
        result = align_audio_lyrics(args.audio, lyrics_text, language=args.language, model_name=args.model)
    except Exception as e:
        print(f"Error during alignment: {e}")
        return
        
    print("Alignment complete. Segmenting...")
    subtitles = segment_results(result, lyrics_text, max_chars=args.max_len)
    
    print(f"Saving to {args.output}...")
    save_to_srt(subtitles, args.output)
    print("Done!")

if __name__ == "__main__":
    main()
