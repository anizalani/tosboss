from typing import Dict, List
import spacy
import textstat
from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

class NLPProcessor:
    """Handles NLP processing for EULA/ToS documents"""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_md")
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        
    def analyze_text(self, text: str) -> Dict:
        """Perform comprehensive NLP analysis on text"""
        doc = self.nlp(text)
        
        return {
            'readability': {
                'flesch_reading_ease': textstat.flesch_reading_ease(text),
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
                'syllable_count': textstat.syllable_count(text)
            },
            'linguistics': {
                'sentence_count': len(list(doc.sents)),
                'word_count': len(doc),
                'unique_words': len(set([token.text.lower() for token in doc if token.is_alpha]))
            },
            'sentiment': self._analyze_sentiment(text),
            'key_phrases': self._extract_key_phrases(doc),
            'named_entities': self._extract_entities(doc)
        }
        
    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        try:
            result = self.sentiment_analyzer(text[:512])[0]
            return {
                'label': result['label'],
                'score': result['score']
            }
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return {'label': 'UNKNOWN', 'score': 0.0}
            
    def _extract_key_phrases(self, doc) -> List[str]:
        """Extract important phrases from text"""
        return [chunk.text for chunk in doc.noun_chunks
                if len(chunk.text.split()) > 1]
                
    def _extract_entities(self, doc) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        return entities