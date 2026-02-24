import httpx
from typing import Optional, Dict, Any
import json
from ..core.config import settings

class LangflowClient:
    def __init__(self):
        self.base_url = settings.LANGFLOW_URL
        self.flow_id = settings.LANGFLOW_FLOW_ID
        
    async def run_flow(self, 
                      message: str,
                      session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a Langflow flow with the given message
        """
        url = f"{self.base_url}/api/v1/run/{self.flow_id}"
        
        payload = {
            "input_value": message,
            "output_type": "chat",
            "input_type": "chat"
        }
        
        if session_id:
            payload["session_id"] = session_id
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url, 
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return {"error": f"HTTP error: {e}"}
            except Exception as e:
                return {"error": str(e)}
    
    async def upload_document(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Upload a document to Langflow for processing
        """
        url = f"{self.base_url}/api/v1/upload/{self.flow_id}"
        
        files = {"file": (filename, file_content, "text/csv")}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, files=files)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"error": str(e)}
