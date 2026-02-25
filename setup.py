from setuptools import setup, find_packages

setup(
    name="robot_ai_experiments",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pygame',
        'matplotlib',
        'gymnasium',
    ],
    author="Your Name",
    description="Interactive AI and Robot Path Planning Visualizations",
    license="Apache-2.0",
)
