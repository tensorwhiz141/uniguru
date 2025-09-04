"""
Unit tests for Uniguru-LM composer module

Tests cover all major components:
- Main compose function
- Template engine
- N-gram scorer
- GRU stub
- Grounding verification
"""

import unittest
import os
import sys
import tempfile
import json
from unittest.mock import patch, MagicMock

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from composer.compose import compose, Composer
from composer.templates import TemplateEngine, TemplateType
from composer.ngram_scorer import NGramScorer
from composer.gru import GRUStub
from composer.grounding import GroundingVerifier

class TestComposer(unittest.TestCase):
    """Test the main Composer class and compose function"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_chunks = [
            {
                'text': 'According to the sacred texts, meditation is a powerful practice that brings inner peace.',
                'source': 'Bhagavad Gita',
                'score': 0.95
            },
            {
                'text': 'The ancient wisdom teaches that self-control leads to liberation and spiritual growth.',
                'source': 'Upanishads',
                'score': 0.88
            },
            {
                'text': 'Dharma represents righteous living and moral conduct in all aspects of life.',
                'source': 'Dharma Shastra',
                'score': 0.82
            }
        ]
        
        self.sample_extractive_answer = "Meditation brings peace and spiritual growth through regular practice."
        self.trace_id = "test_trace_123"
    
    def test_compose_function_basic(self):
        """Test basic compose function functionality"""
        result = compose(
            trace_id=self.trace_id,
            extractive_answer=self.sample_extractive_answer,
            top_chunks=self.sample_chunks,
            lang="EN"
        )
        
        # Check required fields
        self.assertIn('trace_id', result)
        self.assertIn('final_text', result)
        self.assertIn('template_id', result)
        self.assertIn('grounded', result)
        self.assertIn('grounding_score', result)
        self.assertIn('composition_time_ms', result)
        
        # Check values
        self.assertEqual(result['trace_id'], self.trace_id)
        self.assertIsInstance(result['final_text'], str)
        self.assertGreater(len(result['final_text']), 0)
        self.assertIsInstance(result['grounded'], bool)
        self.assertIsInstance(result['grounding_score'], (int, float))
        self.assertGreaterEqual(result['grounding_score'], 0.0)
        self.assertLessEqual(result['grounding_score'], 1.0)
    
    def test_compose_function_hindi(self):
        """Test compose function with Hindi language"""
        hindi_chunks = [
            {
                'text': 'पवित्र ग्रंथों के अनुसार, ध्यान एक शक्तिशाली अभ्यास है जो आंतरिक शांति लाता है।',
                'source': 'भगवद्गीता',
                'score': 0.95
            }
        ]
        
        result = compose(
            trace_id=self.trace_id,
            extractive_answer="ध्यान से शांति मिलती है।",
            top_chunks=hindi_chunks,
            lang="HI"
        )
        
        self.assertEqual(result['lang'], 'HI')
        self.assertIn('final_text', result)
    
    def test_compose_function_empty_inputs(self):
        """Test compose function with empty inputs"""
        result = compose(
            trace_id=self.trace_id,
            extractive_answer="",
            top_chunks=[],
            lang="EN"
        )
        
        # Should handle gracefully and return fallback
        self.assertIn('final_text', result)
        self.assertIn('error', result)
    
    def test_composer_singleton(self):
        """Test that composer uses singleton pattern"""
        from composer.compose import get_composer
        
        composer1 = get_composer()
        composer2 = get_composer()
        
        self.assertIs(composer1, composer2)

class TestTemplateEngine(unittest.TestCase):
    """Test the TemplateEngine class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.template_engine = TemplateEngine()
        self.sample_chunks = [
            {
                'text': 'The sacred texts teach us about meditation and its benefits.',
                'source': 'Sacred Text',
                'score': 0.9
            }
        ]
    
    def test_template_initialization(self):
        """Test template engine initialization"""
        self.assertIn('EN', self.template_engine.templates)
        self.assertIn('HI', self.template_engine.templates)
        
        # Check template types exist
        for lang in ['EN', 'HI']:
            self.assertIn(TemplateType.EXPLAIN, self.template_engine.templates[lang])
            self.assertIn(TemplateType.COMPARE, self.template_engine.templates[lang])
            self.assertIn(TemplateType.EXAMPLE, self.template_engine.templates[lang])
            self.assertIn(TemplateType.EXTRACTIVE, self.template_engine.templates[lang])
    
    def test_template_selection(self):
        """Test template selection logic"""
        # Test explanation template selection
        template_id, template = self.template_engine.select_template(
            "What is meditation and how does it work?",
            self.sample_chunks,
            "EN"
        )
        
        self.assertIsInstance(template_id, str)
        self.assertIn('pattern', template)
        self.assertIn('id', template)
    
    def test_template_application(self):
        """Test template application"""
        template_id, template = self.template_engine.select_template(
            "Meditation brings peace",
            self.sample_chunks,
            "EN"
        )
        
        result = self.template_engine.apply_template(
            template, "Meditation brings peace", self.sample_chunks, "EN"
        )
        
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        self.assertIn("Meditation brings peace", result)
    
    def test_extractive_fallback(self):
        """Test extractive fallback template"""
        template_id, template = self.template_engine.get_extractive_fallback("EN")
        
        self.assertEqual(template_id, "extractive_en")
        self.assertIn('pattern', template)

