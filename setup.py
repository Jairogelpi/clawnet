from setuptools import setup, find_packages

setup(
    name="clawnet",
    version="1.0.0",
    description="Distributed Agent Consciousness Protocol — shared memory for AI agents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="CobosNet",
    url="https://github.com/cobosnet/clawnet",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[],
    extras_require={
        "dev": ["pytest", "requests"],
    },
    entry_points={
        "console_scripts": [
            "clawnet-server=clawnet.server:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
)
