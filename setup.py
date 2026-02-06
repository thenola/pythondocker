"""Setup файл для PythonDocker."""

from setuptools import setup, find_packages
from pathlib import Path

# Читаем README для длинного описания
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# Читаем версию из __init__.py
version_file = Path(__file__).parent / "pythondocker" / "__init__.py"
version = "2.0.0"
if version_file.exists():
    for line in version_file.read_text(encoding='utf-8').splitlines():
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"').strip("'")
            break

setup(
    name='python-docker-package',
    version=version,
    description='Tool for running legacy Python scripts in isolated virtual environments',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='thenola',
    author_email='',  # Добавьте email если нужно
    url='https://github.com/thenola/pythondocker',
    project_urls={
        'Bug Reports': 'https://github.com/thenola/pythondocker/issues',
        'Source': 'https://github.com/thenola/pythondocker',
        'Documentation': 'https://github.com/thenola/pythondocker#readme',
    },
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'examples.*']),
    package_data={'pythondocker': ['MANUAL.md']},
    python_requires='>=3.7',
    install_requires=[
        # Стандартная библиотека; PyYAML опционален для .pythondocker.yml
    ],
    extras_require={
        'yaml': ['PyYAML>=5.1'],
    },
    entry_points={
        'console_scripts': [
            'pythondocker=pythondocker.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Environment :: Console',
    ],
    keywords='python version management virtual environment legacy python2 docker alternative',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
)
