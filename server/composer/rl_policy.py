"""
Reinforcement Learning Policy for Template Selection
Implements epsilon-greedy policy for template selection with reward tracking
"""

import logging
import json
import random
import time
import os
from typing import Dict, List, Tuple, Any, Optional
from enum import Enum
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class PolicyAction(Enum):
    """Template selection actions for RL policy"""
    EXPLAIN = "explain"
    COMPARE = "compare"
    EXAMPLE = "example"
    EXTRACTIVE = "extractive"

class RLPolicy:
    """
    Reinforcement Learning Policy for Template Selection
    
    Implements epsilon-greedy strategy with experience replay
    and reward-based template selection optimization
    """
    
    def __init__(self, epsilon: float = 0.1, learning_rate: float = 0.01, 
                 experience_buffer_size: int = 1000):
        """
        Initialize RL Policy
        
        Args:
            epsilon: Exploration rate for epsilon-greedy policy
            learning_rate: Learning rate for policy updates
            experience_buffer_size: Size of experience replay buffer
        """
        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.experience_buffer = deque(maxlen=experience_buffer_size)
        
        # Action-value estimates (Q-values)
        self.q_values = defaultdict(lambda: defaultdict(float))
        
        # Action counts for exploration
        self.action_counts = defaultdict(lambda: defaultdict(int))
        
        # Reward tracking
        self.reward_history = []
        self.action_history = []
        
        # Policy state
        self.total_actions = 0
        self.successful_actions = 0
        
        # Load existing policy if available
        self._load_policy()
    
    def select_action(self, context: Dict[str, Any]) -> Tuple[PolicyAction, Dict[str, Any]]:
        """
        Select template action using epsilon-greedy policy
        
        Args:
            context: Context features for action selection
            
        Returns:
            Tuple of (selected_action, action_metadata)
        """
        try:
            # Extract context features
            context_key = self._extract_context_key(context)
            
            # Epsilon-greedy action selection
            if random.random() < self.epsilon:
                # Exploration: random action
                action = random.choice(list(PolicyAction))
                selection_method = "exploration"
                logger.info(f"RL Policy: Exploration action selected - {action.value}")
            else:
                # Exploitation: best known action
                action = self._get_best_action(context_key)
                selection_method = "exploitation"
                logger.info(f"RL Policy: Exploitation action selected - {action.value}")
            
            # Track action
            self.action_counts[context_key][action.value] += 1
            self.total_actions += 1
            
            # Prepare action metadata
            action_metadata = {
                'action': action.value,
                'context_key': context_key,
                'selection_method': selection_method,
                'q_value': self.q_values[context_key][action.value],
                'action_count': self.action_counts[context_key][action.value],
                'epsilon': self.epsilon,
                'timestamp': time.time()
            }
            
            return action, action_metadata
            
        except Exception as e:
            logger.error(f"RL Policy action selection failed: {str(e)}")
            # Fallback to default action
            return PolicyAction.EXPLAIN, {
                'action': PolicyAction.EXPLAIN.value,
                'selection_method': 'fallback',
                'error': str(e)
            }
    
    def update_policy(self, trace_id: str, action_metadata: Dict[str, Any], 
                     reward: float, final_state: Dict[str, Any]):
        """
        Update policy based on received reward
        
        Args:
            trace_id: Unique identifier for the action
            action_metadata: Metadata from action selection
            reward: Reward signal (0.0 to 1.0)
            final_state: Final state after action execution
        """
        try:
            context_key = action_metadata.get('context_key', 'default')
            action = action_metadata.get('action', 'explain')
            
            # Update Q-value using simple temporal difference learning
            current_q = self.q_values[context_key][action]
            
            # TD update: Q(s,a) = Q(s,a) + α[r - Q(s,a)]
            new_q = current_q + self.learning_rate * (reward - current_q)
            self.q_values[context_key][action] = new_q
            
            # Track rewards
            self.reward_history.append(reward)
            self.action_history.append(action)
            
            # Update success tracking
            if reward > 0.7:  # Consider high rewards as successful
                self.successful_actions += 1
            
            # Store experience for replay
            experience = {
                'trace_id': trace_id,
                'context_key': context_key,
                'action': action,
                'reward': reward,
                'q_value_old': current_q,
                'q_value_new': new_q,
                'timestamp': time.time(),
                'final_state': final_state
            }
            
            self.experience_buffer.append(experience)
            
            # Adaptive epsilon decay
            self._update_epsilon()
            
            # Periodic policy save
            if len(self.experience_buffer) % 10 == 0:
                self._save_policy()
            
            logger.info(f"RL Policy updated: trace_id={trace_id}, action={action}, "
                       f"reward={reward:.3f}, new_q={new_q:.3f}")
            
        except Exception as e:
            logger.error(f"RL Policy update failed: {str(e)}")
    
    def _extract_context_key(self, context: Dict[str, Any]) -> str:
        """Extract context key for state representation"""
        # Simple context features for template selection
        extractive_length = len(context.get('extractive_answer', ''))
        chunk_count = len(context.get('top_chunks', []))
        lang = context.get('lang', 'EN')
        
        # Categorize context
        if extractive_length < 50:
            length_cat = 'short'
        elif extractive_length < 150:
            length_cat = 'medium'
        else:
            length_cat = 'long'
        
        if chunk_count <= 1:
            chunk_cat = 'single'
        elif chunk_count <= 3:
            chunk_cat = 'few'
        else:
            chunk_cat = 'many'
        
        # Create context key
        context_key = f"{lang}_{length_cat}_{chunk_cat}"
        return context_key
    
    def _get_best_action(self, context_key: str) -> PolicyAction:
        """Get best action for given context"""
        if context_key not in self.q_values:
            # No experience with this context, return default
            return PolicyAction.EXPLAIN
        
        # Find action with highest Q-value
        best_action = None
        best_q = float('-inf')
        
        for action_name, q_value in self.q_values[context_key].items():
            if q_value > best_q:
                best_q = q_value
                best_action = action_name
        
        if best_action:
            return PolicyAction(best_action)
        else:
            return PolicyAction.EXPLAIN
    
    def _update_epsilon(self):
        """Update epsilon for exploration-exploitation balance"""
        # Adaptive epsilon decay based on performance
        if len(self.reward_history) >= 10:
            recent_performance = sum(self.reward_history[-10:]) / 10
            
            # If performance is good, reduce exploration
            if recent_performance > 0.8:
                self.epsilon = max(0.05, self.epsilon * 0.99)
            # If performance is poor, increase exploration
            elif recent_performance < 0.5:
                self.epsilon = min(0.3, self.epsilon * 1.01)
    
    def get_policy_stats(self) -> Dict[str, Any]:
        """Get policy statistics and performance metrics"""
        stats = {
            'total_actions': self.total_actions,
            'successful_actions': self.successful_actions,
            'success_rate': self.successful_actions / max(1, self.total_actions),
            'epsilon': self.epsilon,
            'experience_buffer_size': len(self.experience_buffer),
            'contexts_learned': len(self.q_values),
            'average_reward': sum(self.reward_history) / max(1, len(self.reward_history)) if self.reward_history else 0.0,
            'recent_performance': sum(self.reward_history[-10:]) / min(10, len(self.reward_history)) if self.reward_history else 0.0
        }
        
        # Action distribution
        action_dist = defaultdict(int)
        for action in self.action_history:
            action_dist[action] += 1
        
        stats['action_distribution'] = dict(action_dist)
        
        # Q-value summary
        q_value_summary = {}
        for context, actions in self.q_values.items():
            q_value_summary[context] = {
                'best_action': max(actions.items(), key=lambda x: x[1])[0] if actions else None,
                'best_q_value': max(actions.values()) if actions else 0.0,
                'action_count': len(actions)
            }
        
        stats['q_value_summary'] = q_value_summary
        
        return stats
    
    def _save_policy(self):
        """Save policy state to disk"""
        try:
            policy_dir = "composer/models"
            os.makedirs(policy_dir, exist_ok=True)
            
            policy_data = {
                'q_values': dict(self.q_values),
                'action_counts': dict(self.action_counts),
                'epsilon': self.epsilon,
                'total_actions': self.total_actions,
                'successful_actions': self.successful_actions,
                'reward_history': list(self.reward_history),
                'action_history': list(self.action_history),
                'timestamp': time.time()
            }
            
            policy_path = os.path.join(policy_dir, 'rl_policy.json')
            with open(policy_path, 'w') as f:
                json.dump(policy_data, f, indent=2)
            
            logger.info(f"RL Policy saved to {policy_path}")
            
        except Exception as e:
            logger.error(f"Failed to save RL policy: {str(e)}")
    
    def _load_policy(self):
        """Load policy state from disk"""
        try:
            policy_path = "composer/models/rl_policy.json"
            
            if os.path.exists(policy_path):
                with open(policy_path, 'r') as f:
                    policy_data = json.load(f)
                
                # Restore state
                self.q_values = defaultdict(lambda: defaultdict(float))
                for context, actions in policy_data.get('q_values', {}).items():
                    for action, q_value in actions.items():
                        self.q_values[context][action] = q_value
                
                self.action_counts = defaultdict(lambda: defaultdict(int))
                for context, actions in policy_data.get('action_counts', {}).items():
                    for action, count in actions.items():
                        self.action_counts[context][action] = count
                
                self.epsilon = policy_data.get('epsilon', self.epsilon)
                self.total_actions = policy_data.get('total_actions', 0)
                self.successful_actions = policy_data.get('successful_actions', 0)
                self.reward_history = deque(policy_data.get('reward_history', []), maxlen=1000)
                self.action_history = deque(policy_data.get('action_history', []), maxlen=1000)
                
                logger.info(f"RL Policy loaded from {policy_path}")
            else:
                logger.info("No existing RL policy found, starting fresh")
                
        except Exception as e:
            logger.error(f"Failed to load RL policy: {str(e)}")

