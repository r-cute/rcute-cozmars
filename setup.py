import setuptools

with open("./README.md", 'r') as f:
    long_description = f.read()

with open('./requirements.txt', 'r') as f:
    requirements = [a.strip() for a in f]

setuptools.setup(
    name="rcute-cozmars",
    version="1.0.2",
    author="Huang Yan",
    author_email="hyansuper@foxmail.com",
    description="Python SDK for Cozmars, the 3d printable educational robot.",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hyansuper/rcute-cozmars",
    packages=['rcute_cozmars'],
    install_requires=requirements,
    classifiers=(
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)