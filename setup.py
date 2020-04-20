from setuptools import setup

description = "Board view widget for EyePoint"

setup(name='boardview',
      version='0.0.0',
      description=description,
      long_description=description,
      long_description_content_type="text/markdown",
      url='https://github.com/EPC-MSU/board-view',
      author='EPC MSU',
      author_email='mihalin@physlab.ru',
      license='MIT',
      packages=['boardview'],
      install_requires=[
            'PyQtExtendedScene',
      ],
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
      python_requires='>=3.6',
      zip_safe=False)
