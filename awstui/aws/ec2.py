from typing import Any, List, Dict
from .base import BaseAWSAdapter

class EC2Adapter(BaseAWSAdapter):
    async def list_resources(self) -> List[Dict[str, Any]]:
        async with self.client_manager.get_client("ec2") as client:
            response = await client.describe_instances()
            instances = []
            for reservation in response.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    instances.append({
                        "id": instance["InstanceId"],
                        "type": instance["InstanceType"],
                        "state": instance["State"]["Name"],
                        "name": next((tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"), "N/A"),
                        "public_ip": instance.get("PublicIpAddress", "N/A"),
                        "launch_time": instance["LaunchTime"].isoformat() if "LaunchTime" in instance else "N/A"
                    })
            return instances

    async def get_details(self, instance_id: str) -> Dict[str, Any]:
        async with self.client_manager.get_client("ec2") as client:
            response = await client.describe_instances(InstanceIds=[instance_id])
            reservations = response.get("Reservations", [])
            if reservations:
                return reservations[0]["Instances"][0]
            return {}

    async def stop_instance(self, instance_id: str) -> Dict[str, Any]:
        async with self.client_manager.get_client("ec2") as client:
            return await client.stop_instances(InstanceIds=[instance_id])

    async def start_instance(self, instance_id: str) -> Dict[str, Any]:
        async with self.client_manager.get_client("ec2") as client:
            return await client.start_instances(InstanceIds=[instance_id])

    async def terminate_instance(self, instance_id: str) -> Dict[str, Any]:
        async with self.client_manager.get_client("ec2") as client:
            return await client.terminate_instances(InstanceIds=[instance_id])
