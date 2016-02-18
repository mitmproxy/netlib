from setuptools import setup, find_packages

setup(
    name="netlib",
    version="0.17",
    description="A collection of network utilities used by pathod and mitmproxy.",
    long_description="netlib is now part of mitmproxy. This package does nothing but install mitmproxy.",
    url="http://github.com/mitmproxy/netlib",
    author="Aldo Cortesi",
    author_email="aldo@corte.si",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 7 - Inactive",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Testing :: Traffic Generation",
    ],
    packages=[],
    install_requires=["mitmproxy>=0.17"]
)
