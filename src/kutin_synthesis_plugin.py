from qiskit.circuit import QuantumCircuit
from qiskit.circuit.library import LinearFunction
from qiskit.transpiler.passes.synthesis.high_level_synthesis import HighLevelSynthesisPlugin

from binary_matrix_utils import calc_inverse_matrix
from kutin_synthesis import optimize_cx_circ_from_cx_matrix_NN_5_n_for_mix


"""Kutin's synthesis, implemented as a Qiskit Terra plugin."""

def synthesize_cx_circuit_lnn_depth(mat):
    num_qubits = len(mat)
    qc = optimize_cx_circ_from_cx_matrix_NN_5_n_for_mix(mat)
    qc1 = QuantumCircuit(num_qubits)
    for pair in qc[0]:
        qc1.cx(pair[0], pair[1])
    for pair in qc[1]:
        qc1.cx(pair[0], pair[1])
    mat1 = calc_inverse_matrix(LinearFunction(qc1).linear)
    assert ((mat == mat1).all())
    return qc1


class KutinSynthesisPlugin(HighLevelSynthesisPlugin):
    """Plugin."""

    def run(self, high_level_object, **options):
        """Run synthesis for the given LinearFunction."""

        qc = synthesize_cx_circuit_lnn_depth(high_level_object)
        return qc
