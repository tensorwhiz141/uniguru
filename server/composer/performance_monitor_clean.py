"""
Performance monitoring and trace logging for Uniguru-LM Composer
Tracks composition metrics, RL actions, and system performance
"""

import logging
import time
import json
import os
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CompositionTrace:
    """Data class for composition trace logging"""
    trace_id: str
    timestamp: float
    extractive_answer: str
    lang: str
    chunk_count: int
    template_id: str
    rl_action: str
    rl_reward: float
    grounded: bool
    grounding_score: float
    composition_time_ms: float
    final_text_length: int
    grounding_attempts: int
    method: str
    success: bool
    error: Optional[str] = None

class PerformanceMonitor:
    """
    Monitors composer performance and logs traces for analysis
    Provides metrics for system optimization and RL training
    """
    
    def __init__(self, log_dir: str = "composer/logs"):
        self.log_dir = log_dir
        self.traces = deque(maxlen=10000)  # Keep last 10k traces in memory
        self.metrics = defaultdict(list)
        self.session_start = time.time()
        
        # Performance counters
        self.total_compositions = 0
        self.successful_compositions = 0
        self.failed_compositions = 0
        self.grounding_failures = 0
        
        # Timing metrics
        self.composition_times = deque(maxlen=1000)
        
        # Create log directory
        os.makedirs(log_dir, exist_ok=True)
        
        # Initialize log files
        self.trace_log_path = os.path.join(log_dir, f"traces_{datetime.now().strftime('%Y%m%d')}.jsonl")
        self.metrics_log_path = os.path.join(log_dir, f"metrics_{datetime.now().strftime('%Y%m%d')}.json")
    
    def log_composition(self, composition_result: Dict[str, Any], 
                       extractive_answer: str, top_chunks: List[Dict]) -> None:
        """Log a composition result for monitoring and analysis"""
        try:
            # Create trace record
            trace = CompositionTrace(
                trace_id=composition_result.get('trace_id', 'unknown'),
                timestamp=time.time(),
                extractive_answer=extractive_answer[:100],  # Truncate for logging
                lang=composition_result.get('lang', 'EN'),
                chunk_count=len(top_chunks),
                template_id=composition_result.get('template_id', 'unknown'),
                rl_action=composition_result.get('rl_action', 'unknown'),
                rl_reward=composition_result.get('rl_reward', 0.0),
                grounded=composition_result.get('grounded', False),
                grounding_score=composition_result.get('grounding_score', 0.0),
                composition_time_ms=composition_result.get('composition_time_ms', 0.0),
                final_text_length=len(composition_result.get('final_text', '')),
                grounding_attempts=composition_result.get('grounding_attempts', 1),
                method=composition_result.get('method', 'unknown'),
                success='error' not in composition_result,
                error=composition_result.get('error')
            )
            
            # Add to memory
            self.traces.append(trace)
            
            # Update counters
            self.total_compositions += 1
            if trace.success:
                self.successful_compositions += 1
            else:
                self.failed_compositions += 1
            
            if not trace.grounded:
                self.grounding_failures += 1
            
            # Update timing metrics
            self.composition_times.append(trace.composition_time_ms)
            
            # Log to file
            self._write_trace_to_file(trace)
            
            # Update performance metrics
            self._update_metrics(trace)
            
            logger.info(f"Composition trace logged: {trace.trace_id}, success={trace.success}, grounded={trace.grounded}")
            
        except Exception as e:
            logger.error(f"Failed to log composition trace: {str(e)}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary"""
        try:
            uptime = time.time() - self.session_start
            
            # Calculate success rates
            success_rate = self.successful_compositions / max(1, self.total_compositions)
            grounding_rate = (self.total_compositions - self.grounding_failures) / max(1, self.total_compositions)
            
            # Calculate timing statistics
            avg_composition_time = sum(self.composition_times) / max(1, len(self.composition_times))
            
            # Calculate percentiles
            sorted_times = sorted(self.composition_times) if self.composition_times else [0]
            p50_time = sorted_times[len(sorted_times) // 2]
            p95_time = sorted_times[int(len(sorted_times) * 0.95)]
            p99_time = sorted_times[int(len(sorted_times) * 0.99)]
            
            summary = {
                'session_info': {
                    'uptime_seconds': uptime,
                    'start_time': self.session_start,
                    'total_compositions': self.total_compositions
                },
                'success_metrics': {
                    'success_rate': success_rate,
                    'grounding_rate': grounding_rate,
                    'successful_compositions': self.successful_compositions,
                    'failed_compositions': self.failed_compositions,
                    'grounding_failures': self.grounding_failures
                },
                'performance_metrics': {
                    'avg_composition_time_ms': avg_composition_time,
                    'p50_composition_time_ms': p50_time,
                    'p95_composition_time_ms': p95_time,
                    'p99_composition_time_ms': p99_time,
                    'min_time_ms': min(self.composition_times) if self.composition_times else 0,
                    'max_time_ms': max(self.composition_times) if self.composition_times else 0
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate performance summary: {str(e)}")
            return {'error': str(e)}
    
    def _write_trace_to_file(self, trace: CompositionTrace):
        """Write trace to log file"""
        try:
            trace_dict = asdict(trace)
            trace_dict['datetime'] = datetime.fromtimestamp(trace.timestamp).isoformat()
            
            with open(self.trace_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(trace_dict, ensure_ascii=False) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to write trace to file: {str(e)}")
    
    def _update_metrics(self, trace: CompositionTrace):
        """Update performance metrics"""
        try:
            # Update timing metrics by template
            self.metrics[f'timing_{trace.template_id}'].append(trace.composition_time_ms)
            
            # Update grounding metrics by language
            self.metrics[f'grounding_{trace.lang}'].append(trace.grounding_score)
            
            # Update success metrics by method
            self.metrics[f'success_{trace.method}'].append(1 if trace.success else 0)
            
            # Periodically save metrics
            if self.total_compositions % 10 == 0:
                self._save_metrics()
                
        except Exception as e:
            logger.error(f"Failed to update metrics: {str(e)}")
    
    def _save_metrics(self):
        """Save aggregated metrics to file"""
        try:
            metrics_summary = {
                'timestamp': time.time(),
                'session_start': self.session_start,
                'total_compositions': self.total_compositions,
                'performance_summary': self.get_performance_summary()
            }
            
            with open(self.metrics_log_path, 'w', encoding='utf-8') as f:
                json.dump(metrics_summary, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save metrics: {str(e)}")

# Global monitor instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get singleton performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def log_composition_trace(composition_result: Dict[str, Any], 
                         extractive_answer: str, top_chunks: List[Dict]) -> None:
    """Convenience function to log composition trace"""
    monitor = get_performance_monitor()
    monitor.log_composition(composition_result, extractive_answer, top_chunks)