import multiprocessing

from setuptools import setup


with open('README.rst') as readme:
    long_description = readme.read()


setup(name='buckeye',
      version='1.3',
      description='Classes and iterators for the Buckeye Corpus',
      long_description=long_description,
      url='https://github.com/scjs/buckeye/',
      author='Scott Seyfarth',
      license='MIT',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Science/Research',
          'Topic :: Multimedia :: Sound/Audio :: Analysis',
          'Topic :: Multimedia :: Sound/Audio :: Speech',
          'Topic :: Scientific/Engineering',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6'],
      keywords='speech linguistics language conversation corpus',
      packages=['buckeye'],
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=['nose', 'mock']
     )
