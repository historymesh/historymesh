try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages
import linkfinder

setup(name="linkfinder",
      version=linkfinder.__version__,
      packages=find_packages(),
      include_package_data=True,
      author='Richard Boulton',
      author_email='richard@tartarus.org',
      description='Get the links in and out of a wikipedia page',
      long_description=__doc__,
      zip_safe=False,
      platforms='any',
      license='MIT',
      #url='https://github.com/rboulton/linkfinder',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Operating System :: Unix',
      ],
      install_requires=[
        'flask',
        'restpose>=0.7.2',
      ],
      setup_requires=[
        'nose>=0.11',
      ],
      tests_require=[
        'coverage',
      ],
)
