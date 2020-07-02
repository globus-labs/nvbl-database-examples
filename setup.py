import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
packages = (setuptools.find_packages(),)
setuptools.setup(
    name="nvbl_client",
    version="0.0.1",
    author="Ben Blaiszik",
    author_email="blaiszik@uchicago.edu",
    packages=setuptools.find_packages(),
    description="Package to support interaction with NVBL data infrastructure elements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["requests",],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
    ],
    keywords=[],
    license="MIT License",
    url="https://github.com/globus-labs/nvbl-database-examples",
)
