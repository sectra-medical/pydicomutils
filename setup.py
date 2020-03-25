from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name="pydicomutils",
    version="0.0.1",
    description="Python library for creating DICOM objects",
    long_description=README,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Daniel Forsberg",
    author_email="daniel.forsberg@sectra.com",
    url="https://github.com/sectra-medical/pydicomutils",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=[
        "pydicom",
        "SimpleITK",
        "numpy",
        "imageio",
        "scikit-image",
        "pandas",
        "colormath",
        "requests"
    ]
)

if __name__ == '__main__':
    setup(**setup_args)