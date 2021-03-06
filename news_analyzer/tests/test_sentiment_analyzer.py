"""
Unit Tests for Sentiment Analyzer
"""
import unittest
import sys
sys.path.append('news_analyzer/libraries')

# pylint: disable=wrong-import-position
import sentiment_analyzer # noqa


# Define a class in which the tests will run
class SentimentAnalyzerTest(unittest.TestCase):
    """
    Unit TestCase Class for Sentiment Analyzer
    """

    def test_smoke(self):
        """
        Basic Smoke Test

        Args:
            self (object): Reference to the class

        Returns:
            null
        """
        my_sentiment = sentiment_analyzer.get_sentiment("This is a sentence.")
        self.assertTrue(my_sentiment is not None)

    def test_positive_only(self):
        """
        Test a positive sentence

        Args:
            self (object): Reference to the class

        Returns:
            null
        """
        my_sentiment = sentiment_analyzer.get_sentiment("I am happy.")
        self.assertTrue((my_sentiment["Overall_Sentiment"] == 'Positive') &
                        (my_sentiment["Positive_Sentences"] == 1) &
                        (my_sentiment["Negative_Sentences"] == 0) &
                        (my_sentiment["Neutral_Sentences"] == 0) &
                        (my_sentiment["Total_Sentences"] == 1))

    def test_negative_only(self):
        """
        Test a negative sentence

        Args:
            self (object): Reference to the class

        Returns:
            null
        """
        my_sentiment = sentiment_analyzer.get_sentiment("I am really sad.")
        self.assertTrue((my_sentiment["Overall_Sentiment"] == 'Negative') &
                        (my_sentiment["Positive_Sentences"] == 0) &
                        (my_sentiment["Negative_Sentences"] == 1) &
                        (my_sentiment["Neutral_Sentences"] == 0) &
                        (my_sentiment["Total_Sentences"] == 1))

    def test_neutral_only(self):
        """
        Test a neutral sentence

        Args:
            self (object): Reference to the class

        Returns:
            null
        """
        my_sentiment = sentiment_analyzer.get_sentiment("The sky is blue.")
        self.assertTrue((my_sentiment["Overall_Sentiment"] == 'Neutral') &
                        (my_sentiment["Positive_Sentences"] == 0) &
                        (my_sentiment["Negative_Sentences"] == 0) &
                        (my_sentiment["Neutral_Sentences"] == 1) &
                        (my_sentiment["Total_Sentences"] == 1))

    def test_mixed_sentiments(self):
        """
        Test a text with positive, negative and neutral sentences.

        Args:
            self (object): Reference to the class

        Returns:
            null
        """
        my_sentiment = sentiment_analyzer.get_sentiment(
            "I am happy. I am sad. The sky is blue.")
        self.assertTrue((my_sentiment["Overall_Sentiment"] == 'Neutral') &
                        (my_sentiment["Positive_Sentences"] == 1) &
                        (my_sentiment["Negative_Sentences"] == 1) &
                        (my_sentiment["Neutral_Sentences"] == 1) &
                        (my_sentiment["Total_Sentences"] == 3))


if __name__ == '__main__':
    unittest.main()
