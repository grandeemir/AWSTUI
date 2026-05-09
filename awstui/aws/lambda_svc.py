from typing import Any, List, Dict
from .base import BaseAWSAdapter

class LambdaAdapter(BaseAWSAdapter):
    async def list_resources(self) -> List[Dict[str, Any]]:
        async with self.client_manager.get_client("lambda") as client:
            response = await client.list_functions()
            functions = []
            for func in response.get("Functions", []):
                functions.append({
                    "name": func["FunctionName"],
                    "runtime": func["Runtime"],
                    "handler": func["Handler"],
                    "modified": func["LastModified"]
                })
            return functions

    async def get_details(self, function_name: str) -> Dict[str, Any]:
        async with self.client_manager.get_client("lambda") as client:
            response = await client.get_function(FunctionName=function_name)
            return response.get("Configuration", {})
