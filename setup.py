from setuptools import setup, find_packages

setup(
    name='inventory-management',
    version='1.0.0',
    description='CLI-based Inventory Management System with MySQL',
    author='vinisha231',
    author_email='viba2022@gmail.com',
    python_requires='>=3.8',
    install_requires=[
        'mysql-connector-python>=8.3.0',
        'python-dotenv>=1.0.0',
        'tabulate>=0.9.0',
        'colorama>=0.4.6',
    ],
    extras_require={
        'dev': ['pytest>=7.0', 'pytest-cov>=4.0']
    },
    entry_points={
        'console_scripts': [
            'inventory=inventory:main',
        ],
    },
)
