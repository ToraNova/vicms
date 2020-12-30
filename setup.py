from setuptools import find_packages, setup
from viauth.vial import name, description, version

setup(
    name=name,
    version=version,
    description=description,
    packages=find_packages(),
    author='Chia Jason',
    author_email='unreason78@gmail.com',
    url='https://github.com/toranova/vicms/',
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask','sqlalchemy'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
