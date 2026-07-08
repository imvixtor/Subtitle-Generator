
import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import MagicMock
from src.segmentation import segment_results, subtitles_to_ass_string

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
        
        subtitles = segment_results(mock_result, "Hello world today", max_chars=12)
        
        self.assertEqual(len(subtitles), 2)
        self.assertEqual(subtitles[0]['text'], "Hello world")
        self.assertEqual(subtitles[0]['start'], 0.0)
        self.assertEqual(subtitles[0]['end'], 2.0)
        
        # Verify word-level timings are present
        self.assertEqual(len(subtitles[0]['words']), 2)
        self.assertEqual(subtitles[0]['words'][0]['text'], "Hello")
        self.assertEqual(subtitles[0]['words'][0]['start'], 0.0)
        self.assertEqual(subtitles[0]['words'][0]['end'], 1.0)
        self.assertEqual(subtitles[0]['words'][1]['text'], "world")
        self.assertEqual(subtitles[0]['words'][1]['start'], 1.0)
        self.assertEqual(subtitles[0]['words'][1]['end'], 2.0)
        
        self.assertEqual(subtitles[1]['text'], "today")
        self.assertEqual(subtitles[1]['start'], 2.0)
        self.assertEqual(subtitles[1]['end'], 3.0)
        
        self.assertEqual(len(subtitles[1]['words']), 1)
        self.assertEqual(subtitles[1]['words'][0]['text'], "today")
        self.assertEqual(subtitles[1]['words'][0]['start'], 2.0)
        self.assertEqual(subtitles[1]['words'][0]['end'], 3.0)

    def test_ass_formatting(self):
        subs = [
            {
                'start': 1.25, 
                'end': 4.88, 
                'text': 'Hello world',
                'words': [
                    {'start': 1.25, 'end': 2.0, 'text': 'Hello'},
                    {'start': 2.5, 'end': 4.88, 'text': 'world'}
                ]
            },
            {
                'start': 75.0, 
                'end': 80.5, 
                'text': 'Line 2\nWith newline'
            }
        ]
        
        ass_str = subtitles_to_ass_string(subs)
        
        # Check standard headers
        self.assertIn("[Script Info]", ass_str)
        self.assertIn("[V4+ Styles]", ass_str)
        self.assertIn("[Events]", ass_str)
        
        # Check Dialogue lines and timing formats
        # Hello duration: 2.0 - 1.25 = 0.75s -> {\k75}
        # Gap: 2.5 - 2.0 = 0.50s -> {\k50}
        # world duration: 4.88 - 2.5 = 2.38s -> {\k238}
        self.assertIn("Dialogue: 0,0:00:01.25,0:00:04.88,Default,,0,0,0,,{\\k75}Hello {\\k50}{\\k238}world", ass_str)
        
        # 75.0 -> 0:01:15.00
        # 80.5 -> 0:01:20.50
        # Without words, falls back to text with \N
        self.assertIn("Dialogue: 0,0:01:15.00,0:01:20.50,Default,,0,0,0,,Line 2\\NWith newline", ass_str)

if __name__ == '__main__':
    unittest.main()

