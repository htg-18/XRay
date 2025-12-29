import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Iterator, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class EvaluationStream:
    def __init__(self, step_id: str, buffer_size: int = 100, output_dir: str = "./xray_data/evaluations"):
        self.step_id = step_id
        if buffer_size <= 0:
            raise ValueError("buffer_size must be positive")
        if buffer_size > 10000:
            logger.warning(f"buffer_size {buffer_size} exceeds recommended maximum of 10000")
            buffer_size = 10000  
        
        self.buffer_size = buffer_size
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.filename = f"{step_id}.jsonl"
        self.filepath = self.output_dir / self.filename
        self._file_handle = None
        self.buffer: List[Dict] = []
        self.count = 0
        self.passed_count = 0
        self.failed_count = 0
    
    def __enter__(self):
        self._file_handle = open(self.filepath, 'w', encoding='utf-8')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()
        if self._file_handle:
            self._file_handle.close()
        return False
    
    def write(self, evaluation: Dict):
        self.buffer.append(evaluation)
        
        self.count += 1
        if evaluation.get("qualified", False):
            self.passed_count += 1
        else:
            self.failed_count += 1
        
        if len(self.buffer) >= self.buffer_size:
            self.flush()
    
    def flush(self):
        if not self.buffer:
            return
        
        for evaluation in self.buffer:
            self._file_handle.write(json.dumps(evaluation) + '\n')
        
        self.buffer.clear()
    
    def get_summary(self) -> Dict:
        pass_rate = 0.0
        if self.count > 0:
            pass_rate = round((self.passed_count / self.count) * 100, 2)
        
        relative_path = Path("xray_data") / "evaluations" / self.filename
        
        return {
            "mode": "stream",
            "file": str(relative_path).replace("\\", "/"),
            "total": self.count,
            "passed": self.passed_count,
            "failed": self.failed_count,
            "pass_rate": pass_rate
        }
    
    def iterate(self, page: int = 0, page_size: int = 100) -> List[Dict]:
        
        if not self.filepath.exists():
            return []
        
        evaluations = []
        start_line = page * page_size
        end_line = start_line + page_size
        
        with open(self.filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i < start_line:
                    continue
                if i >= end_line:
                    break
                
                try:
                    evaluations.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse evaluation at line {i+1} in {self.filepath}: {e}")
                    continue
        
        return evaluations
    
    def get_all(self) -> Iterator[Dict]:
        if not self.filepath.exists():
            return
        
        with open(self.filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse evaluation at line {i+1} in {self.filepath}: {e}")
                    continue 
    
    @staticmethod
    def load_from_file(filepath: str, page: int = 0, page_size: int = 100) -> List[Dict]:
        evaluations = []
        start_line = page * page_size
        end_line = start_line + page_size
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i < start_line:
                        continue
                    if i >= end_line:
                        break
                    
                    try:
                        evaluations.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse evaluation at line {i+1} in {filepath}: {e}")
                        continue  
        except FileNotFoundError:
            logger.warning(f"Evaluation file not found: {filepath}")
        except Exception as e:
            logger.exception(f"Unexpected error reading evaluation file {filepath}: {e}")
        
        return evaluations

