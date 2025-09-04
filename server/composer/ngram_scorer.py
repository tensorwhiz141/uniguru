"""
N-gram scorer for Uniguru-LM composer
Provides text smoothing and fluency scoring using n-gram models
"""

import logging
import re
import math
from typing import Dict, List, Tuple, Set
from collections import defaultdict, Counter
from functools import lru_cache

logger = logging.getLogger(__name__)

class NGramScorer:
    """N-gram based text scorer and smoother for improving fluency"""
    
    def __init__(self, n=3):
        self.n = n  # Default to trigrams
        self.language_models = {
            'EN': self._initialize_english_model(),
            'HI': self._initialize_hindi_model()
        }
        
    def _initialize_english_model(self) -> Dict:
        """Initialize English n-gram model with common patterns"""
        # Common English trigrams and patterns for spiritual/educational content
        common_trigrams = {
            # Religious/spiritual content
            ('according', 'to', 'the'): 0.95,
            ('in', 'the', 'sacred'): 0.90,
            ('the', 'sacred', 'texts'): 0.92,
            ('as', 'mentioned', 'in'): 0.88,
            ('this', 'teaching', 'shows'): 0.85,
            ('we', 'can', 'understand'): 0.87,
            ('the', 'scripture', 'tells'): 0.89,
            ('based', 'on', 'the'): 0.91,
            ('let', 'us', 'understand'): 0.84,
            ('this', 'helps', 'us'): 0.83,
            
            # Explanatory patterns
            ('for', 'example', 'when'): 0.86,
            ('this', 'means', 'that'): 0.88,
            ('in', 'other', 'words'): 0.82,
            ('to', 'understand', 'this'): 0.89,
            ('it', 'is', 'important'): 0.85,
            ('we', 'must', 'remember'): 0.84,
            
            # Comparative patterns
            ('on', 'the', 'other'): 0.87,
            ('in', 'contrast', 'to'): 0.83,
            ('similar', 'to', 'this'): 0.81,
            ('different', 'from', 'the'): 0.82,
            
            # Concluding patterns
            ('therefore', 'we', 'can'): 0.86,
            ('thus', 'it', 'is'): 0.84,
            ('in', 'conclusion', 'the'): 0.85,
            ('this', 'wisdom', 'teaches'): 0.87
        }
        
        # Common bigrams
        common_bigrams = {
            ('the', 'sacred'): 0.92,
            ('sacred', 'texts'): 0.90,
            ('according', 'to'): 0.95,
            ('we', 'can'): 0.88,
            ('this', 'teaching'): 0.85,
            ('spiritual', 'wisdom'): 0.87,
            ('divine', 'knowledge'): 0.86,
            ('ancient', 'wisdom'): 0.84,
            ('for', 'example'): 0.89,
            ('in', 'conclusion'): 0.83
        }
        
        return {
            'trigrams': common_trigrams,
            'bigrams': common_bigrams,
            'vocabulary': self._build_vocabulary(common_trigrams, common_bigrams)
        }
    
    def _initialize_hindi_model(self) -> Dict:
        """Initialize Hindi n-gram model with common patterns"""
        # Common Hindi trigrams for spiritual content
        common_trigrams = {
            # Religious patterns
            ('शास्त्रों', 'के', 'अनुसार'): 0.95,
            ('पवित्र', 'ग्रंथों', 'में'): 0.92,
            ('इस', 'शिक्षा', 'से'): 0.88,
            ('हमें', 'यह', 'समझना'): 0.87,
            ('के', 'अनुसार', 'यह'): 0.89,
            ('यह', 'ज्ञान', 'हमें'): 0.86,
            ('आध्यात्मिक', 'ज्ञान', 'के'): 0.85,
            
            # Explanatory patterns  
            ('उदाहरण', 'के', 'लिए'): 0.90,
            ('इसका', 'अर्थ', 'यह'): 0.87,
            ('दूसरे', 'शब्दों', 'में'): 0.84,
            ('समझने', 'के', 'लिए'): 0.88,
            ('यह', 'महत्वपूर्ण', 'है'): 0.86,
            
            # Concluding patterns
            ('इसलिए', 'हम', 'कह'): 0.85,
            ('निष्कर्ष', 'में', 'यह'): 0.83,
            ('यह', 'ज्ञान', 'सिखाता'): 0.87
        }
        
        common_bigrams = {
            ('पवित्र', 'ग्रंथ'): 0.91,
            ('आध्यात्मिक', 'ज्ञान'): 0.89,
            ('के', 'अनुसार'): 0.94,
            ('हमें', 'समझना'): 0.86,
            ('यह', 'शिक्षा'): 0.84,
            ('प्राचीन', 'ज्ञान'): 0.87,
            ('दिव्य', 'ज्ञान'): 0.85
        }
        
        return {
            'trigrams': common_trigrams,
            'bigrams': common_bigrams,
            'vocabulary': self._build_vocabulary(common_trigrams, common_bigrams)
        }
    
    def _build_vocabulary(self, trigrams: Dict, bigrams: Dict) -> Set[str]:
        """Build vocabulary from n-gram patterns"""
        vocab = set()
        for trigram in trigrams.keys():
            vocab.update(trigram)
        for bigram in bigrams.keys():
            vocab.update(bigram)
        return vocab
    
    def smooth_text(self, text: str, lang: str) -> str:
        """
        Apply n-gram smoothing to improve text fluency
        
        Args:
            text: Input text to smooth
            lang: Language code (EN/HI)
            
        Returns:
            Smoothed text with improved fluency
        """
        try:
            # Get language model
            model = self.language_models.get(lang, self.language_models['EN'])
            
            # Tokenize text into sentences
            sentences = self._tokenize_sentences(text, lang)
            
            # Smooth each sentence
            smoothed_sentences = []
            for sentence in sentences:
                smoothed_sentence = self._smooth_sentence(sentence, model, lang)
                smoothed_sentences.append(smoothed_sentence)
            
            # Rejoin sentences
            smoothed_text = self._rejoin_sentences(smoothed_sentences, lang)
            
            # Apply final polishing
            polished_text = self._apply_final_polish(smoothed_text, lang)
            
            logger.info(f"Text smoothed for language: {lang}")
            return polished_text
            
        except Exception as e:
            logger.error(f"Text smoothing failed: {str(e)}")
            return text  # Return original text if smoothing fails
    
    def _tokenize_sentences(self, text: str, lang: str) -> List[str]:
        """Tokenize text into sentences"""
        if lang == 'HI':
            # Hindi sentence boundaries
            sentences = re.split(r'[।!?]', text)
        else:
            # English sentence boundaries
            sentences = re.split(r'[.!?]', text)
        
        # Clean and filter empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _smooth_sentence(self, sentence: str, model: Dict, lang: str) -> str:
        """Smooth individual sentence using n-gram scoring"""
        # Tokenize sentence into words
        words = self._tokenize_words(sentence, lang)
        if len(words) < 2:
            return sentence
        
        # Apply n-gram based smoothing
        smoothed_words = self._apply_ngram_smoothing(words, model)
        
        # Reconstruct sentence
        smoothed_sentence = self._reconstruct_sentence(smoothed_words, lang)
        return smoothed_sentence
    
    def _tokenize_words(self, sentence: str, lang: str) -> List[str]:
        """Tokenize sentence into words"""
        # Remove punctuation and split
        if lang == 'HI':
            # Handle Devanagari script
            words = re.findall(r'[\u0900-\u097F]+|[A-Za-z]+', sentence.lower())
        else:
            # English tokenization
            words = re.findall(r'\b\w+\b', sentence.lower())
        
        return [word for word in words if word.strip()]
    
    def _apply_ngram_smoothing(self, words: List[str], model: Dict) -> List[str]:
        """Apply n-gram based smoothing to word sequence"""
        if len(words) < 3:
            return words
        
        smoothed_words = words.copy()
        
        # Check and improve trigrams
        for i in range(len(words) - 2):
            trigram = (words[i], words[i+1], words[i+2])
            
            # Look for better alternatives in model
            if trigram not in model['trigrams']:
                better_trigram = self._find_better_trigram(trigram, model)
                if better_trigram:
                    smoothed_words[i] = better_trigram[0]
                    smoothed_words[i+1] = better_trigram[1]
                    smoothed_words[i+2] = better_trigram[2]
        
        return smoothed_words
    
    def _find_better_trigram(self, original_trigram: Tuple, model: Dict) -> Tuple:
        """Find better trigram alternative if available"""
        # Look for trigrams with similar words
        best_score = 0.0
        best_trigram = None
        
        for model_trigram, score in model['trigrams'].items():
            similarity = self._calculate_trigram_similarity(original_trigram, model_trigram)
            if similarity > 0.6 and score > best_score:
                best_score = score
                best_trigram = model_trigram
        
        return best_trigram
    
    def _calculate_trigram_similarity(self, trigram1: Tuple, trigram2: Tuple) -> float:
        """Calculate similarity between two trigrams"""
        matches = sum(1 for w1, w2 in zip(trigram1, trigram2) if w1 == w2)
        return matches / 3.0
    
    def _reconstruct_sentence(self, words: List[str], lang: str) -> str:
        """Reconstruct sentence from words"""
        if not words:
            return ""
        
        # Join words with appropriate spacing
        sentence = " ".join(words)
        
        # Capitalize first letter
        if sentence:
            sentence = sentence[0].upper() + sentence[1:]
        
        return sentence
    
    def _rejoin_sentences(self, sentences: List[str], lang: str) -> str:
        """Rejoin sentences with appropriate punctuation"""
        if not sentences:
            return ""
        
        # Add appropriate sentence endings
        punctuated_sentences = []
        for sentence in sentences:
            if sentence and not sentence.endswith(('.', '!', '?', '।')):
                if lang == 'HI':
                    sentence += '।'
                else:
                    sentence += '.'
            punctuated_sentences.append(sentence)
        
        # Join with spaces
        return " ".join(punctuated_sentences)
    
    def _apply_final_polish(self, text: str, lang: str) -> str:
        """Apply final polishing to the smoothed text"""
        # Fix common spacing issues
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\s+([।.!?])', r'\1', text)  # Space before punctuation
        text = re.sub(r'([।.!?])\s*([A-Za-z\u0900-\u097F])', r'\1 \2', text)  # Space after punctuation
        
        # Ensure proper capitalization
        if lang == 'EN':
            text = re.sub(r'([।.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
        
        return text.strip()
    
    def calculate_fluency_score(self, text: str, lang: str) -> float:
        """
        Calculate fluency score for generated text
        
        Args:
            text: Text to score
            lang: Language code
            
        Returns:
            Fluency score between 0.0 and 1.0
        """
        try:
            model = self.language_models.get(lang, self.language_models['EN'])
            sentences = self._tokenize_sentences(text, lang)
            
            total_score = 0.0
            total_ngrams = 0
            
            for sentence in sentences:
                words = self._tokenize_words(sentence, lang)
                sentence_score, ngram_count = self._score_sentence(words, model)
                total_score += sentence_score
                total_ngrams += ngram_count
            
            if total_ngrams == 0:
                return 0.5  # Neutral score for empty/very short text
            
            average_score = total_score / total_ngrams
            return min(1.0, max(0.0, average_score))  # Clamp to [0, 1]
            
        except Exception as e:
            logger.error(f"Fluency scoring failed: {str(e)}")
            return 0.5  # Neutral score on error
    
    def _score_sentence(self, words: List[str], model: Dict) -> Tuple[float, int]:
        """Score individual sentence and return score and n-gram count"""
        if len(words) < 2:
            return 0.5, 1
        
        score = 0.0
        ngram_count = 0
        
        # Score trigrams
        for i in range(len(words) - 2):
            trigram = (words[i], words[i+1], words[i+2])
            if trigram in model['trigrams']:
                score += model['trigrams'][trigram]
            else:
                score += 0.3  # Default score for unknown trigrams
            ngram_count += 1
        
        # Score bigrams
        for i in range(len(words) - 1):
            bigram = (words[i], words[i+1])
            if bigram in model['bigrams']:
                score += model['bigrams'][bigram] * 0.5  # Lower weight for bigrams
            else:
                score += 0.15  # Default score for unknown bigrams
            ngram_count += 0.5  # Partial count for bigrams
        
        return score, ngram_count
    
    @lru_cache(maxsize=1000)
    def get_word_suggestions(self, context: Tuple[str, str], lang: str) -> List[str]:
        """Get word suggestions based on context (cached for performance)"""
        model = self.language_models.get(lang, self.language_models['EN'])
        suggestions = []
        
        # Look for trigrams that start with the context
        for trigram in model['trigrams'].keys():
            if trigram[:2] == context:
                suggestions.append(trigram[2])
        
        # Sort by score
        suggestions = sorted(suggestions, key=lambda w: model['trigrams'].get(context + (w,), 0), reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions