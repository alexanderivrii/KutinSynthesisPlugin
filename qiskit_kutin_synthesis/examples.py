from .binary_matrix_utils import  random_invertible_binary_matrix
from .kutin_synthesis_plugin import KutinSynthesisPlugin

import stevedore

from qiskit.circuit import QuantumCircuit
from qiskit.circuit.library import LinearFunction
from qiskit.transpiler.passes.synthesis.high_level_synthesis import HLSConfig, HighLevelSynthesis
from qiskit.transpiler import PassManager


def print_available_plugins():
    plugins = stevedore.ExtensionManager(
        "qiskit.synthesis", invoke_on_load=True, propagate_map_exceptions=True
    )
    print(f"{plugins.names() = }")


def synthesize_some_linear_function():
    mat = random_invertible_binary_matrix(6, seed=0)
    print(mat)

    lf = LinearFunction(mat)

    qc = KutinSynthesisPlugin().run(lf)

    print(f"qc has gate_count = {qc.size()}, depth = {qc.depth()}")
    # print(qc)




def test_qiskit_code():
    qc1 = QuantumCircuit(3)
    qc1.swap(0, 2)
    qc1.cx(0, 1)
    qc1.swap(1, 2)
    lf1 = LinearFunction(qc1)

    qc2 = QuantumCircuit(2)
    qc2.swap(0, 1)
    qc2.cx(1, 0)
    qc2.swap(0, 1)
    lf2 = LinearFunction(qc2)

    qc = QuantumCircuit(4)
    qc.append(lf1, [0, 1, 2])
    qc.h(2)
    qc.append(lf2, [2, 3])
    print(qc)

    hls_config = HLSConfig(linear_function=[("kutin", {})])

    qct = PassManager(HighLevelSynthesis(hls_config=hls_config)).run(qc)
    print(qct)


if __name__ == "__main__":
    print_available_plugins()
    synthesize_some_linear_function()
    test_qiskit_code()
