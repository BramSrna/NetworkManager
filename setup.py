#!/usr/bin/env python3

import os
from setuptools import setup

directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(directory, 'README.md'), encoding='utf-8') as f:
  long_description = f.read()

setup(name='NetworkManager',
      version='1.0.0',
      description='Extensible utility for deploying and controlling a network of nodes.',
      author='Abraham Srna',
      license='MIT',
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages = ['network_manager'],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
      ],
      install_requires=['numpy', 'requests', 'pillow', 'networkx'],
      python_requires='>=3.8',
      extras_require={
        'gpu': ["pyopencl", "six"],
        'llvm': ["llvmlite"],
        'testing': [
            "pytest",
            "torch~=1.11.0",
            "tqdm",
            "protobuf~=3.19.0",
            "onnx",
            "onnx2torch",
            "mypy",
        ],
      },
      include_package_data=True)