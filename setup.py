from setuptools import setup, find_packages


setup(
    name="cyphermesh",
    version="1.0.1",

    package_dir={"": "src"},
    packages=find_packages(where="src"),

    include_package_data=True,
    install_requires=[
        "cryptography",
        "flask"
    ],
    entry_points={
        "console_scripts": [
            "cyphermesh-run-peer = cyphermesh.cli.run_peer:main",
            "cyphermesh-reset = cyphermesh.cli.reset:main",
            "cyphermesh-add-peer = cyphermesh.cli.add_peer:main",
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
