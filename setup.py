from setuptools import setup, find_packages

setup(
    name="cyphermesh",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "cryptography",
        "flask"
    ],
    entry_points={
        "console_scripts": [
            "cyphermesh-install = cli.install:main",
            "cyphermesh-peer = cli.run_peer:main",
            "cyphermesh-discovery-server = cli.run_discovery_server:main"
        ]
    },
    author="Massimo Fedrigo",
    description="cyphermesh - P2P Threat Intelligence Network",
    keywords=["cybersecurity", "p2p", "distributed", "threat intelligence"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.8',
)
