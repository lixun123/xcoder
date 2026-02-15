#!/usr/bin/env python3
"""
IntentAgent - Lightweight agent for problem classification

This agent quickly analyzes problems and classifies them as 'simple' or 'complex'
to route to appropriate handling paths.
"""

import json
import re
from typing import Dict, Any

from core.agents.base_sub_agent import BaseSubAgent, AgentType


class IntentAgent(BaseSubAgent):
    """Lightweight agent for classifying problem complexity and intent."""

    def get_agent_type(self) -> AgentType:
        return AgentType.INTENT

    def get_system_prompt(self) -> str:
        return """
You are a lightweight intelligent agent specialized in problem classification. Your primary responsibility is to quickly analyze code problems and classify them as "simple" or "complex" to select the most appropriate fix path.

**Classification Criteria:**

**Simple Problems (simple):**
- Syntax errors (SyntaxError, IndentationError, missing colons, brackets, etc.)
- Import errors (ImportError, ModuleNotFoundError)
- Variable name spelling errors (NameError)
- Simple type errors (TypeError with single parameter issues)
- Simple logic fixes within a single file
- Obvious spelling or formatting errors

**Complex Problems (complex):**
- Multi-file coordinated modifications
- Architecture-level refactoring
- Business logic design issues
- Performance optimization
- Concurrency and async issues
- Database design or query optimization
- API design or integration
- Algorithm design or optimization
- New feature development

**Analysis Dimensions:**
1. **Keyword Analysis**: Identify keywords in the problem description
2. **Impact Scope**: Single file vs multiple files
3. **Error Type**: Syntax/compilation vs logic/design
4. **Fix Complexity**: Direct modification vs requires planning

**Output Format (strict JSON):**
```json
{
  "intent": "simple|complex",
  "confidence": 0.85,
  "reasoning": "Detected syntax error, scope limited to single file",
  "estimated_effort": "low|medium|high",
  "primary_issue_type": "syntax|import|logic|architecture|performance|other"
}
```

Please classify based on problem description and quick code scan, prioritizing simple fix paths for efficiency.
"""

    def _post_execute(self, task, response: str) -> str:
        """Parse and validate the intent classification result."""
        try:
            # Extract JSON from response
            classification = self._parse_classification(response)

            if classification:
                # Validate required fields
                required_fields = ["intent", "confidence", "reasoning"]
                if all(field in classification for field in required_fields):
                    # Ensure intent is valid
                    if classification["intent"] in ["simple", "complex"]:
                        return json.dumps(classification, ensure_ascii=False, indent=2)

            # Fallback to default classification
            print("⚠️ Intent classification result invalid, using default complex classification")
            return json.dumps({
                "intent": "complex",
                "confidence": 0.5,
                "reasoning": "Classification parsing failed, conservatively choosing complex path",
                "estimated_effort": "medium",
                "primary_issue_type": "other"
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"⚠️ Intent classification processing error: {e}")
            # Fallback to complex path for safety
            return json.dumps({
                "intent": "complex",
                "confidence": 0.3,
                "reasoning": f"Classification processing exception: {str(e)}",
                "estimated_effort": "high",
                "primary_issue_type": "other"
            }, ensure_ascii=False, indent=2)

    def _parse_classification(self, response: str) -> Dict[str, Any]:
        """Parse JSON classification from response."""
        # Try different JSON extraction patterns
        json_patterns = [
            r'\{[^{}]*"intent"[^{}]*\}',  # Simple intent JSON
            r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks
            r'```\s*(\{.*?\})\s*```',      # Generic code blocks
            r'\{.*?\}',                    # Any JSON-like structure
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    # Handle captured groups
                    json_str = match if not isinstance(match, tuple) else match[0]
                    classification = json.loads(json_str)

                    # Validate it has intent field
                    if "intent" in classification:
                        return classification

                except (json.JSONDecodeError, TypeError):
                    continue

        # Try parsing entire response as JSON
        try:
            classification = json.loads(response.strip())
            if "intent" in classification:
                return classification
        except json.JSONDecodeError:
            pass

        return None

    def classify_problem(self, problem_description: str) -> Dict[str, Any]:
        """Main method to classify a problem's complexity.

        Args:
            problem_description: Description of the problem to classify

        Returns:
            Classification result with intent, confidence, and reasoning
        """
        from core.utils.common import TaskItem, TaskStatus

        task = TaskItem(
            id="intent_classification",
            title="Problem Complexity Classification",
            description=f"""
Please analyze the following problem and classify it:

Problem Description: {problem_description}

Please quickly analyze the problem type, impact scope, and fix complexity, and return classification result in standard JSON format.
""",
            agent_type=AgentType.INTENT,
            status=TaskStatus.PENDING,
            dependencies=[]
        )

        result = self.execute(task)

        if result["success"]:
            try:
                classification = json.loads(result["result"])
                return classification
            except json.JSONDecodeError:
                # Fallback
                return {
                    "intent": "complex",
                    "confidence": 0.3,
                    "reasoning": "JSON parsing failed, defaulting to complex handling",
                    "estimated_effort": "medium",
                    "primary_issue_type": "other"
                }
        else:
            return {
                "intent": "complex",
                "confidence": 0.2,
                "reasoning": f"Classification execution failed: {result.get('error', 'unknown')}",
                "estimated_effort": "high",
                "primary_issue_type": "other"
            }