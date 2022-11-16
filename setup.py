from setuptools import setup, find_packages

with open("README.md", "r") as fh:
      long_description = fh.read()

setup(name='scoro',
      version='1.1.0',
      description='A file based index system, keeps a log of folder contents',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/bwinnett12/scoro',
      author='Bill Winnett',
      author_email='bwinnett12@gmail.com',
      license='MIT',
      py_modules=["scoro"],
      packages=find_packages('scoro'),
      package_dir={'': 'scoro'},
      zip_safe=False)