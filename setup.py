from setuptools import setup, find_packages

import viflow

setup(
    name='viflow',
    version=viflow.__version__,
    url='https://github.ibm.com/aur-bic/video-to-opticalflow',
    author='Stefan Maetschke',
    author_email='stefanrm@au1.ibm.com',
    description='Convert videos to optical flow',
    packages=find_packages(),
    install_requires=['opencv-contrib-python >= 4.4.0.46',
                      'nutsflow >= 1.1.0',
                      'keyboard >= 0.13.5'],
)
