from setuptools import setup, find_packages

setup(
  name = 'recast-susyhiggs-demo',
  version = '0.0.1',
  description = 'recast-susyhiggs-demo',
  url = 'http://github.com/recast-hep/recast-susyhiggs-demo',
  author = 'Lukas Heinrich',
  author_email = 'lukas.heinrich@cern.ch',
  packages = find_packages(),
  include_package_data = True,
  scripts=[
    'scripts/rucio_wrapper.sh',
    'scripts/NtMaker_wrapper.sh',
    'scripts/SusySel_wrapper.sh',
    'scripts/setup_area_ntuplize.sh',
    'scripts/setup_area_analysis.sh',
      ],
  entry_points='''
        [console_scripts]
        susyplot=susyhiggs.plot:plot
    ''',  
  install_requires = [
    'Click',
    'Flask',
    'celery',
    'requests',
    'recast-api',
    'yoda',
    'socket.io-python-emitter',
    'redis'
  ],
  dependency_links = [    'https://github.com/ziyasal/socket.io-python-emitter/tarball/master#egg=socket.io-python-emitter-0.1.3',
    'https://github.com/recast-hep/recast-api/tarball/master#egg=recast-api-0.0.1'
  ]
)
