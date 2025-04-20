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
            "cyphermesh-run-peer = cli.run_peer:main",
            "cyphermesh-reset = cli.reset:main",
            "cyphermesh-add-peer = cli.add_peer:main",
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
