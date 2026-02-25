import re

def segment_results(alignment_result, original_lyrics, max_chars=30, max_duration=None):
    """
    Segments the alignment result into subtitles based on original lyrics and constraints.
    
    Respects the original line breaks from the lyrics file.
    Only splits lines that exceed max_chars at word boundaries.
    Does NOT add or remove any punctuation.
    
    Args:
        alignment_result: The result object from stable-ts.
        original_lyrics (str): The original lyrics text.
        max_chars (int): Maximum characters per subtitle line.
        max_duration (float): Maximum duration in seconds per subtitle line (optional).
        
    Returns:
        list: A list of subtitle segments (start, end, text).
    """
    
    # 1. Flatten all words from all segments
    all_words = []
    if hasattr(alignment_result, 'segments'):
        for segment in alignment_result.segments:
            all_words.extend(segment.words)

    # 2. Split original lyrics into lines, respecting the original line breaks
    # Keep each non-empty line exactly as-is (only strip leading/trailing whitespace)
    original_lines = [line.strip() for line in original_lyrics.split('\n') if line.strip()]

    subtitles = []
    word_index = 0
    total_words = len(all_words)
    
    def normalize(text):
        return re.sub(r'[^\w]', '', text.lower())

    for line_text in original_lines:
        if word_index >= total_words:
            break
            
        # 3. Match words from alignment to this original line
        current_line_matched_words = []
        target_norm = normalize(line_text)
        current_norm = ""
        
        while word_index < total_words:
            word_obj = all_words[word_index]
            word_val = word_obj.word.strip()
            word_norm = normalize(word_val)
            
            if len(current_norm) >= len(target_norm):
                 break
                 
            current_line_matched_words.append(word_obj)
            current_norm += word_norm
            word_index += 1
        
        # 4. Process the matched words for this line
        if not current_line_matched_words:
            continue
        
        # Use original line text as-is (preserving original punctuation)
        full_text = line_text
            
        # 5. If line exceeds max_chars, split at word boundaries
        if len(full_text) > max_chars:
            # Split the original line text into words for display
            line_words = full_text.split()
            # We need to distribute aligned word timings across the display words
            
            buffer_display = []
            buffer_aligned = []
            buffer_chars = 0
            aligned_idx = 0
            
            for display_word in line_words:
                w_len = len(display_word) + (1 if buffer_display else 0)
                
                if buffer_chars + w_len > max_chars and buffer_display:
                    # Flush current buffer as a subtitle
                    subtitles.append({
                        'start': buffer_aligned[0].start,
                        'end': buffer_aligned[-1].end,
                        'text': " ".join(buffer_display)
                    })
                    buffer_display = [display_word]
                    buffer_aligned = [current_line_matched_words[min(aligned_idx, len(current_line_matched_words) - 1)]]
                    buffer_chars = len(display_word)
                else:
                    buffer_display.append(display_word)
                    buffer_aligned.append(current_line_matched_words[min(aligned_idx, len(current_line_matched_words) - 1)])
                    buffer_chars += w_len
                
                aligned_idx += 1
            
            if buffer_display:
                subtitles.append({
                    'start': buffer_aligned[0].start,
                    'end': buffer_aligned[-1].end,
                    'text': " ".join(buffer_display)
                })
        else:
            subtitles.append({
                'start': current_line_matched_words[0].start,
                'end': current_line_matched_words[-1].end,
                'text': full_text
            })

    return subtitles

def save_to_srt(subtitles, output_path):
    """
    Saves subtitles to an SRT file.
    """
    def format_timestamp(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

    with open(output_path, 'w', encoding='utf-8') as f:
        for i, sub in enumerate(subtitles, 1):
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(sub['start'])} --> {format_timestamp(sub['end'])}\n")
            f.write(f"{sub['text']}\n\n")
