import setuptools

with open("README.md", "r") as fh:
        long_description = fh.read()

setuptools.setup(
    name="jazz-lib",
    version="0.0.1",
    author="Ryan Lee",
    author_email="ryanlee250@gmail.com",
    description="A program that lets you search jazz records",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/savoy1211/jazz-lib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