class TestNGramScorer(unittest.TestCase):
    """Test the NGramScorer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ngram_scorer = NGramScorer()
    
    def test_ngram_scorer_initialization(self):
        """Test n-gram scorer initialization"""
        self.assertIn('EN', self.ngram_scorer.language_models)
        self.assertIn('HI', self.ngram_scorer.language_models)
        
        # Check model structure
        en_model = self.ngram_scorer.language_models['EN']
        self.assertIn('trigrams', en_model)
        self.assertIn('bigrams', en_model)
        self.assertIn('vocabulary', en_model)
    
    def test_text_smoothing_english(self):
        """Test text smoothing for English"""
        input_text = "According to the texts, meditation brings peace. This teaching helps us understand wisdom."
        
        smoothed_text = self.ngram_scorer.smooth_text(input_text, "EN")
        
        self.assertIsInstance(smoothed_text, str)
        self.assertGreater(len(smoothed_text), 0)
        # Should preserve basic meaning
        self.assertIn("meditation", smoothed_text.lower())
        self.assertIn("peace", smoothed_text.lower())
    
    def test_text_smoothing_hindi(self):
        """Test text smoothing for Hindi"""
        input_text = "शास्त्रों के अनुसार ध्यान शांति लाता है। यह शिक्षा हमें ज्ञान समझने में मदद करती है।"
        
        smoothed_text = self.ngram_scorer.smooth_text(input_text, "HI")
        
        self.assertIsInstance(smoothed_text, str)
        self.assertGreater(len(smoothed_text), 0)
    
    def test_fluency_scoring(self):
        """Test fluency scoring"""
        good_text = "According to the sacred texts, meditation helps achieve inner peace."
        poor_text = "Texts the according meditation inner achieve peace helps."
        
        good_score = self.ngram_scorer.calculate_fluency_score(good_text, "EN")
        poor_score = self.ngram_scorer.calculate_fluency_score(poor_text, "EN")
        
        self.assertIsInstance(good_score, float)
        self.assertIsInstance(poor_score, float)
        self.assertGreaterEqual(good_score, 0.0)
        self.assertLessEqual(good_score, 1.0)
        self.assertGreaterEqual(poor_score, 0.0)
        self.assertLessEqual(poor_score, 1.0)
    
    def test_word_suggestions(self):
        """Test word suggestions"""
        context = ('according', 'to')
        suggestions = self.ngram_scorer.get_word_suggestions(context, "EN")
        
        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), 5)

class TestGRUStub(unittest.TestCase):
    """Test the GRU stub class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use temporary directory for model
        self.temp_dir = tempfile.mkdtemp()
        self.model_path = os.path.join(self.temp_dir, "test_gru_model.pkl")
        self.gru_stub = GRUStub(model_path=self.model_path)
        
        self.sample_chunks = [
            {
                'text': 'Meditation is a spiritual practice.',
                'source': 'Test Source',
                'score': 0.9
            }
        ]
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_gru_stub_initialization(self):
        """Test GRU stub initialization"""
        self.assertIsNotNone(self.gru_stub.enhancement_rules)
        self.assertIn('EN', self.gru_stub.enhancement_rules)
        self.assertIn('HI', self.gru_stub.enhancement_rules)
    
    def test_gru_availability(self):
        """Test GRU availability check"""
        # Initially should not be available
        self.assertFalse(self.gru_stub.is_available())
    
    def test_text_enhancement_fallback(self):
        """Test text enhancement with fallback"""
        input_text = "Meditation brings peace."
        
        enhanced_text = self.gru_stub.enhance_text(input_text, self.sample_chunks, "EN")
        
        self.assertIsInstance(enhanced_text, str)
        self.assertGreater(len(enhanced_text), 0)
    
    def test_training_data_addition(self):
        """Test adding training data"""
        initial_count = len(self.gru_stub.training_data)
        
        self.gru_stub.add_training_data(
            "Input text",
            "Target text",
            {"type": "test"}
        )
        
        self.assertEqual(len(self.gru_stub.training_data), initial_count + 1)
        
        latest_sample = self.gru_stub.training_data[-1]
        self.assertEqual(latest_sample['input'], "Input text")
        self.assertEqual(latest_sample['target'], "Target text")
        self.assertEqual(latest_sample['metadata']['type'], "test")
    
    def test_model_training(self):
        """Test model training functionality"""
        # Add some training data
        for i in range(15):  # Add enough samples for training
            self.gru_stub.add_training_data(f"Input {i}", f"Target {i}")
        
        # Train model
        result = self.gru_stub.train_model(epochs=2, batch_size=8)
        
        self.assertIn('success', result)
        self.assertTrue(result['success'])
        self.assertIn('metrics', result)
    
    def test_model_info(self):
        """Test model info retrieval"""
        info = self.gru_stub.get_model_info()
        
        self.assertIn('is_available', info)
        self.assertIn('is_trained', info)
        self.assertIn('training_samples', info)
        self.assertIn('status', info)

