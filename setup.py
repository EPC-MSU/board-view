from setuptools import find_packages, setup


setup(name="boardview",
      version="2.0.2",
      description="Board view widget for EyePoint",
      url="https://github.com/EPC-MSU/board-view",
      author="EPC MSU",
      author_email="info@physlab.ru",
      license="MIT",
      packages=find_packages(),
      python_requires=">=3.6",
      install_requires=[
            "Pillow<10.0.0",
            'PyQt5>=5.8.2, <=5.15.0; python_version=="3.6"',
            'PyQt5; python_version>"3.6"'
            "PyQtExtendedScene @ git+https://github.com/EPC-MSU/PyQtExtendedScene@v2.0.1#egg=PyQtExtendedScene"
      ],
      package_data={"boardview": ["translation/translation_ru.qm"]},
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
      zip_safe=False)
