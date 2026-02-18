"""
Entity Extractor for Pharmaceutical Documents
Extracts biomedical entities (drugs, diseases, proteins, companies) from text
"""
import re
import logging
from typing import Dict, List, Set
import config

logger = logging.getLogger(__name__)

class EntityExtractor:
    """
    Extracts pharmaceutical and biomedical entities from text.
    Uses both pattern-based and model-based approaches.
    """
    
    def __init__(self):
        self.spacy_model = None
        self._init_spacy()
        
    def _init_spacy(self):
        """Initialize scispacy model for biomedical NER"""
        try:
            import spacy
            # Try to load the scispacy model
            try:
                self.spacy_model = spacy.load("en_core_sci_sm")
                logger.info("Loaded scispacy model for entity extraction")
            except OSError:
                logger.warning("scispacy model not found. Install with: pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_sm-0.5.3.tar.gz")
                self.spacy_model = None
        except ImportError:
            logger.warning("spacy not installed. Entity extraction will use pattern-based approach only.")
            self.spacy_model = None
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract all entities from text.
        
        Args:
            text: Input text to extract entities from
            
        Returns:
            Dictionary with entity types as keys and lists of entity names as values
        """
        entities = {
            'drug': [],
            'disease': [],
            'protein': [],
            'company': [],
            'clinical_trial_id': [],
            'gene': []
        }
        
        # Pattern-based extraction
        entities['clinical_trial_id'] = self._extract_trial_ids(text)
        entities['company'] = self._extract_companies(text)
        
        # Spacy-based extraction (if available)
        if self.spacy_model:
            spacy_entities = self._extract_with_spacy(text)
            for entity_type, entity_list in spacy_entities.items():
                if entity_type in entities:
                    entities[entity_type].extend(entity_list)
        
        # Deduplicate and clean
        for entity_type in entities:
            entities[entity_type] = list(set(entities[entity_type]))
            entities[entity_type] = [e.strip() for e in entities[entity_type] if e.strip()]
        
        return entities
    
    def _extract_trial_ids(self, text: str) -> List[str]:
        """Extract clinical trial IDs (NCT numbers)"""
        pattern = r'NCT\d{8}'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [m.upper() for m in matches]
    
    def _extract_companies(self, text: str) -> List[str]:
        """Extract pharmaceutical company names from predefined list"""
        companies = []
        for company in config.PHARMA_COMPANIES:
            # Case-insensitive search with word boundaries
            pattern = r'\b' + re.escape(company) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                companies.append(company)
        return companies
    
    def _extract_with_spacy(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using scispacy model"""
        entities = {
            'drug': [],
            'disease': [],
            'protein': [],
            'gene': []
        }
        
        if not self.spacy_model:
            return entities
        
        try:
            # Process text with spacy
            doc = self.spacy_model(text[:1000000])  # Limit to 1M chars for performance
            
            for ent in doc.ents:
                entity_text = ent.text
                entity_label = ent.label_
                
                # Map spacy labels to our entity types
                if entity_label in ['CHEMICAL', 'DRUG']:
                    entities['drug'].append(entity_text)
                elif entity_label in ['DISEASE', 'DISORDER']:
                    entities['disease'].append(entity_text)
                elif entity_label in ['PROTEIN', 'GENE']:
                    # Try to distinguish protein from gene based on context
                    if len(entity_text) <= 10 and entity_text.isupper():
                        entities['gene'].append(entity_text)
                    else:
                        entities['protein'].append(entity_text)
        
        except Exception as e:
            logger.error(f"Error in spacy entity extraction: {e}")
        
        return entities
    
    def extract_entities_batch(self, texts: List[str]) -> List[Dict[str, List[str]]]:
        """
        Extract entities from multiple texts efficiently.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of entity dictionaries
        """
        return [self.extract_entities(text) for text in texts]
    
    def get_entity_set(self, entity_dict: Dict[str, List[str]]) -> Set[str]:
        """
        Get a flat set of all unique entities from an entity dictionary.
        
        Args:
            entity_dict: Dictionary from extract_entities
            
        Returns:
            Set of all unique entity names
        """
        all_entities = set()
        for entity_list in entity_dict.values():
            all_entities.update(entity_list)
        return all_entities


# Singleton instance
_extractor_instance = None

def get_entity_extractor() -> EntityExtractor:
    """Get or create the singleton entity extractor instance"""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = EntityExtractor()
    return _extractor_instance
