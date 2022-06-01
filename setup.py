import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nyt_comments_scraper",
    version="1.0.0",
    author="Jiali Galarza",
    author_email="jialigalarza@gmail.com",
    description="New York Times comments scraper by article(s)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jiali-jihuan/nyt_comments_scraper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)



