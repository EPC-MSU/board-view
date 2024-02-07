from setuptools import find_packages, setup


setup(name="boardview",
      version="0.1.3",
      description="Board view widget for EyePoint",
      url="https://github.com/EPC-MSU/board-view",
      author="EPC MSU",
      author_email="info@physlab.ru",
      license="MIT",
      packages=find_packages(),
      python_requires=">=3.6",
      install_requires=[
            "PyQt5>=5.8.2, <=5.15.0"
      ],
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
      zip_safe=False)
