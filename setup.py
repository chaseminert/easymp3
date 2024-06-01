from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()

setup(
    name='easymp3',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'mutagen==1.47.0'
    ],
    author="Chase Minert",
    author_email="cminert58@gmail.com",
    long_description=description,
)