class TestGroundingVerifier(unittest.TestCase):
    """Test the GroundingVerifier class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.grounding_verifier = GroundingVerifier()
        self.sample_chunks = [
            {
                'text': 'Meditation is a spiritual practice that brings inner peace and wisdom.',
                'source': 'Sacred Text',
                'score': 0.9
            },
            {
                'text': 'The ancient teachings describe various forms of spiritual discipline.',
                'source': 'Ancient Wisdom',
                'score': 0.8
            }
        ]
    
    def test_grounding_verifier_initialization(self):
        """Test grounding verifier initialization"""
        self.assertIsInstance(self.grounding_verifier.min_overlap_ratio, float)
        self.assertIsInstance(self.grounding_verifier.min_tokens, int)
        self.assertIn('EN', self.grounding_verifier.stopwords)
        self.assertIn('HI', self.grounding_verifier.stopwords)
    
    def test_grounding_verification_success(self):
        """Test successful grounding verification"""
        # Text with good overlap
        grounded_text = "Meditation is a spiritual practice that brings peace and wisdom to practitioners."
        
        result = self.grounding_verifier.verify_grounding(grounded_text, self.sample_chunks)
        
        self.assertIn('grounded', result)
        self.assertIn('score', result)
        self.assertIn('overlapping_tokens', result)
        self.assertIn('chunk_coverage', result)
        
        self.assertIsInstance(result['grounded'], bool)
        self.assertIsInstance(result['score'], (int, float))
        self.assertGreaterEqual(result['score'], 0.0)
        self.assertLessEqual(result['score'], 1.0)
    
    def test_grounding_verification_failure(self):
        """Test grounding verification failure"""
        # Text with no overlap
        ungrounded_text = "Cooking recipes involve various ingredients and preparation methods."
        
        result = self.grounding_verifier.verify_grounding(ungrounded_text, self.sample_chunks)
        
        self.assertFalse(result['grounded'])
        self.assertLessEqual(result['score'], 0.5)
    
    def test_sentence_grounding(self):
        """Test sentence-level grounding check"""
        grounded_sentence = "Meditation brings inner peace."
        ungrounded_sentence = "Cooking involves chopping vegetables."
        
        grounded_result = self.grounding_verifier.check_sentence_grounding(
            grounded_sentence, self.sample_chunks
        )
        ungrounded_result = self.grounding_verifier.check_sentence_grounding(
            ungrounded_sentence, self.sample_chunks
        )
        
        self.assertTrue(grounded_result)
        self.assertFalse(ungrounded_result)
    
    def test_sentence_by_sentence_verification(self):
        """Test sentence-by-sentence grounding verification"""
        mixed_text = "Meditation brings peace. Cooking involves vegetables. Spiritual practice leads to wisdom."
        
        result = self.grounding_verifier.verify_sentence_by_sentence(mixed_text, self.sample_chunks)
        
        self.assertIn('all_sentences_grounded', result)
        self.assertIn('grounded_sentences', result)
        self.assertIn('total_sentences', result)
        self.assertIn('sentence_details', result)
        
        # Should have some grounded and some ungrounded sentences
        self.assertGreater(result['total_sentences'], 0)
        self.assertGreater(result['grounded_sentences'], 0)
    
    def test_grounding_improvement(self):
        """Test grounding improvement functionality"""
        poorly_grounded_text = "Some general text about topics."
        
        improved_text = self.grounding_verifier.improve_grounding(
            poorly_grounded_text, self.sample_chunks
        )
        
        self.assertIsInstance(improved_text, str)
        self.assertGreaterEqual(len(improved_text), len(poorly_grounded_text))
    
    def test_empty_inputs(self):
        """Test handling of empty inputs"""
        result = self.grounding_verifier.verify_grounding("", [])
        
        self.assertFalse(result['grounded'])
        self.assertEqual(result['score'], 0.0)
        self.assertIn('error', result)

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete composer system"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.sample_chunks = [
            {
                'text': 'According to the Bhagavad Gita, meditation is essential for spiritual growth and inner peace.',
                'source': 'Bhagavad Gita 6.19',
                'score': 0.95,
                'sentences': [
                    {'s': 'According to the Bhagavad Gita, meditation is essential for spiritual growth and inner peace.', 'start': 0, 'end': 90}
                ]
            },
            {
                'text': 'The Upanishads teach that self-realization comes through disciplined practice and wisdom.',
                'source': 'Katha Upanishad',
                'score': 0.88,
                'sentences': [
                    {'s': 'The Upanishads teach that self-realization comes through disciplined practice and wisdom.', 'start': 0, 'end': 84}
                ]
            }
        ]
    
    def test_end_to_end_composition(self):
        """Test complete end-to-end composition process"""
        result = compose(
            trace_id="integration_test_001",
            extractive_answer="Meditation leads to spiritual growth through regular practice.",
            top_chunks=self.sample_chunks,
            lang="EN"
        )
        
        # Verify all required components work together
        self.assertIn('final_text', result)
        self.assertIn('grounded', result)
        self.assertIn('template_id', result)
        self.assertIn('citations', result)
        
        # Check that grounding works
        final_text = result['final_text']
        self.assertIsInstance(final_text, str)
        self.assertGreater(len(final_text), len("Meditation leads to spiritual growth through regular practice."))
        
        # Should have reasonable grounding
        if result['grounded']:
            self.assertGreater(result['grounding_score'], 0.3)
    
    def test_fallback_behavior(self):
        """Test system fallback behavior with problematic inputs"""
        # Test with minimal chunks
        minimal_chunks = [{'text': 'Short text.', 'source': 'Test'}]
        
        result = compose(
            trace_id="fallback_test_001",
            extractive_answer="Some answer.",
            top_chunks=minimal_chunks,
            lang="EN"
        )
        
        # Should still produce result
        self.assertIn('final_text', result)
        self.assertIsInstance(result['final_text'], str)
    
    def test_api_signature_compliance(self):
        """Test that the API signature matches requirements"""
        # Test the exact signature specified: compose(trace_id, extractive_answer, top_chunks, lang)
        result = compose(
            "test_trace_123",
            "Test answer",
            self.sample_chunks,
            "EN"
        )
        
        # Should return expected fields as per requirements
        required_fields = ['trace_id', 'final_text', 'template_id', 'grounded']
        for field in required_fields:
            self.assertIn(field, result)
        
        # Trace ID should be preserved
        self.assertEqual(result['trace_id'], "test_trace_123")

def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestComposer,
        TestTemplateEngine,
        TestNGramScorer,
        TestGRUStub,
        TestGroundingVerifier,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)