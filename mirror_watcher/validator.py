"""
Data Validator for Mirror Watcher CLI.

Validates input data format and structure for analysis.
"""

import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import re


class DataValidator:
    """Validates input data for Mirror Watcher analysis."""
    
    def __init__(self):
        self.schema = self._load_schema()
        self.validation_rules = self._load_validation_rules()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load expected data schema."""
        return {
            "agents": {
                "type": "object",
                "properties": {
                    "Oracle": {"type": "object"},
                    "Gemini": {"type": "object"},
                    "Capri": {"type": "object"},
                    "Aria": {"type": "object"}
                }
            },
            "system": {
                "type": "object",
                "properties": {
                    "timestamp": {"type": "string"},
                    "status": {"type": "string"},
                    "version": {"type": "string"}
                }
            },
            "messages": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "timestamp": {"type": "string"},
                        "from_agent": {"type": "string"},
                        "to_agents": {"type": "array"},
                        "channel": {"type": "string"},
                        "message": {"type": "string"}
                    },
                    "required": ["timestamp", "from_agent", "message"]
                }
            },
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": ["string", "number"]},
                        "status": {"type": "string"},
                        "agent": {"type": "string"},
                        "description": {"type": "string"},
                        "timestamp": {"type": "string"}
                    },
                    "required": ["id", "status"]
                }
            }
        }
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules."""
        return {
            "timestamp_format": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
            "valid_agents": ["Oracle", "Gemini", "Capri", "Aria"],
            "valid_task_statuses": ["pending", "active", "completed", "failed"],
            "valid_system_statuses": ["operational", "degraded", "offline"],
            "max_message_length": 10000,
            "max_array_size": 10000
        }
    
    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data comprehensively."""
        errors = []
        warnings = []
        
        try:
            # Basic structure validation
            if not isinstance(data, dict):
                errors.append("Input must be a JSON object")
                return {"valid": False, "errors": errors, "warnings": warnings}
            
            # Validate each section
            for section_name, section_schema in self.schema.items():
                if section_name in data:
                    section_errors = self._validate_section(
                        data[section_name], section_schema, section_name
                    )
                    errors.extend(section_errors)
                else:
                    warnings.append(f"Optional section '{section_name}' not found")
            
            # Cross-validation
            cross_errors = self._cross_validate(data)
            errors.extend(cross_errors)
            
            # Data quality checks
            quality_warnings = self._check_data_quality(data)
            warnings.extend(quality_warnings)
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "validation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation exception: {str(e)}"],
                "warnings": warnings
            }
    
    def _validate_section(self, data: Any, schema: Dict[str, Any], section_name: str) -> List[str]:
        """Validate a specific section against its schema."""
        errors = []
        
        expected_type = schema.get("type", "object")
        
        # Type validation
        if expected_type == "object" and not isinstance(data, dict):
            errors.append(f"Section '{section_name}' must be an object")
            return errors
        
        if expected_type == "array" and not isinstance(data, list):
            errors.append(f"Section '{section_name}' must be an array")
            return errors
        
        # Array size validation
        if expected_type == "array" and len(data) > self.validation_rules["max_array_size"]:
            errors.append(f"Section '{section_name}' exceeds maximum array size")
        
        # Properties validation for objects
        if expected_type == "object" and "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                if prop_name in data:
                    prop_errors = self._validate_property(
                        data[prop_name], prop_schema, f"{section_name}.{prop_name}"
                    )
                    errors.extend(prop_errors)
        
        # Items validation for arrays
        if expected_type == "array" and "items" in schema:
            for i, item in enumerate(data):
                item_errors = self._validate_section(
                    item, schema["items"], f"{section_name}[{i}]"
                )
                errors.extend(item_errors)
        
        return errors
    
    def _validate_property(self, value: Any, schema: Dict[str, Any], prop_path: str) -> List[str]:
        """Validate a specific property."""
        errors = []
        
        expected_type = schema.get("type")
        
        if isinstance(expected_type, list):
            # Multiple types allowed
            if not any(self._check_type(value, t) for t in expected_type):
                errors.append(f"Property '{prop_path}' must be one of types: {expected_type}")
        else:
            # Single type
            if not self._check_type(value, expected_type):
                errors.append(f"Property '{prop_path}' must be of type: {expected_type}")
        
        # Specific validations
        if prop_path.endswith("timestamp"):
            if not self._validate_timestamp(value):
                errors.append(f"Invalid timestamp format in '{prop_path}': {value}")
        
        if prop_path.endswith("agent") or prop_path.endswith("from_agent"):
            if value not in self.validation_rules["valid_agents"]:
                errors.append(f"Invalid agent name in '{prop_path}': {value}")
        
        if prop_path.endswith("status") and "task" in prop_path.lower():
            if value not in self.validation_rules["valid_task_statuses"]:
                errors.append(f"Invalid task status in '{prop_path}': {value}")
        
        if prop_path.endswith("status") and "system" in prop_path.lower():
            if value not in self.validation_rules["valid_system_statuses"]:
                errors.append(f"Invalid system status in '{prop_path}': {value}")
        
        if prop_path.endswith("message") and isinstance(value, str):
            if len(value) > self.validation_rules["max_message_length"]:
                errors.append(f"Message too long in '{prop_path}': {len(value)} characters")
        
        return errors
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "number":
            return isinstance(value, (int, float))
        elif expected_type == "integer":
            return isinstance(value, int)
        elif expected_type == "array":
            return isinstance(value, list)
        elif expected_type == "object":
            return isinstance(value, dict)
        elif expected_type == "boolean":
            return isinstance(value, bool)
        else:
            return True  # Unknown type, allow
    
    def _validate_timestamp(self, timestamp: str) -> bool:
        """Validate timestamp format."""
        if not isinstance(timestamp, str):
            return False
        
        # Check ISO format pattern
        pattern = self.validation_rules["timestamp_format"]
        if not re.match(pattern, timestamp):
            return False
        
        # Try to parse as datetime
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    def _cross_validate(self, data: Dict[str, Any]) -> List[str]:
        """Perform cross-section validation."""
        errors = []
        
        # Check agent consistency
        if "agents" in data and "messages" in data:
            agent_names = set(data["agents"].keys())
            message_agents = set()
            
            for msg in data["messages"]:
                if isinstance(msg, dict):
                    if "from_agent" in msg:
                        message_agents.add(msg["from_agent"])
                    if "to_agents" in msg and isinstance(msg["to_agents"], list):
                        message_agents.update(msg["to_agents"])
            
            unknown_agents = message_agents - agent_names
            if unknown_agents:
                errors.append(f"Messages reference unknown agents: {list(unknown_agents)}")
        
        # Check task-agent consistency
        if "agents" in data and "tasks" in data:
            agent_names = set(data["agents"].keys())
            task_agents = set()
            
            for task in data["tasks"]:
                if isinstance(task, dict) and "agent" in task:
                    task_agents.add(task["agent"])
            
            unknown_task_agents = task_agents - agent_names
            if unknown_task_agents:
                errors.append(f"Tasks reference unknown agents: {list(unknown_task_agents)}")
        
        return errors
    
    def _check_data_quality(self, data: Dict[str, Any]) -> List[str]:
        """Check data quality and completeness."""
        warnings = []
        
        # Check for empty sections
        for section_name in ["agents", "messages", "tasks"]:
            if section_name in data:
                if isinstance(data[section_name], (list, dict)) and len(data[section_name]) == 0:
                    warnings.append(f"Section '{section_name}' is empty")
        
        # Check message frequency
        if "messages" in data and isinstance(data["messages"], list):
            if len(data["messages"]) > 1000:
                warnings.append("High message volume detected")
            elif len(data["messages"]) < 10:
                warnings.append("Low message volume detected")
        
        # Check task completion rates
        if "tasks" in data and isinstance(data["tasks"], list):
            completed_tasks = sum(1 for task in data["tasks"] 
                                if isinstance(task, dict) and task.get("status") == "completed")
            total_tasks = len(data["tasks"])
            
            if total_tasks > 0:
                completion_rate = completed_tasks / total_tasks
                if completion_rate < 0.5:
                    warnings.append(f"Low task completion rate: {completion_rate:.2%}")
        
        return warnings
    
    def validate_json_format(self, json_string: str) -> Dict[str, Any]:
        """Validate JSON format specifically."""
        try:
            data = json.loads(json_string)
            return {
                "valid": True,
                "parsed_data": data,
                "size": len(json_string)
            }
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": str(e),
                "line": e.lineno,
                "column": e.colno
            }
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about the expected data schema."""
        return {
            "schema": self.schema,
            "validation_rules": self.validation_rules,
            "supported_sections": list(self.schema.keys()),
            "supported_agents": self.validation_rules["valid_agents"]
        }