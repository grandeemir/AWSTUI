import pytest
from awstui.app import AWSTUIApp
from awstui.aws.client import AWSClientManager

def test_app_initialization():
    app = AWSTUIApp()
    assert app.TITLE == "AWS TUI Manager"
    assert "nav-ec2" in app.adapters
    assert isinstance(app.client_manager, AWSClientManager)

def test_aws_client_manager():
    manager = AWSClientManager(profile_name="test-profile", region_name="us-east-1")
    assert manager.profile_name == "test-profile"
    assert manager.region_name == "us-east-1"
