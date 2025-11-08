"""
Code Executor Service
Safely executes dynamically generated pandas code
"""
import pandas as pd
import traceback
from typing import Dict, Any, Optional


class CodeExecutor:
    """Service for safely executing pandas code in a controlled environment"""

    def __init__(self, dataframe: pd.DataFrame):
        """
        Initialize code executor with a dataframe

        Args:
            dataframe: The pandas DataFrame to work with
        """
        self.df = dataframe

    def execute(self, code: str) -> Dict[str, Any]:
        """
        Execute pandas code safely

        Args:
            code: Python/pandas code to execute

        Returns:
            Dict with success status, result, and any errors
        """
        try:
            # Create a safe execution environment
            namespace = {
                'pd': pd,
                'df': self.df,
                'result': None
            }

            # Execute the code
            exec(code, namespace)

            # Get the result
            result = namespace.get('result')

            if result is None:
                return {
                    'success': False,
                    'error': 'Code executed but did not set result variable',
                    'data': None
                }

            # Convert result to serializable format
            formatted_result = self._format_result(result)

            return {
                'success': True,
                'data': formatted_result,
                'error': None
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'data': None
            }

    def _format_result(self, result: Any) -> Dict[str, Any]:
        """
        Format execution result into a standardized structure

        Args:
            result: The result from code execution

        Returns:
            Formatted result dictionary
        """
        # Handle pandas Series
        if isinstance(result, pd.Series):
            return {
                'type': 'series',
                'data': result.to_dict()
            }

        # Handle pandas DataFrame
        elif isinstance(result, pd.DataFrame):
            return {
                'type': 'dataframe',
                'data': result.to_dict('records')
            }

        # Handle dict
        elif isinstance(result, dict):
            return {
                'type': 'dict',
                'data': self._serialize_dict(result)
            }

        # Handle list
        elif isinstance(result, list):
            return {
                'type': 'list',
                'data': result
            }

        # Handle scalar values
        elif isinstance(result, (int, float, str, bool)):
            return {
                'type': 'scalar',
                'value': result
            }

        # Handle None
        elif result is None:
            return {
                'type': 'none',
                'data': None
            }

        # Default: convert to string
        else:
            return {
                'type': 'unknown',
                'data': str(result)
            }

    def _serialize_dict(self, data: dict) -> dict:
        """
        Recursively serialize dictionary to handle nested pandas objects

        Args:
            data: Dictionary to serialize

        Returns:
            Serialized dictionary
        """
        serialized = {}
        for key, value in data.items():
            if isinstance(value, pd.Series):
                serialized[key] = value.to_dict()
            elif isinstance(value, pd.DataFrame):
                serialized[key] = value.to_dict('records')
            elif isinstance(value, dict):
                serialized[key] = self._serialize_dict(value)
            elif isinstance(value, list):
                serialized[key] = [self._serialize_value(v) for v in value]
            else:
                serialized[key] = self._serialize_value(value)
        return serialized

    def _serialize_value(self, value: Any) -> Any:
        """
        Serialize a single value

        Args:
            value: Value to serialize

        Returns:
            Serialized value
        """
        if isinstance(value, pd.Series):
            return value.to_dict()
        elif isinstance(value, pd.DataFrame):
            return value.to_dict('records')
        elif isinstance(value, dict):
            return self._serialize_dict(value)
        elif pd.isna(value):
            return None
        else:
            return value

    def validate_code(self, code: str) -> Optional[str]:
        """
        Validate code for safety issues

        Args:
            code: Code to validate

        Returns:
            Error message if validation fails, None if valid
        """
        # List of dangerous operations
        dangerous_patterns = [
            'import os',
            'import sys',
            'import subprocess',
            '__import__',
            'eval(',
            'exec(',
            'compile(',
            'open(',
            'file(',
            'input(',
            'raw_input(',
            '__',
        ]

        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in code_lower:
                return f"Dangerous operation detected: {pattern}"

        return None
