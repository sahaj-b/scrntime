from setuptools import setup

setup(
    name="scrntime",
    version="1.4.1",
    py_modules=["scrntime"],
    entry_points={
        "console_scripts": [
            "scrntime=scrntime:main",
        ],
    },
    install_requires=[],
    author="Sahaj Bhatt",
    author_email="sahajb0606@gmail.com",
    description="A CLI for displaying daily screentime with afk/idle time support",
    url="https://github.com/sahaj-b/scrntime.git",
    license="BSD",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
    ],
)
