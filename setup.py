"""KutinSynthesisPlugin setup file."""

from setuptools import setup, find_packages

setup(
    name="kutin-synthesis-plugin-for-qiskit",
    version="0.1.1",
    description="Synthesis for linear functions as a qiskit-terra plugin",
    license="MIT",
    author="Alexander Ivrii",
    author_email="alexi@il.ibm.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/alexanderivrii/KutinSynthesisPlugin",
    keywords="linear synthesis",
    install_requires=[
      ],

    entry_points={
        "qiskit.synthesis": [
            "linear_function.kutin = kutin_synthesis_plugin:KutinSynthesisPlugin",
        ]
    },
)
