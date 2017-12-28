from setuptools import setup, find_packages

setup(name = 'gravio',
      version = '0.0',
      description = 'Gravio is graph generation and visualization with an object oriented data structure',
      author = 'Brett Viren',
      author_email = 'brett.viren@gmail.com',
      license = 'GPLv2',
      url = 'http://github.com/brettviren/gratrain',
      packages = find_packages(),
      install_requires=[l.strip() for l in open("requirements.txt").readlines()],
      dependency_links = [
      ],
      entry_points = {
          'console_scripts': [
          ]
      }
)
