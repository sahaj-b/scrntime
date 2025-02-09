from setuptools import setup

setup(
    name='scrntime',
    version='0.1.0',  # Update this version on new releases
    py_modules=['scrntime'],  # Because your script is a single module file
    entry_points={
        'console_scripts': [
            'scrntime=scrntime:main',  # creates a command 'scrntime'
        ],
    },
    install_requires=[ ],
    author='Sahaj Bhatt',
    author_email='sahajb0606@gmail.com',
    description='A CLI for displaying daily screentime with afk/idle time support',
    url='https://github.com/sahaj-b/scrntime.git',
    license='BSD',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Linux',
    ],
)
