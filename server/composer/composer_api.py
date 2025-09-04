"""
Composer API endpoint for Uniguru-LM
Integrates with existing Express.js server via Python subprocess
"""

import sys
import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_compose_request(args: list) -> Dict[str, Any]:
    """
    Handle compose request from Node.js server
    
    Args:
        args: Command line arguments [trace_id, extractive_answer, top_chunks_json, lang]
        
    Returns:
        Composition result as dictionary
    """
    try:
        if len(args) < 4:
            raise ValueError("Insufficient arguments. Expected: trace_id, extractive_answer, top_chunks_json, lang")
        
        trace_id = args[0]
        extractive_answer = args[1]
        top_chunks_json = args[2]
        lang = args[3] if len(args) > 3 else "EN"
        
        # Parse chunks JSON
        try:
            top_chunks = json.loads(top_chunks_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON for top_chunks: {str(e)}")
        
        # Import and use composer
        from composer.compose import compose
        
        # Perform composition
        result = compose(
            trace_id=trace_id,
            extractive_answer=extractive_answer,
            top_chunks=top_chunks,
            lang=lang
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Compose request failed: {str(e)}")
        return {
            'error': str(e),
            'trace_id': args[0] if args else 'unknown',
            'final_text': args[1] if len(args) > 1 else '',
            'grounded': False,
            'score': 0.0
        }

def main():
    """Main entry point for CLI usage"""
    try:
        # Get arguments from command line
        args = sys.argv[1:]
        
        if not args:
            print(json.dumps({
                'error': 'No arguments provided',
                'usage': 'python composer_api.py <trace_id> <extractive_answer> <top_chunks_json> [lang]'
            }))
            sys.exit(1)
        
        # Handle request
        result = handle_compose_request(args)
        
        # Output result as JSON
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            'error': str(e),
            'trace_id': 'unknown',
            'final_text': '',
            'grounded': False,
            'score': 0.0
        }
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == '__main__':
    main()