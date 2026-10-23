"""Secure AST-checked Python Math & Statistics Sandbox."""

import ast
import math
import statistics
import time
from typing import Dict, Any, List

class UnsafeCodeException(Exception):
    pass

class PythonSandbox:
    """Restricted execution environment for pure quantitative analytics."""

    ALLOWED_NODES = {
        ast.Module, ast.Expr, ast.Assign, ast.BinOp, ast.UnaryOp,
        ast.Num, ast.Constant, ast.Str, ast.List, ast.Dict, ast.Tuple,
        ast.Name, ast.Load, ast.Store, ast.Call, ast.keyword,
        ast.Compare, ast.IfExp, ast.FormattedValue, ast.JoinedStr,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow
    }

    ALLOWED_CALL_NAMES = {
        "abs", "round", "min", "max", "sum", "len", "float", "int", "str",
        "math.sqrt", "math.pow", "math.log", "math.ceil", "math.floor",
        "statistics.mean", "statistics.median", "statistics.stdev"
    }

    @classmethod
    def validate_ast(cls, code: str):
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if type(node) not in cls.ALLOWED_NODES:
                raise UnsafeCodeException(f"Disallowed AST syntax node '{type(node).__name__}'.")
            
            # Check function calls
            if isinstance(node, ast.Call):
                func = node.func
                func_name = ""
                if isinstance(func, ast.Name):
                    func_name = func.id
                elif isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                    func_name = f"{func.value.id}.{func.attr}"
                
                if func_name not in cls.ALLOWED_CALL_NAMES:
                    raise UnsafeCodeException(f"Call to unauthorized function '{func_name}' is forbidden.")

    @classmethod
    def execute(cls, code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        start = time.time()
        context = context or {}
        try:
            cls.validate_ast(code)
        except Exception as e:
            return {
                "success": False,
                "error": f"Security validation failure: {str(e)}",
                "result": None,
                "execution_time_ms": 0.0
            }

        # Safe global scope
        safe_globals = {
            "__builtins__": {
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                "len": len,
                "float": float,
                "int": int,
                "str": str
            },
            "math": math,
            "statistics": statistics
        }
        
        # Local scope with context variables
        local_scope = dict(context)

        try:
            # Execute code
            exec(code, safe_globals, local_scope)
            # Find newly created variables or "result"
            result_val = local_scope.get("result", None)
            if result_val is None:
                # Pick the last modified variable that was not in context
                new_vars = {k: v for k, v in local_scope.items() if k not in context and not k.startswith("__")}
                result_val = new_vars

            elapsed_ms = round((time.time() - start) * 1000, 2)
            return {
                "success": True,
                "error": None,
                "result": result_val,
                "execution_time_ms": elapsed_ms,
                "locals": {k: v for k, v in local_scope.items() if not k.startswith("__")}
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution runtime error: {str(e)}",
                "result": None,
                "execution_time_ms": round((time.time() - start) * 1000, 2)
            }
