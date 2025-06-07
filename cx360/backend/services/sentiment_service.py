from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize the analyzer globally or within a class structure if preferred
analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str) -> dict:
    """
    Analyzes the sentiment of a given text.

    Args:
        text: The input string to analyze.

    Returns:
        A dictionary containing the sentiment label ('positive', 'negative', 'neutral')
        and the compound sentiment score.
    """
    if not text or not isinstance(text, str):
        # Return a default neutral sentiment for empty or invalid input
        return {"label": "neutral", "score": 0.0}

    # Polarity scores returns a dict: {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}
    vs = analyzer.polarity_scores(text)
    compound_score = vs['compound']

    if compound_score >= 0.05:
        label = "positive"
    elif compound_score <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return {"label": label, "score": compound_score}

# Example usage:
# if __name__ == '__main__':
#     print(analyze_sentiment("VADER is smart, handsome, and funny."))  # positive
#     print(analyze_sentiment("VADER is not smart, handsome, nor funny.")) # negative
#     print(analyze_sentiment("This is a neutral sentence.")) # neutral
#     print(analyze_sentiment("The movie was meh.")) # neutral (can be subjective)
#     print(analyze_sentiment(None)) # neutral (handles None)
#     print(analyze_sentiment("")) # neutral (handles empty string)
#     print(analyze_sentiment("I love this! It's amazing and wonderful.")) # positive
#     print(analyze_sentiment("I hate this. It's awful and terrible.")) # negative
#     print(analyze_sentiment("The food was okay, but the service was slow.")) # can be mixed
```
