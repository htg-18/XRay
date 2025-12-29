import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Storage:
    def __init__(self, base_dir: str = "./xray_data"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def save(self, execution_data: Dict, filename: Optional[str] = None) -> str:
        if filename is None:
            filename = f"{execution_data['id']}.json"
        
        filepath = self.base_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(execution_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def load(self, execution_id: str) -> Dict:
        filepath = self.base_dir / f"{execution_id}.json"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Execution {execution_id} not found")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_executions(self) -> List[Dict]:
        executions = []
        
        for filepath in self.base_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    executions.append({
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "timestamp_start": data.get("timestamp_start"),
                        "status": data.get("status"),
                        "duration_ms": data.get("duration_ms")
                    })
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse execution file {filepath}: {e}")
                continue  # Skip invalid files, but log it
            except Exception as e:
                logger.exception(f"Unexpected error reading execution file {filepath}: {e}")
                continue
        
        executions.sort(key=lambda x: x.get("timestamp_start", ""), reverse=True)
        return executions
    
    def delete(self, execution_id: str):
        filepath = self.base_dir / f"{execution_id}.json"
        if filepath.exists():
            filepath.unlink()


_default_storage = Storage()


def save_execution(execution_data: Dict, filename: Optional[str] = None) -> str:
    return _default_storage.save(execution_data, filename)


def load_execution(execution_id: str) -> Dict:
    return _default_storage.load(execution_id)


def list_executions() -> List[Dict]:
    return _default_storage.list_executions()

