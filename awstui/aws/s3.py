from typing import Any, List, Dict
from .base import BaseAWSAdapter

class S3Adapter(BaseAWSAdapter):
    async def list_resources(self) -> List[Dict[str, Any]]:
        async with self.client_manager.get_client("s3") as client:
            response = await client.list_buckets()
            buckets = []
            for bucket in response.get("Buckets", []):
                buckets.append({
                    "name": bucket["Name"],
                    "creation_date": bucket["CreationDate"].isoformat()
                })
            return buckets

    async def get_details(self, bucket_name: str) -> Dict[str, Any]:
        async with self.client_manager.get_client("s3") as client:
            # For S3 details, we might want to list objects or get bucket policy/tags
            # For now, let's just return basic info and maybe object count
            return {"name": bucket_name}
