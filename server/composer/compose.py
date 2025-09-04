"""
Main composer module for Uniguru-LM
Handles KB-grounded NLP composition with templates, n-gram scoring, and GRU fallback
Day 2: Enhanced with RL policy and strengthened grounding verification
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from .templates import TemplateEngine
from .ngram_scorer import NGramScorer
from .gru import GRUStub
from .grounding import GroundingVerifier
from .rl_policy import get_rl_policy, PolicyAction, calculate_reward
from .performance_monitor_clean import get_performance_monitor, log_composition_trace

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Composer:
    """Main composer class for text generation"""
    
    def __init__(self):
        self.template_engine = TemplateEngine()
        self.ngram_scorer = NGramScorer()
        self.gru_model = GRUStub()
        self.grounding_verifier = GroundingVerifier()
        self.rl_policy = get_rl_policy()  # RL policy for template selection
        self.performance_monitor = get_performance_monitor()  # Performance monitoring
        
    def compose(self, trace_id: str, extractive_answer: str, top_chunks: List[Dict], lang: str = "EN") -> Dict[str, Any]:
        """
        Main composition function as per API specification
        
        Args:
            trace_id (str): Unique identifier for this composition request
            extractive_answer (str): Initial extractive answer from retrieval
            top_chunks (List[Dict]): Top retrieved chunks with metadata
            lang (str): Language code (EN/HI)
            
        Returns:
            Dict containing composed text, grounding status, and metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting composition for trace_id: {trace_id}, lang: {lang}")
            
            # Validate inputs
            if not extractive_answer or not top_chunks:
                raise ValueError("extractive_answer and top_chunks are required")
                
            # Select appropriate template using RL policy
            policy_context = {
                'extractive_answer': extractive_answer,
                'top_chunks': top_chunks,
                'lang': lang
            }
            
            rl_action, action_metadata = self.rl_policy.select_action(policy_context)
            
            # Map RL action to template
            if rl_action == PolicyAction.EXPLAIN:
                template_id, template = self.template_engine.get_explain_template(lang)
            elif rl_action == PolicyAction.COMPARE:
                template_id, template = self.template_engine.get_compare_template(lang)
            elif rl_action == PolicyAction.EXAMPLE:
                template_id, template = self.template_engine.get_example_template(lang)
            else:  # EXTRACTIVE
                template_id, template = self.template_engine.get_extractive_fallback(lang)
            
            # Fallback to content-based selection if RL template not suitable
            if not self._is_template_suitable(template_id, extractive_answer, top_chunks):
                logger.info(f"RL template {template_id} not suitable, falling back to content-based selection")
                template_id, template = self.template_engine.select_template(
                    extractive_answer, top_chunks, lang
                )
            
            # Generate initial composition using template
            composed_text = self.template_engine.apply_template(
                template, extractive_answer, top_chunks, lang
            )
            
            # Apply n-gram smoothing for better fluency
            smoothed_text = self.ngram_scorer.smooth_text(composed_text, lang)
            
            # Try GRU enhancement if available, fallback to n-gram result
            final_text = self._try_gru_enhancement(smoothed_text, top_chunks, lang)
            
            # Enhanced grounding verification with auto-fallback
            grounding_result = self.grounding_verifier.verify_grounding(
                final_text, top_chunks
            )
            
            grounding_attempts = 1
            max_grounding_attempts = 3
            
            # If grounding fails, apply progressive fallback strategy
            while not grounding_result['grounded'] and grounding_attempts < max_grounding_attempts:
                logger.warning(f"Grounding failed (attempt {grounding_attempts}), applying fallback strategy")
                
                if grounding_attempts == 1:
                    # First fallback: Try extractive template
                    template_id, fallback_template = self.template_engine.get_extractive_fallback(lang)
                    final_text = self.template_engine.apply_template(
                        fallback_template, extractive_answer, top_chunks, lang
                    )
                elif grounding_attempts == 2:
                    # Second fallback: Improve grounding directly
                    final_text = self.grounding_verifier.improve_grounding(
                        final_text, top_chunks
                    )
                
                # Re-verify grounding
                grounding_result = self.grounding_verifier.verify_grounding(
                    final_text, top_chunks
                )
                grounding_attempts += 1
            
            # Prepare response with RL integration
            composition_time = time.time() - start_time
            
            result = {
                'trace_id': trace_id,
                'final_text': final_text,
                'template_id': template_id,
                'grounded': grounding_result['grounded'],
                'grounding_score': grounding_result['score'],
                'overlapping_tokens': grounding_result['overlapping_tokens'],
                'composition_time_ms': round(composition_time * 1000, 2),
                'lang': lang,
                'method': 'gru' if self.gru_model.is_available() else 'ngram_template',
                'citations': self._extract_citations(top_chunks),
                'grounding_attempts': grounding_attempts,
                # RL metadata
                'rl_action': rl_action.value,
                'rl_metadata': action_metadata,
                'policy_stats': self.rl_policy.get_policy_stats()
            }
            
            # Calculate and log reward for RL
            reward = calculate_reward(result)
            self.rl_policy.update_policy(trace_id, action_metadata, reward, result)
            result['rl_reward'] = reward
            
            # Log composition trace for monitoring
            log_composition_trace(result, extractive_answer, top_chunks)
            
            logger.info(f"Composition completed for trace_id: {trace_id}, grounded: {grounding_result['grounded']}")
            return result
            
        except Exception as e:
            logger.error(f"Composition failed for trace_id: {trace_id}, error: {str(e)}")
            return {
                'trace_id': trace_id,
                'final_text': extractive_answer,  # Fallback to original answer
                'template_id': 'error_fallback',
                'grounded': False,
                'grounding_score': 0.0,
                'overlapping_tokens': [],
                'composition_time_ms': round((time.time() - start_time) * 1000, 2),
                'lang': lang,
                'method': 'error_fallback',
                'error': str(e),
                'citations': self._extract_citations(top_chunks) if top_chunks else []
            }
    
    def _try_gru_enhancement(self, text: str, top_chunks: List[Dict], lang: str) -> str:
        """Try to enhance text with GRU model, fallback to original if not available"""
        try:
            if self.gru_model.is_available():
                return self.gru_model.enhance_text(text, top_chunks, lang)
            else:
                logger.info("GRU model not available, using n-gram result")
                return text
        except Exception as e:
            logger.warning(f"GRU enhancement failed: {str(e)}, using fallback")
            return text
    
    def _is_template_suitable(self, template_id: str, extractive_answer: str, top_chunks: List[Dict]) -> bool:
        """Check if selected template is suitable for the content"""
        # Simple heuristics for template suitability
        answer_length = len(extractive_answer)
        chunk_count = len(top_chunks)
        
        if 'compare' in template_id and chunk_count < 2:
            return False  # Need multiple chunks for comparison
        
        if 'example' in template_id and answer_length < 30:
            return False  # Need substantial content for examples
        
        return True
    
    def update_with_feedback(self, trace_id: str, feedback: Dict[str, Any]):
        """Update RL policy with user feedback"""
        try:
            # Find the action metadata for this trace_id
            # This would typically be stored in a database
            # For now, we'll use the current session data
            
            reward = calculate_reward({}, feedback)
            logger.info(f"Feedback received for trace_id: {trace_id}, reward: {reward:.3f}")
            
            # Note: In a full implementation, we would store action metadata
            # and retrieve it here to update the policy
            
        except Exception as e:
            logger.error(f"Failed to update with feedback: {str(e)}")
    
    def _extract_citations(self, top_chunks: List[Dict]) -> List[Dict]:
        citations = []
        for i, chunk in enumerate(top_chunks[:3]):  # Limit to top 3 citations
            citation = {
                'id': i + 1,
                'source': chunk.get('source', 'Unknown'),
                'text_preview': chunk.get('text', '')[:100] + '...' if len(chunk.get('text', '')) > 100 else chunk.get('text', ''),
                'score': chunk.get('score', 0.0)
            }
            citations.append(citation)
        return citations

# Global composer instance
_composer_instance = None

def get_composer():
    """Get singleton composer instance"""
    global _composer_instance
    if _composer_instance is None:
        _composer_instance = Composer()
    return _composer_instance

def compose(trace_id: str, extractive_answer: str, top_chunks: List[Dict], lang: str = "EN") -> Dict[str, Any]:
    """
    Public API function for composition
    
    Args:
        trace_id (str): Unique identifier for this composition request
        extractive_answer (str): Initial extractive answer from retrieval
        top_chunks (List[Dict]): Top retrieved chunks with metadata
        lang (str): Language code (EN/HI)
        
    Returns:
        Dict containing composed text and metadata
    """
    composer = get_composer()
    return composer.compose(trace_id, extractive_answer, top_chunks, lang)