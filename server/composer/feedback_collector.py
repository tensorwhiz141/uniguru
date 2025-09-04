"""
Feedback Collection System for Uniguru-LM Composer
Handles user feedback for RL training and system improvement
"""

import logging
import json
import time
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from .rl_policy import get_rl_policy, calculate_reward

logger = logging.getLogger(__name__)

@dataclass
class FeedbackRecord:
    """Data class for feedback record"""
    trace_id: str
    user_id: Optional[str]
    timestamp: float
    rating: int  # 1-5 scale
    feedback_type: str  # 'quality', 'relevance', 'accuracy', 'helpfulness'
    comments: Optional[str]
    metadata: Dict[str, Any]

class FeedbackCollector:
    """
    Collects and processes user feedback for RL training
    Integrates with RL policy to improve template selection
    """
    
    def __init__(self, feedback_dir: str = "composer/feedback"):
        self.feedback_dir = feedback_dir
        self.feedback_records = []
        self.rl_policy = get_rl_policy()
        
        # Create feedback directory
        os.makedirs(feedback_dir, exist_ok=True)
        
        # Feedback log file
        self.feedback_log_path = os.path.join(
            feedback_dir, 
            f"feedback_{datetime.now().strftime('%Y%m%d')}.jsonl"
        )
    
    def collect_feedback(self, trace_id: str, user_id: Optional[str], 
                        feedback_data: Dict[str, Any]) -> bool:
        """
        Collect user feedback for a composition
        
        Args:
            trace_id: Unique identifier for the composition
            user_id: User providing feedback (optional)
            feedback_data: Feedback information
            
        Returns:
            Success status
        """
        try:
            # Validate feedback data
            if not self._validate_feedback(feedback_data):
                logger.error(f"Invalid feedback data for trace_id: {trace_id}")
                return False
            
            # Create feedback record
            feedback_record = FeedbackRecord(
                trace_id=trace_id,
                user_id=user_id,
                timestamp=time.time(),
                rating=feedback_data.get('rating', 3),
                feedback_type=feedback_data.get('type', 'quality'),
                comments=feedback_data.get('comments'),
                metadata=feedback_data.get('metadata', {})
            )
            
            # Store feedback
            self.feedback_records.append(feedback_record)
            
            # Log to file
            self._log_feedback_to_file(feedback_record)
            
            # Update RL policy with feedback
            self._update_rl_policy_with_feedback(feedback_record)
            
            logger.info(f"Feedback collected for trace_id: {trace_id}, rating: {feedback_record.rating}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to collect feedback: {str(e)}")
            return False
    
    def get_feedback_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get feedback summary for the last N days"""
        try:
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            recent_feedback = [
                f for f in self.feedback_records 
                if f.timestamp >= cutoff_time
            ]
            
            if not recent_feedback:
                return {
                    'total_feedback': 0,
                    'average_rating': 0.0,
                    'rating_distribution': {},
                    'feedback_types': {}
                }
            
            # Calculate metrics
            total_feedback = len(recent_feedback)
            average_rating = sum(f.rating for f in recent_feedback) / total_feedback
            
            # Rating distribution
            rating_dist = {}
            for i in range(1, 6):
                rating_dist[str(i)] = sum(1 for f in recent_feedback if f.rating == i)
            
            # Feedback types
            type_dist = {}
            for feedback in recent_feedback:
                type_dist[feedback.feedback_type] = type_dist.get(feedback.feedback_type, 0) + 1
            
            return {
                'total_feedback': total_feedback,
                'average_rating': round(average_rating, 2),
                'rating_distribution': rating_dist,
                'feedback_types': type_dist,
                'days_analyzed': days,
                'high_satisfaction_rate': sum(1 for f in recent_feedback if f.rating >= 4) / total_feedback
            }
            
        except Exception as e:
            logger.error(f"Failed to generate feedback summary: {str(e)}")
            return {'error': str(e)}
    
    def get_feedback_for_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get feedback for specific trace"""
        for feedback in self.feedback_records:
            if feedback.trace_id == trace_id:
                return asdict(feedback)
        return None
    
    def export_feedback_for_training(self, output_path: str, min_rating: int = 1) -> int:
        """Export feedback data for ML training"""
        try:
            training_data = []
            
            for feedback in self.feedback_records:
                if feedback.rating >= min_rating:
                    training_record = {
                        'trace_id': feedback.trace_id,
                        'rating': feedback.rating,
                        'feedback_type': feedback.feedback_type,
                        'normalized_rating': (feedback.rating - 1) / 4,  # 0-1 scale
                        'timestamp': feedback.timestamp,
                        'has_comments': feedback.comments is not None,
                        'comment_length': len(feedback.comments) if feedback.comments else 0
                    }
                    training_data.append(training_record)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(training_data)} feedback records for training")
            return len(training_data)
            
        except Exception as e:
            logger.error(f"Failed to export feedback for training: {str(e)}")
            return 0
    
    def _validate_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Validate feedback data"""
        # Check required fields
        if 'rating' not in feedback_data:
            return False
        
        # Validate rating range
        rating = feedback_data['rating']
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return False
        
        # Validate feedback type if provided
        valid_types = ['quality', 'relevance', 'accuracy', 'helpfulness', 'overall']
        feedback_type = feedback_data.get('type', 'quality')
        if feedback_type not in valid_types:
            return False
        
        return True
    
    def _log_feedback_to_file(self, feedback_record: FeedbackRecord):
        """Log feedback to file"""
        try:
            feedback_dict = asdict(feedback_record)
            feedback_dict['datetime'] = datetime.fromtimestamp(feedback_record.timestamp).isoformat()
            
            with open(self.feedback_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(feedback_dict, ensure_ascii=False) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to log feedback to file: {str(e)}")
    
    def _update_rl_policy_with_feedback(self, feedback_record: FeedbackRecord):
        """Update RL policy with feedback"""
        try:
            # Calculate reward from feedback
            feedback_reward = self._calculate_feedback_reward(feedback_record)
            
            # Note: In a full implementation, we would retrieve the original
            # composition result and action metadata for this trace_id
            # For now, we'll create a simplified update
            
            # Create dummy action metadata (in real implementation, this would be retrieved)
            action_metadata = {
                'trace_id': feedback_record.trace_id,
                'action': 'unknown',  # Would be retrieved from trace
                'context_key': 'default',
                'timestamp': feedback_record.timestamp
            }
            
            # Update policy with feedback reward
            self.rl_policy.update_policy(
                trace_id=feedback_record.trace_id,
                action_metadata=action_metadata,
                reward=feedback_reward,
                final_state={'feedback_rating': feedback_record.rating}
            )
            
            logger.info(f"RL policy updated with feedback reward: {feedback_reward:.3f}")
            
        except Exception as e:
            logger.error(f"Failed to update RL policy with feedback: {str(e)}")
    
    def _calculate_feedback_reward(self, feedback_record: FeedbackRecord) -> float:
        """Calculate reward from feedback"""
        # Simple mapping: 1-5 rating to 0-1 reward
        base_reward = (feedback_record.rating - 1) / 4
        
        # Bonus for detailed feedback (comments)
        if feedback_record.comments and len(feedback_record.comments) > 10:
            base_reward += 0.1
        
        # Penalty for very negative feedback
        if feedback_record.rating == 1:
            base_reward -= 0.1
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, base_reward))

# Global feedback collector instance
_feedback_collector = None

def get_feedback_collector() -> FeedbackCollector:
    """Get singleton feedback collector instance"""
    global _feedback_collector
    if _feedback_collector is None:
        _feedback_collector = FeedbackCollector()
    return _feedback_collector

def collect_user_feedback(trace_id: str, user_id: Optional[str], 
                         feedback_data: Dict[str, Any]) -> bool:
    """Convenience function to collect user feedback"""
    collector = get_feedback_collector()
    return collector.collect_feedback(trace_id, user_id, feedback_data)