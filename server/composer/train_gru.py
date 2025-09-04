#!/usr/bin/env python3
"""
GRU Model Training Script for Uniguru-LM Composer

This script handles training of the GRU model for text enhancement.
It can be run independently or imported as a module.

Usage:
    python train_gru.py [--epochs 10] [--batch-size 32] [--data-path ./data/]
"""

import argparse
import logging
import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from composer.gru import GRUStub

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_training_data(data_path: str) -> list:
    """Load training data from various sources"""
    training_data = []
    
    # Try to load from JSON file
    json_path = os.path.join(data_path, 'training_data.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                training_data.extend(data)
                logger.info(f"Loaded {len(data)} samples from {json_path}")
        except Exception as e:
            logger.error(f"Failed to load training data from {json_path}: {str(e)}")
    
    # Try to load from text files
    txt_files = Path(data_path).glob('*.txt')
    for txt_file in txt_files:
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Simple format: alternating lines of input and target
                for i in range(0, len(lines) - 1, 2):
                    input_text = lines[i].strip()
                    target_text = lines[i + 1].strip()
                    if input_text and target_text:
                        training_data.append({
                            'input': input_text,
                            'target': target_text,
                            'source': str(txt_file)
                        })
            logger.info(f"Loaded {len(lines)//2} samples from {txt_file}")
        except Exception as e:
            logger.error(f"Failed to load from {txt_file}: {str(e)}")
    
    return training_data

def generate_synthetic_data() -> list:
    """Generate synthetic training data for demonstration"""
    logger.info("Generating synthetic training data...")
    
    synthetic_data = [
        {
            'input': "According to the texts, meditation helps achieve peace.",
            'target': "According to the sacred texts, meditation is a powerful practice that helps us achieve inner peace and spiritual growth. Through regular practice, one can develop deeper understanding.",
            'metadata': {'type': 'explanation', 'lang': 'EN'}
        },
        {
            'input': "Dharma is important for spiritual growth.",
            'target': "Dharma, as described in the ancient scriptures, is fundamental for spiritual growth. It represents righteous living and moral conduct that guides us toward liberation.",
            'metadata': {'type': 'explanation', 'lang': 'EN'}
        },
        {
            'input': "Yoga connects body and mind.",
            'target': "Yoga, as taught in the sacred traditions, creates a profound connection between body, mind, and spirit. This ancient practice offers a path to self-realization and inner harmony.",
            'metadata': {'type': 'explanation', 'lang': 'EN'}
        },
        {
            'input': "ध्यान से शांति मिलती है।",
            'target': "पवित्र ग्रंथों के अनुसार, ध्यान एक ऐसा अभ्यास है जो हमें आंतरिक शांति और आध्यात्मिक विकास प्रदान करता है। नियमित अभ्यास से गहरी समझ विकसित होती है।",
            'metadata': {'type': 'explanation', 'lang': 'HI'}
        },
        {
            'input': "करुणा सभी धर्मों में महत्वपूर्ण है।",
            'target': "शास्त्रों के अनुसार, करुणा सभी आध्यात्मिक परंपराओं का केंद्रीय सिद्धांत है। यह दिव्य प्रेम की अभिव्यक्ति है और मोक्ष के पथ पर आवश्यक गुण है।",
            'metadata': {'type': 'explanation', 'lang': 'HI'}
        },
        {
            'input': "Knowledge and devotion are both important.",
            'target': "The sacred teachings reveal that both knowledge (jnana) and devotion (bhakti) are essential paths to spiritual realization. While knowledge illuminates the truth, devotion purifies the heart.",
            'metadata': {'type': 'comparison', 'lang': 'EN'}
        },
        {
            'input': "Service to others is spiritual practice.",
            'target': "As exemplified in the scriptures, service to others (seva) is a powerful spiritual practice. For instance, when we serve without expectation of reward, we cultivate selflessness and connect with the divine.",
            'metadata': {'type': 'example', 'lang': 'EN'}
        },
        {
            'input': "Self-control leads to freedom.",
            'target': "The ancient wisdom teaches that self-control (self-restraint) paradoxically leads to true freedom. By mastering our desires and impulses, we break free from the bondage of conditioning and achieve liberation.",
            'metadata': {'type': 'explanation', 'lang': 'EN'}
        }
    ]
    
    logger.info(f"Generated {len(synthetic_data)} synthetic training samples")
    return synthetic_data

def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description='Train GRU model for Uniguru-LM composer')
    parser.add_argument('--epochs', type=int, default=10, help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=32, help='Training batch size')
    parser.add_argument('--data-path', type=str, default='./composer/data/', help='Path to training data')
    parser.add_argument('--synthetic', action='store_true', help='Use synthetic data for training')
    parser.add_argument('--model-path', type=str, default='composer/models/gru_model.pkl', help='Path to save model')
    
    args = parser.parse_args()
    
    logger.info("Starting GRU model training...")
    logger.info(f"Configuration: epochs={args.epochs}, batch_size={args.batch_size}")
    
    # Initialize GRU model
    gru_model = GRUStub(model_path=args.model_path)
    
    # Load or generate training data
    if args.synthetic:
        training_data = generate_synthetic_data()
    else:
        training_data = load_training_data(args.data_path)
        
        # If no data found, generate synthetic data as fallback
        if not training_data:
            logger.warning("No training data found, generating synthetic data...")
            training_data = generate_synthetic_data()
    
    if not training_data:
        logger.error("No training data available. Cannot proceed with training.")
        return 1
    
    # Add training data to model
    logger.info(f"Adding {len(training_data)} samples to training set...")
    for sample in training_data:
        gru_model.add_training_data(
            input_text=sample['input'],
            target_text=sample['target'],
            metadata=sample.get('metadata', {})
        )
    
    # Train the model
    logger.info("Starting model training...")
    training_result = gru_model.train_model(epochs=args.epochs, batch_size=args.batch_size)
    
    if training_result['success']:
        logger.info("Training completed successfully!")
        logger.info(f"Training metrics: {training_result['metrics']}")
        logger.info(f"Model saved to: {training_result['model_path']}")
        
        # Test the trained model
        logger.info("Testing trained model...")
        test_input = "Meditation brings peace to the mind."
        test_chunks = [{'text': 'Sacred texts describe meditation as a path to inner peace.', 'source': 'Test Source'}]
        enhanced_output = gru_model.enhance_text(test_input, test_chunks, 'EN')
        
        logger.info(f"Test input: {test_input}")
        logger.info(f"Enhanced output: {enhanced_output}")
        
        return 0
    else:
        logger.error(f"Training failed: {training_result['message']}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)