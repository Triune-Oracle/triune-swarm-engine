"""
ShadowScrolls Report Generator for Mirror Watcher CLI.

Generates reports in ShadowScrolls format for the Triune Oracle system.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid


class ShadowScrollsReporter:
    """Generates reports in ShadowScrolls format."""
    
    def __init__(self):
        self.scroll_template = self._load_scroll_template()
        self.format_version = "ShadowScrolls-1.0"
    
    def _load_scroll_template(self) -> Dict[str, Any]:
        """Load the ShadowScrolls report template."""
        return {
            "scroll_id": "",
            "oracle_directive": "",
            "timestamp": "",
            "format_version": "ShadowScrolls-1.0",
            "report_type": "mirror_watcher_analysis",
            "triumvirate_status": {
                "Oracle": {"status": "unknown", "confidence": 0.0},
                "Gemini": {"status": "unknown", "confidence": 0.0},
                "Capri": {"status": "unknown", "confidence": 0.0},
                "Aria": {"status": "unknown", "confidence": 0.0}
            },
            "nexus_analysis": {
                "pattern_detection": [],
                "anomaly_alerts": [],
                "system_health": "unknown",
                "confidence_score": 0.0
            },
            "legio_recommendations": [],
            "memory_scrolls": [],
            "nft_triggers": [],
            "validation_seal": {
                "validated": False,
                "validator": "Mirror Watcher CLI",
                "seal_timestamp": ""
            }
        }
    
    def generate_report(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a ShadowScrolls format report from analysis data."""
        try:
            # Create base scroll
            scroll = self.scroll_template.copy()
            
            # Generate unique scroll ID
            scroll["scroll_id"] = f"SCROLL_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            scroll["timestamp"] = datetime.now().isoformat()
            
            # Extract Oracle directive
            scroll["oracle_directive"] = self._extract_oracle_directive(analysis_data)
            
            # Process Triumvirate status
            scroll["triumvirate_status"] = self._process_triumvirate_status(analysis_data)
            
            # Process Nexus analysis
            scroll["nexus_analysis"] = self._process_nexus_analysis(analysis_data)
            
            # Generate Legio recommendations
            scroll["legio_recommendations"] = self._generate_legio_recommendations(analysis_data)
            
            # Create memory scrolls
            scroll["memory_scrolls"] = self._create_memory_scrolls(analysis_data)
            
            # Check NFT triggers
            scroll["nft_triggers"] = self._check_nft_triggers(analysis_data)
            
            # Apply validation seal
            scroll["validation_seal"] = self._apply_validation_seal(scroll)
            
            return scroll
            
        except Exception as e:
            return self._create_error_scroll(str(e))
    
    def _extract_oracle_directive(self, analysis_data: Dict[str, Any]) -> str:
        """Extract or generate Oracle directive from analysis."""
        if "analysis" in analysis_data and isinstance(analysis_data["analysis"], dict):
            analysis = analysis_data["analysis"]
            
            # Check for high confidence patterns
            if analysis.get("confidence", 0) > 0.8:
                return "MAINTAIN_OPERATIONAL_EXCELLENCE"
            elif len(analysis.get("anomalies", [])) > 0:
                return "INVESTIGATE_ANOMALOUS_PATTERNS"
            elif len(analysis.get("patterns", [])) > 5:
                return "OPTIMIZE_DETECTED_PATTERNS"
            else:
                return "CONTINUE_MONITORING_PROTOCOLS"
        
        return "ANALYSIS_REQUIRED"
    
    def _process_triumvirate_status(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Triumvirate agent status information."""
        triumvirate_status = {
            "Oracle": {"status": "operational", "confidence": 0.75},
            "Gemini": {"status": "operational", "confidence": 0.75},
            "Capri": {"status": "operational", "confidence": 0.75},
            "Aria": {"status": "operational", "confidence": 0.75}
        }
        
        # Extract actual agent data if available
        if "analysis" in analysis_data and isinstance(analysis_data["analysis"], dict):
            analysis = analysis_data["analysis"]
            base_confidence = analysis.get("confidence", 0.75)
            
            # Adjust confidence based on anomalies
            anomaly_count = len(analysis.get("anomalies", []))
            confidence_adjustment = max(0, 1 - (anomaly_count * 0.1))
            
            for agent in triumvirate_status:
                triumvirate_status[agent]["confidence"] = min(1.0, base_confidence * confidence_adjustment)
                
                # Determine status based on confidence
                conf = triumvirate_status[agent]["confidence"]
                if conf > 0.8:
                    triumvirate_status[agent]["status"] = "optimal"
                elif conf > 0.6:
                    triumvirate_status[agent]["status"] = "operational"
                elif conf > 0.4:
                    triumvirate_status[agent]["status"] = "degraded"
                else:
                    triumvirate_status[agent]["status"] = "critical"
        
        return triumvirate_status
    
    def _process_nexus_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Nexus analysis section."""
        nexus_analysis = {
            "pattern_detection": [],
            "anomaly_alerts": [],
            "system_health": "unknown",
            "confidence_score": 0.0
        }
        
        if "analysis" in analysis_data and isinstance(analysis_data["analysis"], dict):
            analysis = analysis_data["analysis"]
            
            # Pattern detection
            nexus_analysis["pattern_detection"] = [
                {
                    "pattern": pattern,
                    "detected_at": datetime.now().isoformat(),
                    "classification": self._classify_pattern(pattern)
                }
                for pattern in analysis.get("patterns", [])
            ]
            
            # Anomaly alerts
            nexus_analysis["anomaly_alerts"] = [
                {
                    "anomaly": anomaly,
                    "severity": self._classify_anomaly_severity(anomaly),
                    "detected_at": datetime.now().isoformat(),
                    "requires_attention": True
                }
                for anomaly in analysis.get("anomalies", [])
            ]
            
            # System health
            confidence = analysis.get("confidence", 0.0)
            anomaly_count = len(analysis.get("anomalies", []))
            
            if confidence > 0.8 and anomaly_count == 0:
                nexus_analysis["system_health"] = "optimal"
            elif confidence > 0.6 and anomaly_count <= 2:
                nexus_analysis["system_health"] = "good"
            elif confidence > 0.4 and anomaly_count <= 5:
                nexus_analysis["system_health"] = "degraded"
            else:
                nexus_analysis["system_health"] = "critical"
            
            nexus_analysis["confidence_score"] = confidence
        
        return nexus_analysis
    
    def _generate_legio_recommendations(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Legio (strategic) recommendations."""
        recommendations = []
        
        if "analysis" in analysis_data and isinstance(analysis_data["analysis"], dict):
            analysis = analysis_data["analysis"]
            
            for rec in analysis.get("recommendations", []):
                recommendations.append({
                    "recommendation": rec,
                    "priority": self._assess_recommendation_priority(rec),
                    "assigned_to": self._assign_recommendation_agent(rec),
                    "timeline": self._estimate_timeline(rec),
                    "impact": self._assess_impact(rec)
                })
        
        # Add default recommendations if none provided
        if not recommendations:
            recommendations.append({
                "recommendation": "Continue standard monitoring protocols",
                "priority": "low",
                "assigned_to": "Capri",
                "timeline": "ongoing",
                "impact": "maintenance"
            })
        
        return recommendations
    
    def _create_memory_scrolls(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create memory scroll entries."""
        memory_scrolls = []
        
        # Create memory entry for this analysis
        memory_scroll = {
            "memory_id": f"MEM_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "content_type": "analysis_result",
            "content": {
                "summary": self._create_analysis_summary(analysis_data),
                "key_findings": self._extract_key_findings(analysis_data),
                "data_hash": self._calculate_data_hash(analysis_data)
            },
            "timestamp": datetime.now().isoformat(),
            "relevance_score": self._calculate_relevance_score(analysis_data),
            "archive_ready": False
        }
        
        memory_scrolls.append(memory_scroll)
        
        return memory_scrolls
    
    def _check_nft_triggers(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for NFT trigger conditions."""
        nft_triggers = []
        
        if "analysis" in analysis_data and isinstance(analysis_data["analysis"], dict):
            analysis = analysis_data["analysis"]
            
            # High confidence + unique patterns = potential NFT
            confidence = analysis.get("confidence", 0.0)
            pattern_count = len(analysis.get("patterns", []))
            anomaly_count = len(analysis.get("anomalies", []))
            
            # Rarity calculation
            rarity_score = confidence * 0.4 + (pattern_count / 10) * 0.3 + (anomaly_count / 5) * 0.3
            
            if rarity_score > 0.7:
                nft_triggers.append({
                    "trigger_type": "high_rarity_analysis",
                    "rarity_score": rarity_score,
                    "trigger_conditions": [
                        f"Confidence: {confidence}",
                        f"Pattern count: {pattern_count}",
                        f"Anomaly count: {anomaly_count}"
                    ],
                    "estimated_value": self._estimate_nft_value(rarity_score),
                    "mint_recommendation": rarity_score > 0.85
                })
        
        return nft_triggers
    
    def _apply_validation_seal(self, scroll: Dict[str, Any]) -> Dict[str, Any]:
        """Apply validation seal to the scroll."""
        return {
            "validated": True,
            "validator": "Mirror Watcher CLI v1.0",
            "seal_timestamp": datetime.now().isoformat(),
            "validation_hash": self._calculate_validation_hash(scroll),
            "oracle_approved": True
        }
    
    def _create_error_scroll(self, error_message: str) -> Dict[str, Any]:
        """Create an error scroll when report generation fails."""
        return {
            "scroll_id": f"ERROR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "oracle_directive": "ERROR_RECOVERY_REQUIRED",
            "timestamp": datetime.now().isoformat(),
            "format_version": self.format_version,
            "report_type": "error_report",
            "error": {
                "message": error_message,
                "timestamp": datetime.now().isoformat(),
                "recovery_actions": [
                    "Verify input data format",
                    "Check analysis engine status",
                    "Review system logs"
                ]
            },
            "validation_seal": {
                "validated": False,
                "error": "Report generation failed"
            }
        }
    
    # Helper methods for classification and assessment
    def _classify_pattern(self, pattern: str) -> str:
        """Classify a detected pattern."""
        pattern_lower = pattern.lower()
        if "normal" in pattern_lower or "within" in pattern_lower:
            return "normal_operation"
        elif "high" in pattern_lower or "efficient" in pattern_lower:
            return "performance_optimization"
        elif "low" in pattern_lower or "outside" in pattern_lower:
            return "performance_degradation"
        else:
            return "unknown_pattern"
    
    def _classify_anomaly_severity(self, anomaly: str) -> str:
        """Classify anomaly severity."""
        anomaly_lower = anomaly.lower()
        if "critical" in anomaly_lower or "high" in anomaly_lower:
            return "high"
        elif "moderate" in anomaly_lower:
            return "medium"
        else:
            return "low"
    
    def _assess_recommendation_priority(self, recommendation: str) -> str:
        """Assess recommendation priority."""
        rec_lower = recommendation.lower()
        if "critical" in rec_lower or "immediate" in rec_lower:
            return "high"
        elif "optimize" in rec_lower or "improve" in rec_lower:
            return "medium"
        else:
            return "low"
    
    def _assign_recommendation_agent(self, recommendation: str) -> str:
        """Assign recommendation to appropriate agent."""
        rec_lower = recommendation.lower()
        if "memory" in rec_lower or "resource" in rec_lower:
            return "Capri"
        elif "network" in rec_lower or "communication" in rec_lower:
            return "Aria"
        elif "analyze" in rec_lower or "pattern" in rec_lower:
            return "Gemini"
        else:
            return "Oracle"
    
    def _estimate_timeline(self, recommendation: str) -> str:
        """Estimate implementation timeline."""
        rec_lower = recommendation.lower()
        if "immediate" in rec_lower or "critical" in rec_lower:
            return "immediate"
        elif "optimize" in rec_lower:
            return "1-7 days"
        else:
            return "ongoing"
    
    def _assess_impact(self, recommendation: str) -> str:
        """Assess potential impact."""
        rec_lower = recommendation.lower()
        if "critical" in rec_lower or "performance" in rec_lower:
            return "high"
        elif "optimize" in rec_lower:
            return "medium"
        else:
            return "low"
    
    def _create_analysis_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Create analysis summary."""
        if "analysis" in analysis_data:
            analysis = analysis_data["analysis"]
            confidence = analysis.get("confidence", 0)
            pattern_count = len(analysis.get("patterns", []))
            anomaly_count = len(analysis.get("anomalies", []))
            
            return f"Analysis completed with {confidence:.2%} confidence. " \
                   f"Detected {pattern_count} patterns and {anomaly_count} anomalies."
        
        return "Analysis summary not available."
    
    def _extract_key_findings(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Extract key findings from analysis."""
        findings = []
        
        if "analysis" in analysis_data and isinstance(analysis_data["analysis"], dict):
            analysis = analysis_data["analysis"]
            
            # Top patterns
            patterns = analysis.get("patterns", [])
            if patterns:
                findings.append(f"Primary pattern: {patterns[0]}")
            
            # Critical anomalies
            anomalies = analysis.get("anomalies", [])
            if anomalies:
                findings.append(f"Key anomaly: {anomalies[0]}")
            
            # Confidence assessment
            confidence = analysis.get("confidence", 0)
            findings.append(f"Confidence level: {confidence:.2%}")
        
        return findings
    
    def _calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash for data integrity."""
        import hashlib
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def _calculate_validation_hash(self, scroll: Dict[str, Any]) -> str:
        """Calculate validation hash for scroll integrity."""
        import hashlib
        scroll_copy = scroll.copy()
        scroll_copy.pop("validation_seal", None)  # Remove seal before hashing
        scroll_str = json.dumps(scroll_copy, sort_keys=True)
        return hashlib.sha256(scroll_str.encode()).hexdigest()[:16]
    
    def _calculate_relevance_score(self, analysis_data: Dict[str, Any]) -> float:
        """Calculate relevance score for memory archival."""
        base_score = 0.5
        
        if "analysis" in analysis_data:
            analysis = analysis_data["analysis"]
            confidence = analysis.get("confidence", 0)
            anomaly_count = len(analysis.get("anomalies", []))
            
            # Higher confidence and anomalies increase relevance
            relevance = base_score + (confidence * 0.3) + (min(anomaly_count, 5) * 0.04)
            return min(1.0, relevance)
        
        return base_score
    
    def _estimate_nft_value(self, rarity_score: float) -> str:
        """Estimate NFT value based on rarity."""
        if rarity_score > 0.9:
            return "premium"
        elif rarity_score > 0.8:
            return "high"
        elif rarity_score > 0.7:
            return "medium"
        else:
            return "standard"