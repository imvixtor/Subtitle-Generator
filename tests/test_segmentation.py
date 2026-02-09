
import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import MagicMock
from src.segmentation import segment_results

class TestSegmentation(unittest.TestCase):
    def test_segmentation_logic(self):
        # Mocking stable_whisper result structure
        # Result -> segments -> words -> WordTiming(start, end, word)
        
        # Create a mock word class or structure
        class WordTiming:
            def __init__(self, start, end, word):
                self.start = start
                self.end = end
                self.word = word
                
        # Mock result object
        mock_result = MagicMock()
        
        # Scenario: 3 words. "Hello", "world", "today".
        # Lengths: 5, 5, 5. With spaces: 6, 6, 5 (+1 for last if we count, but usually we just count chars).
        # Total line length if joined: "Hello world today" = 17 chars.
        
        # Let's say max_len = 12.
        # "Hello world" = 11 chars. Fits.
        # "today" = 5 chars. Wont fit with "Hello world" (11+1+5 = 17 > 12).
        
        words = [
            WordTiming(0.0, 1.0, "Hello"),
            WordTiming(1.0, 2.0, "world"),
            WordTiming(2.0, 3.0, "today")
        ]
        
        mock_segment = MagicMock()
        mock_segment.words = words
        mock_result.segments = [mock_segment]
        
        subtitles = segment_results(mock_result, max_chars=12)
        
        self.assertEqual(len(subtitles), 2)
        self.assertEqual(subtitles[0]['text'], "Hello world")
        self.assertEqual(subtitles[0]['start'], 0.0)
        self.assertEqual(subtitles[0]['end'], 2.0)
        
        self.assertEqual(subtitles[1]['text'], "today")
        self.assertEqual(subtitles[1]['start'], 2.0)
        self.assertEqual(subtitles[1]['end'], 3.0)

if __name__ == '__main__':
    unittest.main()
