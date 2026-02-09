def segment_results(alignment_result, max_chars=40, max_duration=None):
    """
    Segments the alignment result into subtitles based on constraints.
    
    Args:
        alignment_result: The result object from stable-ts.
        max_chars (int): Maximum characters per subtitle line.
        max_duration (float): Maximum duration in seconds per subtitle line (optional).
        
    Returns:
        list: A list of subtitle segments (start, end, text).
    """
    # alignment_result is a stable_whisper.result.WhisperResult object
    # It contains segments, and each segment contains words.
    # Since we used align(), the structure might slightly differ or needs flattening first.
    
    # Let's flatten all words from all segments to re-segment them ourselves
    all_words = []
    for segment in alignment_result.segments:
        all_words.extend(segment.words)
        
    subtitles = []
    current_line_words = []
    current_line_chars = 0
    
    for i, word in enumerate(all_words):
        word_text = word.word.strip()
        word_len = len(word_text) + 1 # +1 for space
        
        # Check if adding this word exceeds max_chars
        if current_line_words and (current_line_chars + word_len > max_chars):
            # Finalize current line
            start_time = current_line_words[0].start
            end_time = current_line_words[-1].end
            text = " ".join([w.word.strip() for w in current_line_words])
            subtitles.append({
                'start': start_time,
                'end': end_time,
                'text': text
            })
            
            # Start new line
            current_line_words = [word]
            current_line_chars = word_len
        else:
            current_line_words.append(word)
            current_line_chars += word_len
            
        # Optional: Check for natural pauses (if word has a long silence after it)
        # This is heuristics-based. For now, we stick to length constraints primarily
        # unless a major gap is detected.
        
    # Append the last line if any
    if current_line_words:
        start_time = current_line_words[0].start
        end_time = current_line_words[-1].end
        text = " ".join([w.word.strip() for w in current_line_words])
        subtitles.append({
            'start': start_time,
            'end': end_time,
            'text': text
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
