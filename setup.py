"""
Setuptools configuration for the todo-cli package.

This setup.py file defines the metadata and dependencies for the todo-cli
package, which is a command-line interface tool for managing tasks using the
Todo.txt format.

The package is distributed on PyPI and can be installed using pip.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="todo-cli",
    version="0.1.0",
    author="ci-c",
    author_email="author@example.com",
    description="A command-line interface tool for managing tasks using the "
                "Todo.txt format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ci-c/todo-cli",
    packages=find_packages(),
    install_requires=[
        "click",
    ],
    entry_points={
        "console_scripts": [
            "todo=todo_cli.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
