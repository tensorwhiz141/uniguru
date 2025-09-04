#!/usr/bin/env python3
"""
Test script for Composer API
Tests the complete composer functionality
"""

import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from composer.compose import compose

def test_composer_api():
    """Test the composer API functionality"""
    
    print("Testing Uniguru-LM Composer...")
    print("=" * 50)
    
    # Test data
    test_cases = [
        {
            "name": "English Spiritual Content",
            "trace_id": "test_en_001",
            "extractive_answer": "Meditation brings inner peace and spiritual growth through regular practice.",
            "top_chunks": [
                {
                    "text": "According to the Bhagavad Gita, meditation is a powerful practice that leads to inner peace and self-realization.",
                    "source": "Bhagavad Gita 6.19",
                    "score": 0.95
                },
                {
                    "text": "The Upanishads teach that regular meditation practice helps achieve spiritual growth and wisdom.",
                    "source": "Katha Upanishad",
                    "score": 0.88
                }
            ],
            "lang": "EN"
        },
        {
            "name": "Hindi Spiritual Content", 
            "trace_id": "test_hi_001",
            "extractive_answer": "ध्यान से आंतरिक शांति और आध्यात्मिक विकास होता है।",
            "top_chunks": [
                {
                    "text": "भगवद्गीता के अनुसार, ध्यान एक शक्तिशाली अभ्यास है जो आंतरिक शांति लाता है।",
                    "source": "भगवद्गीता ६.१९",
                    "score": 0.95
                },
                {
                    "text": "उपनिषदों में कहा गया है कि नियमित ध्यान से आध्यात्मिक विकास होता है।",
                    "source": "कठोपनिषद",
                    "score": 0.88
                }
            ],
            "lang": "HI"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\nTest Case: {test_case['name']}")
        print("-" * 30)
        
        try:
            # Call composer
            result = compose(
                trace_id=test_case['trace_id'],
                extractive_answer=test_case['extractive_answer'],
                top_chunks=test_case['top_chunks'],
                lang=test_case['lang']
            )
            
            # Display results
            print(f"✓ Trace ID: {result['trace_id']}")
            print(f"✓ Template ID: {result['template_id']}")
            print(f"✓ Grounded: {result['grounded']}")
            print(f"✓ Grounding Score: {result['grounding_score']:.3f}")
            print(f"✓ Composition Time: {result['composition_time_ms']}ms")
            print(f"✓ Method: {result['method']}")
            
            print(f"\nInput: {test_case['extractive_answer']}")
            print(f"\nComposed Text:\n{result['final_text']}")
            
            if result['citations']:
                print(f"\nCitations: {len(result['citations'])} sources")
                for i, citation in enumerate(result['citations'], 1):
                    print(f"  [{i}] {citation['source']}")
            
            results.append({
                'test_case': test_case['name'],
                'success': True,
                'grounded': result['grounded'],
                'score': result['grounding_score']
            })
            
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")
            results.append({
                'test_case': test_case['name'],
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    for result in results:
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        print(f"{status} - {result['test_case']}")
        if result['success']:
            print(f"    Grounded: {result['grounded']}, Score: {result['score']:.3f}")
        else:
            print(f"    Error: {result.get('error', 'Unknown error')}")
    
    return passed == total

if __name__ == '__main__':
    success = test_composer_api()
    sys.exit(0 if success else 1)