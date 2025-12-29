import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Iterator, Optional
from contextlib import contextmanager
import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class VercelBlobEvaluationStream:
    """Evaluation stream for Vercel Blob Storage"""
    
    def __init__(self, step_id: str, buffer_size: int = 100, token: str = None):
        self.step_id = step_id
        if buffer_size <= 0:
            raise ValueError("buffer_size must be positive")
        if buffer_size > 10000:
            logger.warning(f"buffer_size {buffer_size} exceeds recommended maximum of 10000")
            buffer_size = 10000
        
        self.buffer_size = buffer_size
        self.token = token or os.getenv('BLOB_READ_WRITE_TOKEN')
        self.base_url = "https://blob.vercel-storage.com"
        self.filename = f"evaluations/{step_id}.jsonl"
        self.buffer: List[Dict] = []
        self.count = 0
        self.passed_count = 0
        self.failed_count = 0
        self._content_lines: List[str] = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()
        self._upload_to_blob()
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
            self._content_lines.append(json.dumps(evaluation))
        
        self.buffer.clear()
    
    def _upload_to_blob(self):
        """Upload accumulated content to Vercel Blob"""
        if not self._content_lines:
            return
        
        content = '\n'.join(self._content_lines) + '\n'
        
        try:
            response = requests.put(
                f"{self.base_url}/{self.filename}",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/x-ndjson"
                },
                data=content.encode('utf-8')
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to upload evaluations to Vercel Blob: {response.text}")
        except Exception as e:
            logger.exception(f"Error uploading evaluations: {e}")
    
    def get_summary(self) -> Dict:
        pass_rate = 0.0
        if self.count > 0:
            pass_rate = round((self.passed_count / self.count) * 100, 2)
        
        return {
            "mode": "stream",
            "file": f"xray_data/{self.filename}",
            "total": self.count,
            "passed": self.passed_count,
            "failed": self.failed_count,
            "pass_rate": pass_rate
        }
    
    @staticmethod
    def load_from_file(filepath: str, page: int = 0, page_size: int = 100) -> List[Dict]:
        """Load evaluations from Vercel Blob"""
        token = os.getenv('BLOB_READ_WRITE_TOKEN')
        base_url = "https://blob.vercel-storage.com"
        
        filename = filepath.replace('xray_data/', '')
        
        try:
            response = requests.get(
                f"{base_url}/{filename}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to load evaluations from blob: {response.text}")
                return []
            
            # Parse JSONL content
            lines = response.text.strip().split('\n')
            start_line = page * page_size
            end_line = start_line + page_size
            
            evaluations = []
            for i, line in enumerate(lines[start_line:end_line]):
                try:
                    evaluations.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse evaluation line: {e}")
                    continue
            
            return evaluations
            
        except Exception as e:
            logger.exception(f"Error loading evaluations from blob: {e}")
            return []


class LocalEvaluationStream:
    """Local filesystem evaluation stream"""
    
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


def EvaluationStream(step_id: str, buffer_size: int = 100, output_dir: str = "./xray_data/evaluations"):
    """Create an evaluation stream based on deployment mode"""
    deployment_mode = os.getenv('DEPLOYMENT_MODE', 'local')
    
    if deployment_mode == 'vercel':
        return VercelBlobEvaluationStream(step_id, buffer_size)
    else:
        return LocalEvaluationStream(step_id, buffer_size, output_dir)
