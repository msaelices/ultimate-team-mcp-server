from setuptools import setup, find_packages
import os
import re


# Read requirements
def parse_requirements(filename):
    requirements = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("-r"):
                # If line starts with -r, it's including another requirements file
                req_file = line.split(" ", 1)[1]
                # Skip the reference to requirements.txt in requirements-dev.txt to avoid duplication
                if req_file != "requirements.txt":
                    requirements.extend(parse_requirements(req_file))
                continue
            requirements.append(line)
    return requirements


# Read version from pyproject.toml
def get_version():
    with open("pyproject.toml", "r") as f:
        content = f.read()
        version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
        if version_match:
            return version_match.group(1)
    return "0.1.0"  # Default version if not found


# Read long description from README
def get_long_description():
    if os.path.exists("README.md"):
        with open("README.md", "r") as f:
            return f.read()
    return ""  # Empty if README not found


setup(
    name="ultimate-team-mcp-server",
    version=get_version(),
    description="A Frisbee Team MCP server for managing players",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Manuel Saelices",
    author_email="msaelices@gmail.com",
    url="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=parse_requirements("requirements.txt"),
    extras_require={
        "dev": parse_requirements("requirements-dev.txt"),
    },
    entry_points={
        "console_scripts": [
            "ultimate-team-mcp-server=ultimate_mcp_server:main",
        ],
    },
)
