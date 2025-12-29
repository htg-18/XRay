import time
import uuid
from contextlib import contextmanager
from typing import Any, Callable, Optional, List, Dict
from datetime import datetime

class Step:
    def __init__(self, name: str, step_type: str = "generic", reasoning: str = ""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.step_type = step_type
        self.reasoning = reasoning
        self.timestamp_start = datetime.utcnow().isoformat()
        self.timestamp_end = None
        self.duration_ms = None
        self.input_data = None
        self.output_data = None
        self.evaluations = []
        self.metadata = {}
        self.status = "running"
        self.error = None
        self._start_time = time.time()
    
    def set_input(self, **kwargs):
        self.input_data = kwargs
    
    def set_output(self, data: Any):
        self.output_data = data
    
    def set_reasoning(self, reasoning: str):
        self.reasoning = reasoning
    
    def record_evaluations(self, evaluations: List[Dict]):
        self.evaluations = evaluations
    
    def evaluation_stream(self, buffer_size: int = 100):
        from .streaming import EvaluationStream
        from contextlib import contextmanager
        
        @contextmanager
        def _stream_context():
            stream = EvaluationStream(self.id, buffer_size=buffer_size)
            with stream:
                yield stream
            self.evaluations = stream.get_summary()
        
        return _stream_context()
    
    def set_metadata(self, **kwargs):
        self.metadata.update(kwargs)
    
    def set_error(self, error: Exception):
        self.error = {
            "type": type(error).__name__,
            "message": str(error)
        }
        self.status = "failed"
    
    def _finalize(self):
        self.timestamp_end = datetime.utcnow().isoformat()
        self.duration_ms = round((time.time() - self._start_time) * 1000, 2)
        if self.status == "running":
            self.status = "success"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "step_type": self.step_type,
            "reasoning": self.reasoning,
            "timestamp_start": self.timestamp_start,
            "timestamp_end": self.timestamp_end,
            "duration_ms": self.duration_ms,
            "input": self.input_data,
            "output": self.output_data,
            "evaluations": self.evaluations,
            "metadata": self.metadata,
            "status": self.status,
            "error": self.error
        }

class XRayExecution:
    def __init__(self, name: str, tags: Optional[Dict] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.tags = tags or {}
        self.timestamp_start = datetime.utcnow().isoformat()
        self.timestamp_end = None
        self.duration_ms = None
        self.status = "running"
        self.steps: List[Step] = []
        self.current_step: Optional[Step] = None
        self.error = None
        self._start_time = time.time()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._finalize(exc_type, exc_val)
        return False 
    
    def step(self, name: str, fn: Optional[Callable] = None, 
             step_type: str = "generic", reasoning: str = "", **kwargs):
        if fn is not None:
            return self._auto_step(name, fn, step_type, reasoning, **kwargs)
        else:
            return self._manual_step_context(name, step_type, reasoning)
    
    def _auto_step(self, name: str, fn: Callable, step_type: str, 
                   reasoning: str, args=(), kwargs=None):
        kwargs = kwargs or {}
        step = Step(name, step_type, reasoning)
        step.set_input(args=args, kwargs=kwargs)
        
        try:
            result = fn(*args, **kwargs)
            step.set_output(result)
            step.status = "success"
        except Exception as e:
            step.set_error(e)
            raise
        finally:
            step._finalize()
            self.steps.append(step)
        
        return result
    
    @contextmanager
    def _manual_step_context(self, name: str, step_type: str, reasoning: str):
        step = Step(name, step_type, reasoning)
        self.current_step = step
        
        try:
            yield step
            step.status = "success"
        except Exception as e:
            step.set_error(e)
            step.status = "failed"
            raise
        finally:
            step._finalize()
            self.steps.append(step)
            self.current_step = None
    
    def _finalize(self, exc_type=None, exc_val=None):
        self.timestamp_end = datetime.utcnow().isoformat()
        self.duration_ms = round((time.time() - self._start_time) * 1000, 2)
        
        if exc_type is not None:
            self.status = "failed"
            self.error = {
                "type": exc_type.__name__,
                "message": str(exc_val)
            }
        else:
            self.status = "completed"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "tags": self.tags,
            "timestamp_start": self.timestamp_start,
            "timestamp_end": self.timestamp_end,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "error": self.error,
            "steps": [step.to_dict() for step in self.steps]
        }

class XRay:
    @staticmethod
    def start(name: str, tags: Optional[Dict] = None) -> XRayExecution:
        return XRayExecution(name, tags)

