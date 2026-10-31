"""Small extractive summarizer (word-frequency sentence scoring), no external models needed."""
import re
from collections import Counter

STOPWORDS = set("""
a about above after again against all am an and any are as at be because been before being below
between both but by can could did do does doing down during each few for from further had has have
having he her here hers herself him himself his how i if in into is it its itself just me more most
my myself no nor not now of off on once only or other our ours ourselves out over own said same she
should so some such than that the their theirs them themselves then there these they this those
through to too under until up very was we were what when where which while who whom why will with
would you your yours yourself yourselves also its it's one new like says say
""".split())


def summarize(text, max_sentences=4):
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.split()) > 5]
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    words = [w for w in re.findall(r"[a-z']+", text.lower()) if w not in STOPWORDS and len(w) > 2]
    freq = Counter(words)
    if not freq:
        return " ".join(sentences[:max_sentences])
    top = max(freq.values())

    def score(sentence):
        tokens = [w for w in re.findall(r"[a-z']+", sentence.lower()) if w in freq]
        return sum(freq[w] / top for w in tokens) / (len(tokens) ** 0.5 or 1)

    best = sorted(range(len(sentences)), key=lambda i: score(sentences[i]), reverse=True)[:max_sentences]
    return " ".join(sentences[i] for i in sorted(best))
