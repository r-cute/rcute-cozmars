import setuptools

with open("./README.md", 'r') as f:
    long_description = f.read()

with open('./requirements.txt', 'r') as f:
    requirements = [a.strip() for a in f]


import os
here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'rcute_cozmars', 'version.py')) as f:
    ns = {}
    exec(f.read(), ns)
    version = ns['__version__']

setuptools.setup(
    name="rcute-cozmars",
    version=version,
    author="Huang Yan",
    author_email="hyansuper@foxmail.com",
    description="Python SDK for Cozmars, the 3d printable educational robot.",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hyansuper/rcute-cozmars",
    packages=['rcute_cozmars'],
    install_requires=requirements,
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)