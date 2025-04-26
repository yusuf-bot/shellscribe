from setuptools import setup

setup(
    name="shellscribe",
    version="0.1.0",
    description="A CLI tool to generate and insert code using AI",
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