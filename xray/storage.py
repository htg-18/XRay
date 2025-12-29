import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class VercelBlobStorage:
    """Storage backend using Vercel Blob Storage API"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://blob.vercel-storage.com"
    
    def save(self, execution_data: Dict, filename: Optional[str] = None) -> str:
        if filename is None:
            filename = f"{execution_data['id']}.json"
        
        content = json.dumps(execution_data, indent=2, ensure_ascii=False)
        
        response = requests.put(
            f"{self.base_url}/{filename}",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            data=content.encode('utf-8')
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to upload to Vercel Blob: {response.text}")
        
        result = response.json()
        return result.get('url', filename)
    
    def load(self, execution_id: str) -> Dict:
        filename = f"{execution_id}.json"
        
        response = requests.get(
            f"{self.base_url}/{filename}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 404:
            raise FileNotFoundError(f"Execution {execution_id} not found")
        
        if response.status_code != 200:
            raise Exception(f"Failed to load from Vercel Blob: {response.text}")
        
        return response.json()
    
    def list_executions(self) -> List[Dict]:
        response = requests.get(
            f"{self.base_url}/",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to list blobs: {response.text}")
            return []
        
        blobs = response.json().get('blobs', [])
        executions = []
        
        for blob in blobs:
            if blob['pathname'].endswith('.json'):
                try:
                    data = self.load(blob['pathname'].replace('.json', ''))
                    executions.append({
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "timestamp_start": data.get("timestamp_start"),
                        "status": data.get("status"),
                        "duration_ms": data.get("duration_ms")
                    })
                except Exception as e:
                    logger.warning(f"Failed to load execution metadata for {blob['pathname']}: {e}")
                    continue
        
        executions.sort(key=lambda x: x.get("timestamp_start", ""), reverse=True)
        return executions
    
    def delete(self, execution_id: str):
        filename = f"{execution_id}.json"
        
        response = requests.delete(
            f"{self.base_url}/{filename}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code not in (200, 204, 404):
            logger.warning(f"Failed to delete blob {filename}: {response.text}")


class LocalStorage:
    """Local filesystem storage backend"""
    
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
                continue
            except Exception as e:
                logger.exception(f"Unexpected error reading execution file {filepath}: {e}")
                continue
        
        executions.sort(key=lambda x: x.get("timestamp_start", ""), reverse=True)
        return executions
    
    def delete(self, execution_id: str):
        filepath = self.base_dir / f"{execution_id}.json"
        if filepath.exists():
            filepath.unlink()


def _get_storage_backend():
    deployment_mode = os.getenv('DEPLOYMENT_MODE', 'local')
    
    if deployment_mode == 'vercel':
        blob_token = os.getenv('BLOB_READ_WRITE_TOKEN')
        if not blob_token:
            logger.warning("BLOB_READ_WRITE_TOKEN not set, falling back to local storage")
            return LocalStorage()
        return VercelBlobStorage(blob_token)
    else:
        return LocalStorage()


_default_storage = _get_storage_backend()


def save_execution(execution_data: Dict, filename: Optional[str] = None) -> str:
    return _default_storage.save(execution_data, filename)


def load_execution(execution_id: str) -> Dict:
    return _default_storage.load(execution_id)


def list_executions() -> List[Dict]:
    return _default_storage.list_executions()
