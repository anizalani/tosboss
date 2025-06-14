from typing import Dict, List, Tuple
import difflib
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)

class ChangeDetector:
    """Detects and analyzes changes between document versions"""
    
    def __init__(self):
        self.diff_matcher = difflib.SequenceMatcher(None)
        
    def detect_changes(self, old_text: str, new_text: str) -> Dict:
        """Analyze changes between two versions of text"""
        self.diff_matcher.set_seqs(old_text, new_text)
        
        changes = {
            'additions': [],
            'deletions': [],
            'modifications': [],
            'similarity': self.diff_matcher.ratio(),
            'change_summary': self._generate_change_summary(old_text, new_text)
        }
        
        for tag, i1, i2, j1, j2 in self.diff_matcher.get_opcodes():
            if tag == 'insert':
                changes['additions'].append(new_text[j1:j2])
            elif tag == 'delete':
                changes['deletions'].append(old_text[i1:i2])
            elif tag == 'replace':
                changes['modifications'].append({
                    'old': old_text[i1:i2],
                    'new': new_text[j1:j2]
                })
                
        return changes
    
    def _generate_change_summary(self, old_text: str, new_text: str) -> Dict:
        """Generate a summary of changes"""
        return {
            'old_length': len(old_text),
            'new_length': len(new_text),
            'length_diff': len(new_text) - len(old_text),
            'old_hash': hashlib.sha256(old_text.encode()).hexdigest(),
            'new_hash': hashlib.sha256(new_text.encode()).hexdigest(),
            'timestamp': datetime.utcnow().isoformat()
        }