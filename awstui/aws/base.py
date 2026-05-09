import abc
from typing import Any, List, Dict
from .client import AWSClientManager

class BaseAWSAdapter(abc.ABC):
    def __init__(self, client_manager: AWSClientManager):
        self.client_manager = client_manager

    @abc.abstractmethod
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List resources for the specific service."""
        pass

    @abc.abstractmethod
    async def get_details(self, resource_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific resource."""
        pass
