from setuptools import setup, find_packages

setup(
    name="awstui",
    version="1.0.4",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "textual>=0.50.0",
        "aiobotocore>=2.12.0",
        "boto3>=1.34.0",
        "python-dotenv>=1.0.1",
    ],
    entry_points={
        "console_scripts": [
            "awstui=main:main",
        ],
    },
)
