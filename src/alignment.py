import stable_whisper

def align_audio_lyrics(audio_path, lyrics_text, language='vi'):
    """
    Aligns audio with lyrics using stable-ts.
    
    Args:
        audio_path (str): Path to the audio file.
        lyrics_text (str): The lyrics text to align.
        language (str): Language code (default 'vi' for Vietnamese).
        
    Returns:
        stable_whisper.result.WhisperResult: The alignment result object.
    """
    # Load the model. 'base' is usually a good trade-off for speed/accuracy.
    # 'small' or 'medium' can be used if higher accuracy is needed.
    model = stable_whisper.load_model('base')
    
    # Perform alignment
    # We use the 'text' parameter to guide the alignment with the provided lyrics.
    result = model.align(
        audio_path, 
        lyrics_text, 
        language=language
    )
    
    return result
