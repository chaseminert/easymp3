from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()

setup(
    name='easymp3',
    version='1.2',
    packages=find_packages(),
    install_requires=[
        'mutagen==1.47.0'
    ],
    author="Chase Minert",
    author_email="cminert58@gmail.com",
    description="Easily tag and manipulate MP3 files in a programmatic way.",
    long_description=description,
    long_description_content_type="text/markdown",
)
