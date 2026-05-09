from typing import Any, List, Dict
from .base import BaseAWSAdapter

class ECSAdapter(BaseAWSAdapter):
    async def list_resources(self) -> List[Dict[str, Any]]:
        async with self.client_manager.get_client("ecs") as client:
            response = await client.list_clusters()
            clusters = []
            for cluster_arn in response.get("clusterArns", []):
                clusters.append({
                    "name": cluster_arn.split("/")[-1],
                    "arn": cluster_arn
                })
            return clusters

    async def get_details(self, cluster_name: str) -> Dict[str, Any]:
        async with self.client_manager.get_client("ecs") as client:
            response = await client.describe_clusters(clusters=[cluster_name])
            return response.get("clusters", [{}])[0]
