from setuptools import setup, find_packages

setup(
    name="pepe_stream_server",
    description="Pepe stream server",
    version="0.0.1",
    src=find_packages(),
    install_requires=[
        "aiohttp[speedups]==3.7.3",
        "python-dotenv==0.15.0",
        "aiortc==1.1.1",
    ],
)