from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shellscribe",
    version="0.1.3",
    description="A CLI tool to generate and insert code using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Yusuf Sabuwala",
    author_email="yusuff.0279@example.com",
    py_modules=["shellscribe"],
    install_requires=[
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "shellscribe=shellscribe:main"
        ]
    },
    include_package_data=True,
    python_requires=">=3.7",
)