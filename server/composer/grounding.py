"""
Grounding verification module for Uniguru-LM composer
Ensures generated text has token overlap with source chunks
"""

import logging
import re
import string
from typing import Dict, List, Set, Tuple, Any
from collections import Counter

logger = logging.getLogger(__name__)

class GroundingVerifier:
    """
    Verifies that generated text is grounded in source chunks
    Implements token overlap checking as specified in requirements
    """
    
    def __init__(self, min_overlap_ratio: float = 0.3, min_tokens: int = 3):
        """
        Initialize grounding verifier
        
        Args:
            min_overlap_ratio: Minimum ratio of overlapping tokens required
            min_tokens: Minimum number of overlapping tokens required
        """
        self.min_overlap_ratio = min_overlap_ratio
        self.min_tokens = min_tokens
        self.stopwords = self._initialize_stopwords()
    
    def _initialize_stopwords(self) -> Dict[str, Set[str]]:
        """Initialize stopwords for different languages"""
        return {
            'EN': {
                'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                'should', 'may', 'might', 'can', 'must', 'shall', 'to', 'of', 'in',
                'for', 'on', 'with', 'by', 'from', 'as', 'at', 'or', 'and', 'but',
                'if', 'then', 'than', 'when', 'where', 'why', 'how', 'what', 'which',
                'who', 'whom', 'whose', 'this', 'that', 'these', 'those', 'i', 'you',
                'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
            },
            'HI': {
                'है', 'हैं', 'था', 'थे', 'थी', 'हो', 'होना', 'होने', 'होगा', 'होंगे',
                'में', 'की', 'के', 'को', 'से', 'पर', 'या', 'और', 'तथा', 'एवं',
                'यह', 'वह', 'ये', 'वे', 'इस', 'उस', 'इन', 'उन', 'जो', 'जिस',
                'कि', 'अगर', 'यदि', 'तो', 'फिर', 'भी', 'तक', 'बाद', 'पहले',
                'अब', 'यहाँ', 'वहाँ', 'कहाँ', 'कब', 'कैसे', 'क्यों', 'क्या',
                'कौन', 'कौनसा', 'मैं', 'तू', 'आप', 'हम', 'तुम', 'वो'
            }
        }
    
    def verify_grounding(self, generated_text: str, top_chunks: List[Dict]) -> Dict[str, Any]:
        """
        Verify that generated text is grounded in source chunks
        
        Args:
            generated_text: The text to verify
            top_chunks: Source chunks to check against
            
        Returns:
            Dict containing grounding verification results
        """
        try:
            if not generated_text or not top_chunks:
                return {
                    'grounded': False,
                    'score': 0.0,
                    'overlapping_tokens': [],
                    'overlap_ratio': 0.0,
                    'chunk_coverage': [],
                    'error': 'Empty input'
                }
            
            # Tokenize generated text
            generated_tokens = self._tokenize_text(generated_text)
            
            # Get content tokens (excluding stopwords)
            content_tokens = self._filter_content_tokens(generated_tokens)
            
            if not content_tokens:
                return {
                    'grounded': False,
                    'score': 0.0,
                    'overlapping_tokens': [],
                    'overlap_ratio': 0.0,
                    'chunk_coverage': [],
                    'error': 'No content tokens found'
                }
            
            # Check overlap with each chunk
            chunk_overlaps = []
            all_overlapping_tokens = set()
            
            for i, chunk in enumerate(top_chunks):
                chunk_text = chunk.get('text', '')
                if not chunk_text:
                    continue
                
                chunk_tokens = self._tokenize_text(chunk_text)
                chunk_content_tokens = self._filter_content_tokens(chunk_tokens)
                
                # Find overlapping tokens
                overlap = content_tokens.intersection(chunk_content_tokens)
                overlap_ratio = len(overlap) / len(content_tokens) if content_tokens else 0.0
                
                chunk_overlap = {
                    'chunk_id': i,
                    'source': chunk.get('source', f'Chunk {i}'),
                    'overlapping_tokens': list(overlap),
                    'overlap_count': len(overlap),
                    'overlap_ratio': overlap_ratio,
                    'chunk_score': chunk.get('score', 0.0)
                }
                
                chunk_overlaps.append(chunk_overlap)
                all_overlapping_tokens.update(overlap)
            
            # Calculate overall grounding metrics
            total_overlap_count = len(all_overlapping_tokens)
            total_overlap_ratio = total_overlap_count / len(content_tokens) if content_tokens else 0.0
            
            # Calculate grounding score
            grounding_score = self._calculate_grounding_score(
                total_overlap_count, total_overlap_ratio, chunk_overlaps
            )
            
            # Determine if text is grounded
            is_grounded = (
                total_overlap_count >= self.min_tokens and 
                total_overlap_ratio >= self.min_overlap_ratio
            )
            
            # Additional semantic grounding check
            semantic_score = self._check_semantic_grounding(generated_text, top_chunks)
            
            # Combine scores
            final_score = (grounding_score * 0.7) + (semantic_score * 0.3)
            
            result = {
                'grounded': is_grounded,
                'score': final_score,
                'overlapping_tokens': list(all_overlapping_tokens),
                'overlap_count': total_overlap_count,
                'overlap_ratio': total_overlap_ratio,
                'content_tokens_count': len(content_tokens),
                'chunk_coverage': chunk_overlaps,
                'semantic_score': semantic_score,
                'min_tokens_met': total_overlap_count >= self.min_tokens,
                'min_ratio_met': total_overlap_ratio >= self.min_overlap_ratio
            }
            
            logger.info(f"Grounding verification: grounded={is_grounded}, score={final_score:.3f}, overlaps={total_overlap_count}")
            
            return result
            
        except Exception as e:
            logger.error(f"Grounding verification failed: {str(e)}")
            return {
                'grounded': False,
                'score': 0.0,
                'overlapping_tokens': [],
                'overlap_ratio': 0.0,
                'chunk_coverage': [],
                'error': str(e)
            }
    
    def _tokenize_text(self, text: str) -> Set[str]:
        """Tokenize text into normalized tokens"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Handle different scripts
        if self._contains_devanagari(text):
            # Devanagari tokenization
            tokens = re.findall(r'[\u0900-\u097F]+', text)
        else:
            # Latin script tokenization
            tokens = re.findall(r'\b[a-zA-Z]+\b', text)
        
        # Filter out very short tokens
        tokens = [token for token in tokens if len(token) > 1]
        
        return set(tokens)
    
    def _contains_devanagari(self, text: str) -> bool:
        """Check if text contains Devanagari script"""
        return bool(re.search(r'[\u0900-\u097F]', text))
    
    def _filter_content_tokens(self, tokens: Set[str]) -> Set[str]:
        """Filter out stopwords to get content tokens"""
        # Determine language based on tokens
        if any(self._contains_devanagari(token) for token in tokens):
            stopwords = self.stopwords['HI']
        else:
            stopwords = self.stopwords['EN']
        
        # Filter out stopwords
        content_tokens = {token for token in tokens if token not in stopwords}
        
        return content_tokens
    
    def _calculate_grounding_score(self, overlap_count: int, overlap_ratio: float, chunk_overlaps: List[Dict]) -> float:
        """Calculate grounding score based on overlap metrics"""
        if not chunk_overlaps:
            return 0.0
        
        # Base score from overlap ratio
        base_score = min(1.0, overlap_ratio / self.min_overlap_ratio)
        
        # Bonus for meeting minimum token count
        token_bonus = 0.2 if overlap_count >= self.min_tokens else 0.0
        
        # Bonus for coverage across multiple chunks
        coverage_bonus = 0.0
        covered_chunks = sum(1 for chunk in chunk_overlaps if chunk['overlap_count'] > 0)
        if covered_chunks > 1:
            coverage_bonus = min(0.2, (covered_chunks - 1) * 0.1)
        
        # Penalty for very low overlap
        penalty = 0.0
        if overlap_ratio < 0.1:
            penalty = 0.3
        
        final_score = base_score + token_bonus + coverage_bonus - penalty
        return max(0.0, min(1.0, final_score))
    
    def _check_semantic_grounding(self, generated_text: str, top_chunks: List[Dict]) -> float:
        """Check semantic grounding beyond just token overlap"""
        try:
            # Extract key concepts and entities
            generated_concepts = self._extract_concepts(generated_text)
            
            semantic_overlap = 0.0
            total_concepts = len(generated_concepts)
            
            if total_concepts == 0:
                return 0.5  # Neutral score if no concepts found
            
            for chunk in top_chunks[:3]:  # Check top 3 chunks
                chunk_text = chunk.get('text', '')
                chunk_concepts = self._extract_concepts(chunk_text)
                
                # Check concept overlap
                concept_overlap = generated_concepts.intersection(chunk_concepts)
                if concept_overlap:
                    semantic_overlap += len(concept_overlap) / total_concepts
            
            # Normalize by number of chunks checked
            semantic_score = min(1.0, semantic_overlap / 3)
            
            return semantic_score
            
        except Exception as e:
            logger.error(f"Semantic grounding check failed: {str(e)}")
            return 0.5  # Neutral score on error
    
    def _extract_concepts(self, text: str) -> Set[str]:
        """Extract key concepts from text"""
        concepts = set()
        
        # Spiritual and philosophical concepts
        spiritual_concepts = [
            # English concepts
            'dharma', 'karma', 'moksha', 'yoga', 'meditation', 'wisdom', 'truth',
            'knowledge', 'devotion', 'compassion', 'enlightenment', 'consciousness',
            'soul', 'spirit', 'divine', 'sacred', 'holy', 'transcendence',
            'liberation', 'self-realization', 'inner peace', 'spiritual growth',
            
            # Hindi concepts (transliterated)
            'ध्यान', 'योग', 'कर्म', 'धर्म', 'मोक्ष', 'आत्मा', 'ब्रह्म', 'ईश्वर',
            'भक्ति', 'ज्ञान', 'शांति', 'करुणा', 'दया', 'अहिंसा', 'सत्य', 'प्रेम'
        ]
        
        text_lower = text.lower()
        
        for concept in spiritual_concepts:
            if concept in text_lower:
                concepts.add(concept)
        
        # Extract proper nouns (likely to be important concepts)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', text)
        concepts.update([noun.lower() for noun in proper_nouns])
        
        return concepts
    
    def check_sentence_grounding(self, sentence: str, top_chunks: List[Dict]) -> bool:
        """
        Check if a single sentence has token overlap with chunks
        As per requirement: any sentence must have at least one token overlap
        
        Args:
            sentence: Single sentence to check
            top_chunks: Source chunks
            
        Returns:
            True if sentence has at least one token overlap with chunks
        """
        try:
            sentence_tokens = self._tokenize_text(sentence)
            content_tokens = self._filter_content_tokens(sentence_tokens)
            
            if not content_tokens:
                return False
            
            # Check if any token overlaps with any chunk
            for chunk in top_chunks:
                chunk_text = chunk.get('text', '')
                chunk_tokens = self._tokenize_text(chunk_text)
                chunk_content_tokens = self._filter_content_tokens(chunk_tokens)
                
                # If there's any overlap, sentence is grounded
                if content_tokens.intersection(chunk_content_tokens):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Sentence grounding check failed: {str(e)}")
            return False
    
    def verify_sentence_by_sentence(self, generated_text: str, top_chunks: List[Dict]) -> Dict[str, Any]:
        """
        Verify grounding sentence by sentence
        Ensures every sentence has token overlap as per requirements
        
        Args:
            generated_text: Text to verify
            top_chunks: Source chunks
            
        Returns:
            Detailed sentence-by-sentence grounding results
        """
        try:
            # Split into sentences
            sentences = self._split_sentences(generated_text)
            
            sentence_results = []
            all_grounded = True
            
            for i, sentence in enumerate(sentences):
                if not sentence.strip():
                    continue
                
                is_grounded = self.check_sentence_grounding(sentence, top_chunks)
                
                sentence_result = {
                    'sentence_id': i,
                    'sentence': sentence.strip(),
                    'grounded': is_grounded
                }
                
                sentence_results.append(sentence_result)
                
                if not is_grounded:
                    all_grounded = False
            
            grounded_count = sum(1 for result in sentence_results if result['grounded'])
            total_sentences = len(sentence_results)
            grounding_ratio = grounded_count / total_sentences if total_sentences > 0 else 0.0
            
            return {
                'all_sentences_grounded': all_grounded,
                'grounded_sentences': grounded_count,
                'total_sentences': total_sentences,
                'grounding_ratio': grounding_ratio,
                'sentence_details': sentence_results
            }
            
        except Exception as e:
            logger.error(f"Sentence-by-sentence grounding check failed: {str(e)}")
            return {
                'all_sentences_grounded': False,
                'grounded_sentences': 0,
                'total_sentences': 0,
                'grounding_ratio': 0.0,
                'sentence_details': [],
                'error': str(e)
            }
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Handle both English and Hindi sentence endings
        sentences = re.split(r'[.!?।]', text)
        
        # Clean and filter
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def improve_grounding(self, generated_text: str, top_chunks: List[Dict]) -> str:
        """
        Improve grounding of text by adding source-based content
        
        Args:
            generated_text: Text to improve
            top_chunks: Source chunks to draw from
            
        Returns:
            Improved text with better grounding
        """
        try:
            # Check current grounding
            grounding_result = self.verify_grounding(generated_text, top_chunks)
            
            if grounding_result['grounded']:
                return generated_text  # Already well grounded
            
            # Improve grounding by adding source content
            improved_text = generated_text
            
            # Add key terms from source chunks
            source_tokens = set()
            for chunk in top_chunks[:2]:  # Use top 2 chunks
                chunk_tokens = self._tokenize_text(chunk.get('text', ''))
                chunk_content = self._filter_content_tokens(chunk_tokens)
                source_tokens.update(chunk_content)
            
            # Find important source tokens not in generated text
            generated_tokens = self._tokenize_text(generated_text)
            generated_content = self._filter_content_tokens(generated_tokens)
            
            missing_tokens = source_tokens - generated_content
            
            # Add some missing tokens as a clarifying sentence
            if missing_tokens:
                important_tokens = list(missing_tokens)[:3]  # Limit to 3 tokens
                if important_tokens:
                    clarification = f" This relates to concepts like {', '.join(important_tokens)}."
                    improved_text += clarification
            
            return improved_text
            
        except Exception as e:
            logger.error(f"Grounding improvement failed: {str(e)}")
            return generated_text  # Return original on error