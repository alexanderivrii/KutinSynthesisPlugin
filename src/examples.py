from binary_matrix_utils import  random_invertible_binary_matrix
from kutin_synthesis_plugin import KutinSynthesisLinearFunction


if __name__ == "__main__":
    mat = random_invertible_binary_matrix(6, seed=0)
    print(mat)

    qc = KutinSynthesisPlugin().run(mat)

    print(f"qc has gate_count = {qc.size()}, depth = {qc.depth()}")
    # print(qc)
