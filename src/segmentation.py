import re

def segment_results(alignment_result, original_lyrics, max_chars=40, max_duration=None):
    """
    Segments the alignment result into subtitles based on original lyrics and constraints.
    
    Args:
        alignment_result: The result object from stable-ts.
        original_lyrics (str): The original lyrics text.
        max_chars (int): Maximum characters per subtitle line.
        max_duration (float): Maximum duration in seconds per subtitle line (optional).
        
    Returns:
        list: A list of subtitle segments (start, end, text).
    """
    
    # 1. Provide a clean version of words for matching
    # Flatten all words from all segments
    all_words = []
    if hasattr(alignment_result, 'segments'):
        for segment in alignment_result.segments:
            all_words.extend(segment.words)
    else:
        # Fallback if structure is different (some versions return dict)
        pass # Assume standard object for now

    # 2. Split original lyrics into lines, processing punctuation as splitting points
    raw_lines = [line.strip() for line in original_lyrics.split('\n') if line.strip()]
    processed_lines = []
    
    for line in raw_lines:
        # Split by comma or dot if they are in the middle of the line
        # We want to keep the punctuation attached to the preceding word
        # "Hello, world." -> ["Hello,", "world."]
        parts = re.split(r'([,\.])', line)
        current_part = ""
        for i in range(0, len(parts) - 1, 2):
            content = parts[i]
            punctuation = parts[i+1]
            segment_str = (content + punctuation).strip()
            if segment_str:
                processed_lines.append(segment_str)
        
        # Handle the last part (or if no split happened)
        if len(parts) % 2 != 0:
            last_part = parts[-1].strip()
            if last_part:
                processed_lines.append(last_part)
    
    # Check if logic above missed simple lines without punctuation splits
    if not processed_lines and raw_lines:
         processed_lines = raw_lines

    subtitles = []
    word_index = 0
    total_words = len(all_words)
    
    def normalize(text):
        return re.sub(r'[^\w]', '', text.lower())

    for line_text in processed_lines:
        if word_index >= total_words:
            break
            
        # 3. Match words to this line
        current_line_matched_words = []
        target_norm = normalize(line_text)
        current_norm = ""
        
        while word_index < total_words:
            word_obj = all_words[word_index]
            word_val = word_obj.word.strip()
            word_norm = normalize(word_val)
            
            # Simple check: if current + word is longer than target, and target matches current prefix
            # check if we should stop.
            if len(current_norm) >= len(target_norm):
                 break
                 
            current_line_matched_words.append(word_obj)
            current_norm += word_norm
            word_index += 1
        
        # 4. Process the matched words for this line
        if not current_line_matched_words:
            continue
            
        full_text = " ".join([w.word.strip() for w in current_line_matched_words])
        
        # Ensure proper punctuation if original line had it (it likely does from our split)
        # But if we split "Hello, world" -> "Hello,", "world"
        # The alignment might just give "Hello" "world"
        # matches: "Hello" -> "Hello,". 
        # If the original line_text ended with punctuation, ensure full_text does too.
        if line_text[-1] in ',.;:?!' and full_text[-1] not in ',.;:?!':
            full_text += line_text[-1]
        elif not full_text.endswith(('.', '?', '!', ',', ';', ':')):
             full_text += "."
             
        # Check max_chars constraint.
        if len(full_text) > max_chars:
            buffer_words = []
            buffer_chars = 0
            
            for w in current_line_matched_words:
                w_len = len(w.word.strip()) + 1
                if buffer_chars + w_len > max_chars and buffer_words:
                    subtitles.append({
                        'start': buffer_words[0].start,
                        'end': buffer_words[-1].end,
                        'text': " ".join([bw.word.strip() for bw in buffer_words])
                    })
                    buffer_words = [w]
                    buffer_chars = w_len
                else:
                    buffer_words.append(w)
                    buffer_chars += w_len
            
            if buffer_words:
                 final_sub_text = " ".join([bw.word.strip() for bw in buffer_words])
                 if final_sub_text.strip() == full_text.split()[-1].strip().rstrip('.,;?!') or \
                    word_index >= total_words:
                     if not final_sub_text[-1] in ',.;:?!':
                         final_sub_text += "."
                         
                 subtitles.append({
                    'start': buffer_words[0].start,
                    'end': buffer_words[-1].end,
                    'text': final_sub_text
                })
        else:
            subtitles.append({
                'start': current_line_matched_words[0].start,
                'end': current_line_matched_words[-1].end,
                'text': full_text
            })

    # 5. Post-processing: Merge short lines / split punctuation parts
    merged_subtitles = []
    if subtitles:
        # Initial pass to handle punctuation splits that are too short
        # We look at the subtitles and see if we can merge them back
        
        # Helper to decide if we should merge
        def should_merge(prev, current, max_chars):
             # 1. Punctuation split check
             # If prev ends with punctuation that triggered a split (comma, dot)
             # And combined length <= max_chars
             
             # Also cover the "really short line" case (word_count <= 2) even if it exceeds max_chars slightly?
             # User said: "nếu một dòng chỉ có một (hoặc 2) từ thì cho phép gộp với dòng trước đó (bất chấp độ dài tối đa)"
             # User also said: "nếu 2 câu gốc được ngăn cách bởi dấu "," hoặc dấu "." mà khi ghép lại có độ dài ngắn hơn độ dài mong muốn thì vẫn ghép vào"
             
             prev_text = prev['text'].strip()
             current_text = current['text'].strip()
             combined_len = len(prev_text) + 1 + len(current_text)
             word_count = len(current_text.split())
             
             # Rule A: Very short line (<=2 words) -> Merge ALWAYS (User request)
             if word_count <= 2:
                 return True
                 
             # Rule B: Punctuation split -> Merge if fits max_chars
             # We assume these segments came from the same original context or are sequential
             if combined_len <= max_chars:
                 return True
                 
             return False

        merged_subtitles.append(subtitles[0])
        
        for i in range(1, len(subtitles)):
            current = subtitles[i]
            prev = merged_subtitles[-1]
            
            if should_merge(prev, current, max_chars):
                # Merge
                prev['end'] = current['end']
                
                prev_text = prev['text'].strip()
                current_text = current['text'].strip()
                
                # Handling punctuation/case when merging
                # If we merged because fit in max_chars (Rule B), we might want to keep the punctuation.
                # "Hello," + "world." -> "Hello, world."
                
                # If we merged because Rule A (short line), we might want to check the dot.
                # "Hello." + "There." (There is short) -> "Hello. There."
                
                # Special check for the "lower case continuation" logic
                if current_text and current_text[0].islower() and prev_text.endswith('.'):
                     prev_text = prev_text[:-1]

                prev['text'] = prev_text + " " + current_text
            else:
                merged_subtitles.append(current)

    return merged_subtitles

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
