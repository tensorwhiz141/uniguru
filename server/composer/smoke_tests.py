"""
Smoke Test Suite for Uniguru-LM Composer
Tests 10 queries (EN + HI) to validate end-to-end functionality
As per Day 2 requirements: confirm final_text, citations, audio readiness, feedback flow, grounding >90%
"""

import json
import time
import sys
import os
from typing import Dict, List, Any, Tuple

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from composer.compose import compose
from composer.feedback_collector import collect_user_feedback
from composer.performance_monitor_clean import get_performance_monitor

class SmokeTestRunner:
    """Runs smoke tests for composer system validation"""
    
    def __init__(self):
        self.test_results = []
        self.performance_monitor = get_performance_monitor()
        
    def run_smoke_tests(self) -> Dict[str, Any]:
        """Run complete smoke test suite"""
        print("🔥 Starting Uniguru-LM Composer Smoke Tests")
        print("=" * 60)
        
        # Test cases: 5 English + 5 Hindi
        test_cases = self._get_test_cases()
        
        results = {
            'total_tests': len(test_cases),
            'passed_tests': 0,
            'failed_tests': 0,
            'grounding_success_rate': 0.0,
            'test_details': [],
            'summary': {},
            'timestamp': time.time()
        }
        
        grounded_count = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}/{len(test_cases)}: {test_case['name']}")
            print("-" * 40)
            
            try:
                # Run composition
                start_time = time.time()
                result = compose(
                    trace_id=test_case['trace_id'],
                    extractive_answer=test_case['extractive_answer'],
                    top_chunks=test_case['top_chunks'],
                    lang=test_case['lang']
                )
                test_time = time.time() - start_time
                
                # Validate result
                validation_result = self._validate_composition_result(result, test_case)
                
                # Test feedback flow
                feedback_result = self._test_feedback_flow(test_case['trace_id'])
                
                # Count grounding success
                if result.get('grounded', False):
                    grounded_count += 1
                
                # Record test result
                test_detail = {
                    'test_name': test_case['name'],
                    'test_id': i,
                    'trace_id': test_case['trace_id'],
                    'lang': test_case['lang'],
                    'passed': validation_result['passed'],
                    'grounded': result.get('grounded', False),
                    'grounding_score': result.get('grounding_score', 0.0),
                    'composition_time_ms': result.get('composition_time_ms', 0.0),
                    'template_id': result.get('template_id', 'unknown'),
                    'rl_action': result.get('rl_action', 'unknown'),
                    'final_text_length': len(result.get('final_text', '')),
                    'citations_count': len(result.get('citations', [])),
                    'validation_details': validation_result,
                    'feedback_test': feedback_result,
                    'test_time_ms': round(test_time * 1000, 2)
                }
                
                results['test_details'].append(test_detail)
                
                if validation_result['passed']:
                    results['passed_tests'] += 1
                    print(f"✅ PASS - {test_case['name']}")
                else:
                    results['failed_tests'] += 1
                    print(f"❌ FAIL - {test_case['name']}")
                
                # Print key metrics
                print(f"   Grounded: {result.get('grounded', False)}")
                print(f"   Score: {result.get('grounding_score', 0.0):.3f}")
                print(f"   Template: {result.get('template_id', 'unknown')}")
                print(f"   Time: {result.get('composition_time_ms', 0.0):.1f}ms")
                print(f"   Citations: {len(result.get('citations', []))}")
                
            except Exception as e:
                print(f"❌ ERROR - {test_case['name']}: {str(e)}")
                results['failed_tests'] += 1
                results['test_details'].append({
                    'test_name': test_case['name'],
                    'test_id': i,
                    'passed': False,
                    'error': str(e)
                })
        
        # Calculate final metrics
        results['grounding_success_rate'] = grounded_count / len(test_cases)
        results['success_rate'] = results['passed_tests'] / len(test_cases)
        
        # Generate summary
        results['summary'] = self._generate_test_summary(results)
        
        # Save results
        self._save_test_results(results)
        
        return results
    
    def _get_test_cases(self) -> List[Dict[str, Any]]:
        """Get test cases for smoke testing"""
        return [
            # English test cases
            {
                'name': 'EN: Meditation and Peace',
                'trace_id': 'smoke_test_en_001',
                'extractive_answer': 'Meditation brings inner peace and spiritual growth through regular practice.',
                'top_chunks': [
                    {
                        'text': 'According to the Bhagavad Gita, meditation is a powerful practice that leads to inner peace and self-realization through disciplined practice.',
                        'source': 'Bhagavad Gita 6.19',
                        'score': 0.95
                    },
                    {
                        'text': 'The Upanishads teach that meditation helps achieve spiritual growth and wisdom by calming the mind and connecting with the divine.',
                        'source': 'Katha Upanishad 2.3.10',
                        'score': 0.88
                    }
                ],
                'lang': 'EN'
            },
            {
                'name': 'EN: Dharma and Righteous Living',
                'trace_id': 'smoke_test_en_002',
                'extractive_answer': 'Dharma represents righteous living and moral conduct in all aspects of life.',
                'top_chunks': [
                    {
                        'text': 'Dharma is the foundation of righteous living, encompassing duty, morality, and ethical conduct as prescribed in the sacred texts.',
                        'source': 'Dharma Shastra',
                        'score': 0.92
                    },
                    {
                        'text': 'Living according to dharma ensures harmony in society and personal spiritual development.',
                        'source': 'Mahabharata',
                        'score': 0.85
                    }
                ],
                'lang': 'EN'
            },
            {
                'name': 'EN: Yoga and Union',
                'trace_id': 'smoke_test_en_003',
                'extractive_answer': 'Yoga means union and connects the individual soul with the universal consciousness.',
                'top_chunks': [
                    {
                        'text': 'Yoga literally means union, representing the connection between individual consciousness and universal consciousness.',
                        'source': 'Patanjali Yoga Sutras 1.2',
                        'score': 0.94
                    },
                    {
                        'text': 'Through yoga practice, one achieves balance of body, mind, and spirit.',
                        'source': 'Hatha Yoga Pradipika',
                        'score': 0.89
                    }
                ],
                'lang': 'EN'
            },
            {
                'name': 'EN: Knowledge and Devotion',
                'trace_id': 'smoke_test_en_004',
                'extractive_answer': 'Both knowledge and devotion are essential paths to spiritual realization.',
                'top_chunks': [
                    {
                        'text': 'The path of knowledge (jnana yoga) leads to understanding the true nature of reality.',
                        'source': 'Advaita Vedanta',
                        'score': 0.90
                    },
                    {
                        'text': 'The path of devotion (bhakti yoga) purifies the heart through love and surrender to the divine.',
                        'source': 'Bhakti Sutras',
                        'score': 0.87
                    }
                ],
                'lang': 'EN'
            },
            {
                'name': 'EN: Service and Selflessness',
                'trace_id': 'smoke_test_en_005',
                'extractive_answer': 'Service to others is a spiritual practice that cultivates selflessness.',
                'top_chunks': [
                    {
                        'text': 'Selfless service (seva) is a path to spiritual growth that dissolves the ego and cultivates compassion.',
                        'source': 'Karma Yoga Teachings',
                        'score': 0.91
                    },
                    {
                        'text': 'When we serve others without expectation, we connect with the divine presence in all beings.',
                        'source': 'Bhagavad Gita 3.19',
                        'score': 0.86
                    }
                ],
                'lang': 'EN'
            },
            
            # Hindi test cases
            {
                'name': 'HI: ध्यान और शांति',
                'trace_id': 'smoke_test_hi_001',
                'extractive_answer': 'ध्यान से आंतरिक शांति और आध्यात्मिक विकास होता है।',
                'top_chunks': [
                    {
                        'text': 'भगवद्गीता के अनुसार, ध्यान एक शक्तिशाली अभ्यास है जो आंतरिक शांति और आत्म-साक्षात्कार की ओर ले जाता है।',
                        'source': 'भगवद्गीता ६.१९',
                        'score': 0.95
                    },
                    {
                        'text': 'उपनिषदों में कहा गया है कि ध्यान से मन की शांति और दिव्य चेतना से जुड़ाव होता है।',
                        'source': 'कठोपनिषद २.३.१०',
                        'score': 0.88
                    }
                ],
                'lang': 'HI'
            },
            {
                'name': 'HI: धर्म और नैतिक आचरण',
                'trace_id': 'smoke_test_hi_002',
                'extractive_answer': 'धर्म का अर्थ है नैतिक आचरण और जीवन में सदाचार।',
                'top_chunks': [
                    {
                        'text': 'धर्म जीवन का आधार है जो कर्तव्य, नैतिकता और सदाचार को दर्शाता है।',
                        'source': 'धर्मशास्त्र',
                        'score': 0.92
                    },
                    {
                        'text': 'धर्म के अनुसार जीने से समाज में शांति और व्यक्तिगत आध्यात्मिक विकास होता है।',
                        'source': 'महाभारत',
                        'score': 0.85
                    }
                ],
                'lang': 'HI'
            },
            {
                'name': 'HI: योग और एकता',
                'trace_id': 'smoke_test_hi_003',
                'extractive_answer': 'योग का अर्थ है मिलन - व्यक्तिगत चेतना का सार्वभौमिक चेतना से।',
                'top_chunks': [
                    {
                        'text': 'योग का शाब्दिक अर्थ है मिलन, जो व्यक्तिगत चेतना और सार्वभौमिक चेतना के बीच संबंध दर्शाता है।',
                        'source': 'पतंजलि योग सूत्र १.२',
                        'score': 0.94
                    },
                    {
                        'text': 'योग अभ्यास से शरीर, मन और आत्मा का संतुलन प्राप्त होता है।',
                        'source': 'हठयोग प्रदीपिका',
                        'score': 0.89
                    }
                ],
                'lang': 'HI'
            },
            {
                'name': 'HI: ज्ञान और भक्ति',
                'trace_id': 'smoke_test_hi_004',
                'extractive_answer': 'ज्ञान और भक्ति दोनों आध्यात्मिक साक्षात्कार के लिए आवश्यक हैं।',
                'top_chunks': [
                    {
                        'text': 'ज्ञान योग का मार्ग सत्य की वास्तविक प्रकृति को समझने में सहायक है।',
                        'source': 'अद्वैत वेदांत',
                        'score': 0.90
                    },
                    {
                        'text': 'भक्ति योग का मार्ग प्रेम और समर्पण के द्वारा हृदय को शुद्ध करता है।',
                        'source': 'भक्ति सूत्र',
                        'score': 0.87
                    }
                ],
                'lang': 'HI'
            },
            {
                'name': 'HI: सेवा और निःस्वार्थता',
                'trace_id': 'smoke_test_hi_005',
                'extractive_answer': 'दूसरों की सेवा एक आध्यात्मिक अभ्यास है जो निःस्वार्थता विकसित करती है।',
                'top_chunks': [
                    {
                        'text': 'निःस्वार्थ सेवा (सेवा) आध्यात्मिक विकास का मार्ग है जो अहंकार को घटाती है और करुणा बढ़ाती है।',
                        'source': 'कर्म योग शिक्षा',
                        'score': 0.91
                    },
                    {
                        'text': 'जब हम बिना अपेक्षा के सेवा करते हैं, तो हम सभी जीवों में दिव्य उपस्थिति से जुड़ते हैं।',
                        'source': 'भगवद्गीता ३.१९',
                        'score': 0.86
                    }
                ],
                'lang': 'HI'
            }
        ]
    
    def _validate_composition_result(self, result: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Validate composition result against requirements"""
        validation = {
            'passed': True,
            'checks': {},
            'issues': []
        }
        
        # Check 1: final_text present and non-empty
        final_text = result.get('final_text', '')
        validation['checks']['final_text_present'] = bool(final_text)
        if not final_text:
            validation['passed'] = False
            validation['issues'].append('Missing or empty final_text')
        
        # Check 2: citations present
        citations = result.get('citations', [])
        validation['checks']['citations_present'] = len(citations) > 0
        if not citations:
            validation['passed'] = False
            validation['issues'].append('Missing citations')
        
        # Check 3: grounding status available
        grounded = result.get('grounded')
        validation['checks']['grounding_status'] = grounded is not None
        if grounded is None:
            validation['passed'] = False
            validation['issues'].append('Missing grounding status')
        
        # Check 4: trace_id preserved
        trace_id_match = result.get('trace_id') == test_case['trace_id']
        validation['checks']['trace_id_preserved'] = trace_id_match
        if not trace_id_match:
            validation['passed'] = False
            validation['issues'].append('Trace ID not preserved')
        
        # Check 5: template_id present
        template_id = result.get('template_id', '')
        validation['checks']['template_id_present'] = bool(template_id)
        if not template_id:
            validation['passed'] = False
            validation['issues'].append('Missing template_id')
        
        # Check 6: reasonable composition time
        comp_time = result.get('composition_time_ms', 0)
        validation['checks']['reasonable_time'] = comp_time < 5000  # < 5 seconds
        if comp_time >= 5000:
            validation['passed'] = False
            validation['issues'].append(f'Composition time too high: {comp_time}ms')
        
        # Check 7: RL metadata present
        rl_action = result.get('rl_action')
        validation['checks']['rl_action_present'] = bool(rl_action)
        if not rl_action:
            validation['issues'].append('Missing RL action metadata')
        
        return validation
    
    def _test_feedback_flow(self, trace_id: str) -> Dict[str, Any]:
        """Test feedback collection flow"""
        try:
            # Simulate user feedback
            feedback_data = {
                'rating': 4,
                'type': 'quality',
                'comments': 'Good composition quality for smoke test'
            }
            
            success = collect_user_feedback(trace_id, 'smoke_test_user', feedback_data)
            
            return {
                'feedback_collection_success': success,
                'feedback_data': feedback_data
            }
            
        except Exception as e:
            return {
                'feedback_collection_success': False,
                'error': str(e)
            }
    
    def _generate_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test summary"""
        test_details = results['test_details']
        
        # Language breakdown
        en_tests = [t for t in test_details if t.get('lang') == 'EN']
        hi_tests = [t for t in test_details if t.get('lang') == 'HI']
        
        en_passed = sum(1 for t in en_tests if t.get('passed', False))
        hi_passed = sum(1 for t in hi_tests if t.get('passed', False))
        
        # Performance metrics
        avg_time = sum(t.get('composition_time_ms', 0) for t in test_details) / len(test_details)
        avg_grounding_score = sum(t.get('grounding_score', 0) for t in test_details) / len(test_details)
        
        # Template usage
        template_usage = {}
        for test in test_details:
            template = test.get('template_id', 'unknown')
            template_usage[template] = template_usage.get(template, 0) + 1
        
        return {
            'overall_success_rate': results['success_rate'],
            'grounding_success_rate': results['grounding_success_rate'],
            'language_breakdown': {
                'english': {'total': len(en_tests), 'passed': en_passed, 'success_rate': en_passed / max(1, len(en_tests))},
                'hindi': {'total': len(hi_tests), 'passed': hi_passed, 'success_rate': hi_passed / max(1, len(hi_tests))}
            },
            'performance_metrics': {
                'avg_composition_time_ms': round(avg_time, 2),
                'avg_grounding_score': round(avg_grounding_score, 3),
                'min_time_ms': min(t.get('composition_time_ms', 0) for t in test_details),
                'max_time_ms': max(t.get('composition_time_ms', 0) for t in test_details)
            },
            'template_usage': template_usage,
            'grounding_requirement_met': results['grounding_success_rate'] >= 0.9
        }
    
    def _save_test_results(self, results: Dict[str, Any]):
        """Save test results to file"""
        try:
            os.makedirs('composer/test_results', exist_ok=True)
            
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            results_file = f'composer/test_results/smoke_test_results_{timestamp}.json'
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\n📊 Test results saved to: {results_file}")
            
        except Exception as e:
            print(f"⚠️  Failed to save test results: {str(e)}")

def main():
    """Run smoke tests"""
    runner = SmokeTestRunner()
    results = runner.run_smoke_tests()
    
    # Print final summary
    print("\n" + "=" * 60)
    print("🎯 SMOKE TEST SUMMARY")
    print("=" * 60)
    
    summary = results['summary']
    
    print(f"Overall Success Rate: {results['success_rate']:.1%}")
    print(f"Grounding Success Rate: {results['grounding_success_rate']:.1%}")
    print(f"Tests Passed: {results['passed_tests']}/{results['total_tests']}")
    
    print(f"\nLanguage Breakdown:")
    print(f"  English: {summary['language_breakdown']['english']['passed']}/{summary['language_breakdown']['english']['total']} ({summary['language_breakdown']['english']['success_rate']:.1%})")
    print(f"  Hindi:   {summary['language_breakdown']['hindi']['passed']}/{summary['language_breakdown']['hindi']['total']} ({summary['language_breakdown']['hindi']['success_rate']:.1%})")
    
    print(f"\nPerformance:")
    print(f"  Avg Composition Time: {summary['performance_metrics']['avg_composition_time_ms']:.1f}ms")
    print(f"  Avg Grounding Score: {summary['performance_metrics']['avg_grounding_score']:.3f}")
    
    print(f"\nTemplate Usage:")
    for template, count in summary['template_usage'].items():
        print(f"  {template}: {count}")
    
    # Check requirements
    print(f"\n📋 Requirements Check:")
    req_met = "✅" if results['grounding_success_rate'] >= 0.9 else "❌"
    print(f"{req_met} Grounding >90%: {results['grounding_success_rate']:.1%}")
    
    req_met = "✅" if results['success_rate'] >= 0.8 else "❌"
    print(f"{req_met} Overall Success >80%: {results['success_rate']:.1%}")
    
    # Final verdict
    if results['grounding_success_rate'] >= 0.9 and results['success_rate'] >= 0.8:
        print("\n🎉 SMOKE TESTS PASSED - System ready for deployment!")
        return 0
    else:
        print("\n⚠️  SMOKE TESTS FAILED - Issues need to be resolved")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)