from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='easy_async_tg_notify',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'httpx',
        'python-decouple',
        'aiofiles'
    ],
    author='Alexey Yakovenko',
    author_email='mr.mnogo@gmail.com',
    description='Asynchronous Telegram notification sender',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Yakvenalex/easy_async_tg_notify',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
