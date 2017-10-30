# Setup template originally taken from learnpythonthehardway.org/book/ex46.html

def main():
	try:
		from setuptools import setup
	except ImportError:
		from distutils.core import setup

	config = {
		'description': 'Call functions with arguments stored in JSON files',
		'author': 'Matt Christie',
		'download_url': 'not online',
		'author_email': 'christiemj09@gmail.com',
		'version': '0.1',
		# 'install_requires': [],
		# 'packages': [],
		# 'scripts': [],
		'name': 'config'
	}

	setup(**config)	

if __name__ == '__main__':
	main()
