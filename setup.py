from setuptools import setup

with open("README.md", "r") as fh:
      long_description = fh.read()

setup(name='Scoro',
      version='0.3',
      description='A file based index system, keeps a log of folder contents',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='',
      author='Bill Winnett',
      author_email='bwinnett12@gmail.com',
      license='MIT',
      py_modules=["scoro"],
      packages={'': 'scoro'},
      zip_safe=False)