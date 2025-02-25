from setuptools import setup, find_packages

setup(
    name="simple_metagpt",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # 在这里添加依赖包，例如 'requests', 'numpy', 等等
        'python-dotenv',
        'openai',
        'numpy',


    ],
    entry_points={
        'console_scripts': [
            # 在这里添加命令行脚本，例如 'simplemetagpt=simplemetagpt:main'
        ],
    },
    author="OopsYouDiedE",
    author_email="your.email@example.com",
    description="A simple MetaGPT project",
    long_description=open('README.md', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    url="https://github.com/yourusername/SimpleMetaGPT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
