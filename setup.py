"""KutinSynthesisPlugin setup file."""

from setuptools import setup, find_packages

setup(
    name="kutin-synthesis-plugin-for-qiskit",
    version="0.2.0",
    description="Synthesis for linear functions as a qiskit-terra plugin",
    license="MIT",
    author="Alexander Ivrii",
    author_email="alexi@il.ibm.com",
    packages=find_packages(),
    url="https://github.com/alexanderivrii/KutinSynthesisPlugin",
    keywords="linear synthesis",
    install_requires=["qiskit-terra>=0.22.*"],
    entry_points={
        "qiskit.synthesis": [
            "linear_function.kutin = qiskit_kutin_synthesis.kutin_synthesis_plugin:KutinSynthesisPlugin",
        ]
    },
    python_requires=">=3.7",
)
