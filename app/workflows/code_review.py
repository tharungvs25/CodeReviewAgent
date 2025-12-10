# workflows/code_review.py
from typing import Dict, Any
from models.graph_models import GraphDefinition, GraphNodeConfig
from engine.registry import tool_registry


def register_code_review_tools():
    """Register all tools needed for the code review workflow."""
    
    def extract_functions(state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract function names from code."""
        code = state.get("code", "")
        # Simple function extraction (looks for 'def ' keyword)
        functions = []
        for line in code.split('\n'):
            line = line.strip()
            if line.startswith('def '):
                func_name = line.split('(')[0].replace('def ', '').strip()
                if func_name:
                    functions.append(func_name)
        state["functions"] = functions
        return state
    
    def check_complexity(state: Dict[str, Any]) -> Dict[str, Any]:
        """Check code complexity metrics."""
        code = state.get("code", "")
        lines = [line for line in code.split('\n') if line.strip()]
        functions = state.get("functions", [])
        
        state["complexity"] = {
            "total_lines": len(lines),
            "num_functions": len(functions),
            "avg_line_length": sum(len(line) for line in lines) / max(len(lines), 1)
        }
        return state
    
    def detect_issues(state: Dict[str, Any]) -> Dict[str, Any]:
        """Detect basic code issues."""
        code = state.get("code", "")
        issues = {
            "missing_docstrings": 0,
            "long_lines": 0,
            "todo_comments": 0
        }
        
        for line in code.split('\n'):
            if len(line) > 100:
                issues["long_lines"] += 1
            if 'TODO' in line or 'FIXME' in line:
                issues["todo_comments"] += 1
        
        # Check for docstrings
        if 'def ' in code and '"""' not in code and "'''" not in code:
            issues["missing_docstrings"] = code.count('def ')
        
        state["issues"] = issues
        return state
    
    def suggest_improvements(state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate improvement suggestions."""
        issues = state.get("issues", {})
        complexity = state.get("complexity", {})
        
        suggestions_list = []
        
        if issues.get("missing_docstrings", 0) > 0:
            suggestions_list.append("Add docstrings to your functions")
        if issues.get("long_lines", 0) > 0:
            suggestions_list.append(f"Break down {issues['long_lines']} long lines (>100 chars)")
        if issues.get("todo_comments", 0) > 0:
            suggestions_list.append(f"Address {issues['todo_comments']} TODO/FIXME comments")
        if complexity.get("num_functions", 0) == 0:
            suggestions_list.append("Consider breaking code into functions")
        if complexity.get("avg_line_length", 0) > 80:
            suggestions_list.append("Consider reducing average line length")
        
        state["suggestions"] = {
            "suggestions": suggestions_list
        }
        return state
    
    def check_quality(state: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality score and determine if we should loop."""
        issues = state.get("issues", {})
        complexity = state.get("complexity", {})
        threshold = state.get("threshold", 0.8)
        
        # Calculate quality score (simple heuristic)
        total_issues = sum(issues.values())
        num_functions = complexity.get("num_functions", 0)
        
        # Score based on issues and structure
        base_score = 1.0
        base_score -= min(0.3, total_issues * 0.05)  # Deduct for issues
        if num_functions == 0:
            base_score -= 0.2  # Deduct if no functions
        
        state["quality_score"] = max(0.0, min(1.0, base_score))
        
        # Loop if quality is below threshold (set _next_node to loop back)
        if state["quality_score"] < threshold:
            # In a real system, this would loop back to improvements
            # For now, we just mark it and end
            pass
        
        return state
    
    # Register all tools
    tool_registry.register("extract_functions", extract_functions)
    tool_registry.register("check_complexity", check_complexity)
    tool_registry.register("detect_issues", detect_issues)
    tool_registry.register("suggest_improvements", suggest_improvements)
    tool_registry.register("check_quality", check_quality)


def create_code_review_graph() -> GraphDefinition:
    """Create a default code review workflow graph."""
    return GraphDefinition(
        id="code_review",
        nodes={
            "extract": GraphNodeConfig(tool_name="extract_functions"),
            "complexity": GraphNodeConfig(tool_name="check_complexity"),
            "issues": GraphNodeConfig(tool_name="detect_issues"),
            "suggestions": GraphNodeConfig(tool_name="suggest_improvements"),
            "quality": GraphNodeConfig(tool_name="check_quality"),
        },
        edges={
            "extract": "complexity",
            "complexity": "issues",
            "issues": "suggestions",
            "suggestions": "quality",
            "quality": None,  # End of workflow
        },
        start_node="extract"
    )
