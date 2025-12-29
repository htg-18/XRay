"""
X-Ray: Decision Process Debugger
A library for capturing and visualizing multi-step decision-making processes.
"""

from .core import XRay, XRayExecution, Step
from .streaming import EvaluationStream

__version__ = "0.1.0"
__all__ = ["XRay", "XRayExecution", "Step", "EvaluationStream"]

