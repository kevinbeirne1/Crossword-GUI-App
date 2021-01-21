import os.path
import setuptools

# The directory containing this file
here = os.path.abspath(os.path.dirname(__file__))



with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fh:
    read_me = fh.read()

setuptools.setup(
    name="ny_crossword_gui", 
    version="0.0.1",
    description="Scrape crossword from website and display in GUI",
    long_description=read_me,
    long_description_content_type="text/markdown",
    url="https://github.com/kevinbeirne1/Crossword-GUI-App",
    author="Kevin Beirne",
    author_email="author@example.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["crossword_gui"],
    python_requires='>=3.6',
    install_requires=[scrapy, PyQt5],
    entry_points={"console_scripts": ["crossword_tool=crossword_gui.__main__:main]}

)