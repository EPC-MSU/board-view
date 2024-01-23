from setuptools import find_packages, setup


setup(name="boardview",
      version="0.1.2",
      description="Board view widget for EyePoint",
      url="https://github.com/EPC-MSU/board-view",
      author="EPC MSU",
      author_email="info@physlab.ru",
      license="MIT",
      packages=find_packages(),
      python_requires=">=3.6",
      install_requires=[
            "PyQtExtendedScene==1.0.12",
      ],
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
      zip_safe=False)
