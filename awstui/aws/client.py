import aiobotocore.session
from contextlib import asynccontextmanager
from typing import AsyncGenerator

class AWSClientManager:
    def __init__(self, profile_name: str = None, region_name: str = None):
        # In aiobotocore, profile is set at the session level
        self.session = aiobotocore.session.get_session()
        self.profile_name = profile_name
        self.region_name = region_name
        self.access_key = None
        self.secret_key = None

    @asynccontextmanager
    async def get_client(self, service_name: str) -> AsyncGenerator:
        # If we have manual keys, use them. Otherwise use profile.
        kwargs = {
            "service_name": service_name,
            "region_name": self.region_name
        }
        
        if self.access_key and self.secret_key:
            kwargs["aws_access_key_id"] = self.access_key
            kwargs["aws_secret_access_key"] = self.secret_key
        elif self.profile_name:
            self.session.set_config_variable('profile', self.profile_name)
            
        async with self.session.create_client(**kwargs) as client:
            yield client

    def update_config(self, profile_name: str = None, region_name: str = None, access_key: str = None, secret_key: str = None):
        self.profile_name = profile_name
        self.region_name = region_name
        self.access_key = access_key
        self.secret_key = secret_key
