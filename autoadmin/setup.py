from setuptools import setup, find_packages

setup(
    name="autoadmin",
    version="0.1.0",
    description="Automation tools for ArcGIS administration",
    author="Jerad King",
    author_email="jerad.king@gcoos.org",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "arcgis"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)