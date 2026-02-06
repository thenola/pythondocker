"""Setup файл для PythonDocker."""

from setuptools import setup, find_packages
from pathlib import Path

# Читаем README для длинного описания
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name='pythondocker',
    version='1.0.0',
    description='Инструмент для запуска старых Python скриптов в изолированных виртуальных окружениях',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='thenola',
    url='https://github.com/thenola/pythondocker',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        # Нет внешних зависимостей, используем только стандартную библиотеку
    ],
    entry_points={
        'console_scripts': [
            'pythondocker=pythondocker.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
