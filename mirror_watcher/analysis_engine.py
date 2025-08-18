"""
Analysis Engine for Mirror Watcher CLI.

Provides data analysis capabilities for Triune Swarm Engine monitoring.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import hashlib


@dataclass
class AnalysisResult:
    """Container for analysis results."""
    success: bool
    confidence: float
    patterns: List[str]
    anomalies: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]


class AnalysisEngine:
    """Core analysis engine for Mirror Watcher."""
    
    def __init__(self):
        self.patterns = self._load_patterns()
        self.thresholds = self._load_thresholds()
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load known patterns for analysis."""
        return {
            "agent_coordination": {
                "normal_response_time": (0.1, 2.0),  # seconds
                "message_frequency": (1, 100),       # messages per hour
                "success_rate": (0.85, 1.0)          # percentage
            },
            "swarm_behavior": {
                "coordination_efficiency": (0.7, 1.0),
                "task_completion_rate": (0.8, 1.0),
                "resource_utilization": (0.6, 0.9)
            },
            "system_health": {
                "memory_usage": (0.0, 0.8),
                "cpu_usage": (0.0, 0.85),
                "network_latency": (0.0, 0.5)
            }
        }
    
    def _load_thresholds(self) -> Dict[str, float]:
        """Load analysis thresholds."""
        return {
            "anomaly_threshold": 0.3,
            "confidence_threshold": 0.7,
            "pattern_match_threshold": 0.8
        }
    
    def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """Perform comprehensive analysis on input data."""
        try:
            # Extract metrics
            metrics = self._extract_metrics(data)
            
            # Detect patterns
            patterns = self._detect_patterns(metrics)
            
            # Find anomalies
            anomalies = self._detect_anomalies(metrics)
            
            # Calculate confidence
            confidence = self._calculate_confidence(patterns, anomalies)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(patterns, anomalies)
            
            # Create metadata
            metadata = {
                "analysis_timestamp": datetime.now().isoformat(),
                "data_hash": self._calculate_hash(data),
                "metrics_count": len(metrics),
                "pattern_matches": len(patterns),
                "anomaly_count": len(anomalies)
            }
            
            return AnalysisResult(
                success=True,
                confidence=confidence,
                patterns=patterns,
                anomalies=anomalies,
                recommendations=recommendations,
                metadata=metadata
            )
            
        except Exception as e:
            return AnalysisResult(
                success=False,
                confidence=0.0,
                patterns=[],
                anomalies=[f"Analysis error: {str(e)}"],
                recommendations=["Review input data format"],
                metadata={"error": str(e)}
            )
    
    def to_dict(self, result: AnalysisResult) -> Dict[str, Any]:
        """Convert AnalysisResult to dictionary for JSON serialization."""
        return {
            "success": result.success,
            "confidence": result.confidence,
            "patterns": result.patterns,
            "anomalies": result.anomalies,
            "recommendations": result.recommendations,
            "metadata": result.metadata
        }
    
    def _extract_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical metrics from input data."""
        metrics = {}
        
        # Agent metrics
        if "agents" in data:
            agents = data["agents"]
            if isinstance(agents, dict):
                for agent_name, agent_data in agents.items():
                    if isinstance(agent_data, dict):
                        for key, value in agent_data.items():
                            if isinstance(value, (int, float)):
                                metrics[f"agent_{agent_name}_{key}"] = float(value)
        
        # System metrics
        if "system" in data:
            system = data["system"]
            if isinstance(system, dict):
                for key, value in system.items():
                    if isinstance(value, (int, float)):
                        metrics[f"system_{key}"] = float(value)
        
        # Message metrics
        if "messages" in data:
            messages = data["messages"]
            if isinstance(messages, list):
                metrics["message_count"] = float(len(messages))
                
                # Calculate message frequency
                timestamps = []
                for msg in messages:
                    if isinstance(msg, dict) and "timestamp" in msg:
                        timestamps.append(msg["timestamp"])
                
                if len(timestamps) > 1:
                    time_span = len(timestamps)  # Simplified calculation
                    metrics["message_frequency"] = len(timestamps) / max(time_span, 1)
        
        # Task metrics
        if "tasks" in data:
            tasks = data["tasks"]
            if isinstance(tasks, list):
                metrics["task_count"] = float(len(tasks))
                
                completed = sum(1 for task in tasks 
                              if isinstance(task, dict) and task.get("status") == "completed")
                metrics["task_completion_rate"] = completed / max(len(tasks), 1)
        
        return metrics
    
    def _detect_patterns(self, metrics: Dict[str, float]) -> List[str]:
        """Detect known patterns in metrics."""
        patterns = []
        
        for pattern_category, pattern_rules in self.patterns.items():
            for pattern_name, (min_val, max_val) in pattern_rules.items():
                # Check if any metric matches this pattern
                for metric_name, metric_value in metrics.items():
                    if pattern_name.replace("_", " ") in metric_name.replace("_", " "):
                        if min_val <= metric_value <= max_val:
                            patterns.append(f"{pattern_category}: {pattern_name} within normal range")
                        else:
                            patterns.append(f"{pattern_category}: {pattern_name} outside normal range")
        
        # Generic pattern detection
        if "message_frequency" in metrics:
            freq = metrics["message_frequency"]
            if freq > 50:
                patterns.append("High message activity detected")
            elif freq < 1:
                patterns.append("Low message activity detected")
        
        if "task_completion_rate" in metrics:
            rate = metrics["task_completion_rate"]
            if rate > 0.9:
                patterns.append("High task completion efficiency")
            elif rate < 0.5:
                patterns.append("Low task completion efficiency")
        
        return patterns
    
    def _detect_anomalies(self, metrics: Dict[str, float]) -> List[str]:
        """Detect anomalies in metrics."""
        anomalies = []
        
        # Statistical anomaly detection (simplified)
        if len(metrics) > 1:
            values = list(metrics.values())
            mean_val = sum(values) / len(values)
            
            for metric_name, value in metrics.items():
                deviation = abs(value - mean_val) / max(mean_val, 1)
                if deviation > self.thresholds["anomaly_threshold"]:
                    anomalies.append(f"Statistical anomaly in {metric_name}: {value}")
        
        # Domain-specific anomaly detection
        for metric_name, value in metrics.items():
            if "response_time" in metric_name and value > 10.0:
                anomalies.append(f"High response time detected: {value}s")
            
            if "memory_usage" in metric_name and value > 0.95:
                anomalies.append(f"Critical memory usage: {value}")
            
            if "error_rate" in metric_name and value > 0.1:
                anomalies.append(f"High error rate: {value}")
        
        return anomalies
    
    def _calculate_confidence(self, patterns: List[str], anomalies: List[str]) -> float:
        """Calculate confidence score for analysis."""
        # Base confidence
        confidence = 0.5
        
        # Increase confidence for pattern matches
        confidence += len(patterns) * 0.1
        
        # Decrease confidence for anomalies
        confidence -= len(anomalies) * 0.15
        
        # Ensure confidence is within bounds
        return max(0.0, min(1.0, confidence))
    
    def _generate_recommendations(self, patterns: List[str], anomalies: List[str]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Recommendations based on anomalies
        for anomaly in anomalies:
            if "high response time" in anomaly.lower():
                recommendations.append("Consider optimizing system performance or scaling resources")
            elif "memory usage" in anomaly.lower():
                recommendations.append("Monitor memory usage and consider memory optimization")
            elif "error rate" in anomaly.lower():
                recommendations.append("Investigate error causes and implement error handling improvements")
        
        # Recommendations based on patterns
        for pattern in patterns:
            if "low message activity" in pattern.lower():
                recommendations.append("Check agent connectivity and message routing")
            elif "low task completion" in pattern.lower():
                recommendations.append("Review task assignment and resource allocation")
        
        # Default recommendation
        if not recommendations:
            recommendations.append("System appears to be operating within normal parameters")
        
        return recommendations
    
    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash of input data for tracking."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get_analysis_summary(self, result: AnalysisResult) -> Dict[str, Any]:
        """Get a summary of analysis results."""
        return {
            "success": result.success,
            "confidence": result.confidence,
            "pattern_count": len(result.patterns),
            "anomaly_count": len(result.anomalies),
            "recommendation_count": len(result.recommendations),
            "timestamp": result.metadata.get("analysis_timestamp", ""),
            "status": "healthy" if result.confidence > 0.7 and len(result.anomalies) == 0 else "requires_attention"
        }