import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='nba-scrape',
    version='0.12',
    description='Python utility to easily scrape NBA stats',
    long_description=long_description,
    packages = setuptools.find_packages(),
    author='Hamza Qadeer',
    author_email='hamza.qadeer@berkeley.edu',
    url='https://github.com/hqadeer/nba-stats.git',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'lxml',
        'bs4',
        'Selenium',
    ]
)
