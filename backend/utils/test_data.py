import json
from pathlib import Path
from typing import Dict, List
import uuid

def generate_test_data() -> Dict:
    """Generate sample test data for scrapers"""
    return {
        "companies": [
            {
                "id": str(uuid.uuid4()),
                "name": "Example Tech",
                "domain": "example.com",
                "documents": [
                    {
                        "type": "terms_of_service",
                        "title": "Terms of Service",
                        "content": "This is a sample Terms of Service...",
                        "effective_date": "2023-01-01",
                        "version": "1.0"
                    },
                    {
                        "type": "privacy_policy",
                        "title": "Privacy Policy",
                        "content": "This is a sample Privacy Policy...",
                        "effective_date": "2023-01-01",
                        "version": "1.0"
                    }
                ]
            }
        ]
    }

def save_test_data(output_dir: str = "tests/fixtures"):
    """Save test data to fixtures directory"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    test_data = generate_test_data()
    with open(f"{output_dir}/sample_documents.json", "w") as f:
        json.dump(test_data, f, indent=2)