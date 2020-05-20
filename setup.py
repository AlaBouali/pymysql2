import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymysql2",
    version="1.2.4",
    author="AlaBouali",
    author_email="trap.leader.123@gmail.com",
    description="Simple and secure module to perform safe MySQL queries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlaBouali/bane",
    python_requires=">=2.7",
    install_requires=['pymysql'],
    packages=["pymysql2"],
    license="MIT License",
    entry_points={
       'console_scripts': [
           'xmysql = pymysql2.__main__:run',
       ],
    },
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License ",
    ],
)
