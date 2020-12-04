import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gradeit",
    version="0.0.1",
    author="National Renewable Energy Laboratory",
    author_email="Jacob.Holden@nrel.gov",
    description="Road Grade Inference Tool (GradeIT) appends elevation and road grade to a sequence of GPS points.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NREL/gradeit",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD 3-Clause License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering"
    ],
    python_requires='>=3.7',
    install_requires=[
        "gdal>=2.3",
        "geos",
        "ipykernel",
        "ipython",
        "matplotlib",
        "numpy",
        "pandas",
        "requests",
        "scipy",
        "sqlalchemy",
        "psycopg2",
    ],
)