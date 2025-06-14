from typing import Dict, List
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import logging

logger = logging.getLogger(__name__)

class DocumentClassifier:
    """Classifies documents and clauses into categories"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=10000)
        self.classifier = MultinomialNB()
        self.categories = [
            'privacy_policy',
            'terms_of_service',
            'eula',
            'data_processing_agreement',
            'acceptable_use_policy'
        ]
        
    def train(self, texts: List[str], labels: List[str]):
        """Train the classifier with example documents"""
        try:
            X = self.vectorizer.fit_transform(texts)
            self.classifier.fit(X, labels)
            return True
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            return False
            
    def classify_document(self, text: str) -> Dict:
        """Classify a document and return probabilities"""
        try:
            X = self.vectorizer.transform([text])
            probs = self.classifier.predict_proba(X)[0]
            
            return {
                'predicted_category': self.categories[probs.argmax()],
                'confidence': float(probs.max()),
                'probabilities': {
                    category: float(prob)
                    for category, prob in zip(self.categories, probs)
                }
            }
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            return {
                'predicted_category': 'unknown',
                'confidence': 0.0,
                'probabilities': {}
            }