# Global policy instance
_rl_policy = None

def get_rl_policy() -> RLPolicy:
    """Get singleton RL policy instance"""
    global _rl_policy
    if _rl_policy is None:
        _rl_policy = RLPolicy()
    return _rl_policy

def calculate_reward(composition_result: Dict[str, Any], feedback: Optional[Dict[str, Any]] = None) -> float:
    """
    Calculate reward for RL policy based on composition result and feedback
    
    Args:
        composition_result: Result from compose function
        feedback: Optional user feedback
        
    Returns:
        Reward value between 0.0 and 1.0
    """
    try:
        reward = 0.0
        
        # Base reward from grounding
        if composition_result.get('grounded', False):
            reward += 0.4
        
        # Reward from grounding score
        grounding_score = composition_result.get('grounding_score', 0.0)
        reward += grounding_score * 0.3
        
        # Reward from composition speed (faster is better)
        composition_time = composition_result.get('composition_time_ms', 1000)
        if composition_time < 50:
            reward += 0.2
        elif composition_time < 100:
            reward += 0.1
        
        # Reward from user feedback if available
        if feedback:
            user_rating = feedback.get('rating', 0)  # Assume 1-5 scale
            if user_rating >= 4:
                reward += 0.3
            elif user_rating >= 3:
                reward += 0.1
            else:
                reward -= 0.1
        
        # Clamp reward to [0, 1]
        reward = max(0.0, min(1.0, reward))
        
        return reward
        
    except Exception as e:
        logger.error(f"Reward calculation failed: {str(e)}")
        return 0.5  # Neutral reward on error