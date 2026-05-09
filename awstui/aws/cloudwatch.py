from typing import Any, List, Dict
from .base import BaseAWSAdapter

class CloudWatchAdapter(BaseAWSAdapter):
    async def list_resources(self) -> List[Dict[str, Any]]:
        async with self.client_manager.get_client("cloudwatch") as client:
            response = await client.list_metrics()
            metrics = []
            for metric in response.get("Metrics", [])[:50]:  # Limit for display
                metrics.append({
                    "namespace": metric["Namespace"],
                    "name": metric["MetricName"],
                    "dimensions": str([d["Name"] for d in metric.get("Dimensions", [])])
                })
            return metrics

    async def get_details(self, metric_name: str) -> Dict[str, Any]:
        return {"metric_name": metric_name, "info": "Detailed stats would require GetMetricData"}
