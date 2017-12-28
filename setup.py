from setuptools import setup, find_packages

setup(name = 'gratrain',
      version = '0.0',
      description = 'Graph Train',
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
