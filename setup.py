import sys
from setuptools import find_packages, setup


PY_VERSION = sys.version_info[:2]
dependencies = []
if PY_VERSION == (3, 6):
    dependencies.extend([
        "PyQt5>=5.8.2, <=5.15.0",
        "PyQtExtendedScene @ git+https://github.com/EPC-MSU/PyQtExtendedScene.git@v1.0.14"
    ])
else:
    dependencies.extend([
        "PyQt5",
        "PyQtExtendedScene @ git+https://github.com/EPC-MSU/PyQtExtendedScene.git@master"
    ])

setup(name="boardview",
      version="0.1.4",
      description="Board view widget for EyePoint",
      url="https://github.com/EPC-MSU/board-view",
      author="EPC MSU",
      author_email="info@physlab.ru",
      license="MIT",
      packages=find_packages(),
      python_requires=">=3.6",
      install_requires=dependencies,
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
      zip_safe=False)
