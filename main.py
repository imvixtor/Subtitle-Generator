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
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audio):
        print(f"Error: Audio file not found: {args.audio}")
        return
        
    if not os.path.exists(args.lyrics):
        print(f"Error: Lyrics file not found: {args.lyrics}")
        return
        
    # Read lyrics
    with open(args.lyrics, 'r', encoding='utf-8') as f:
        lyrics_text = f.read()
        
    print(f"Aligning audio: {args.audio} with lyrics...")
    try:
        result = align_audio_lyrics(args.audio, lyrics_text, language=args.language)
    except Exception as e:
        print(f"Error during alignment: {e}")
        return
        
    print("Alignment complete. Segmenting...")
    subtitles = segment_results(result, max_chars=args.max_len)
    
    print(f"Saving to {args.output}...")
    save_to_srt(subtitles, args.output)
    print("Done!")

if __name__ == "__main__":
    main()
