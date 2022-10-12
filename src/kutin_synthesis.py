import numpy as np
from copy import deepcopy
from binary_matrix_utils import calc_inverse_matrix


"""
Implements the synthesis algorithm from [1], Section 7.

References:
    [1] S. A. Kutin, D. P. Moulton, and L. M. Smithline, "Computation at a distance," 2007.
"""


def el_op(Matrix, ctrl, trgt, row_op=True):
    # Perform ROW or COL operation on Matrix
    if row_op:
        Matrix[trgt] = Matrix[trgt] ^ Matrix[ctrl]
    else:
        Matrix[:, ctrl] = Matrix[:, trgt] ^ Matrix[:, ctrl]


def el_op_all(Matrix, Matrix_inv, ctrl, trgt, row_op=True):
    # Perform ROW or COL operation on Matrix, and update the inverted Matrix
    el_op(Matrix, ctrl, trgt, row_op=row_op)
    el_op(Matrix_inv, ctrl, trgt, row_op=not row_op)


def append_gate_lite(cx_instructions, Matrix, a, b):
    # Add a cx gate to instructions and update matrices
    cx_instructions.append((a, b))
    el_op(Matrix, a, b)


def get_last_index_1(n, Matrix, indx):
    # Return the column index of the last "1" in a chosen row
    for j in reversed(range(n)):
        if Matrix[indx, j]:
            return j


def get_L_transformation(n, Matrix, Matrix_inv):
    Matrix = deepcopy(Matrix)
    Matrix_t = deepcopy(Matrix)
    Matrix_inv_t = deepcopy(Matrix_inv)

    cx_instructions_rows = []

    # Get instructions for LU decomposition
    # Use U instructions, which contains only gates of the form cx(a,b) a>b
    # to transform the matrix to a permutated lower-triangular matrix. Original Matrix unchanged
    for i in reversed(range(0, n)):
        found_first = False
        # Find last "1" in row i, use COL operations to the left in order to zero out all other "1"s in that row.
        for j in reversed(range(0, n)):
            if Matrix[i, j]:
                if not found_first:
                    found_first = True
                    first_j = j
                else:
                    # cx_instructions_cols (L instructions) not needed
                    el_op(Matrix, j, first_j, row_op=False)
        # Use row operations directed upwards to zero out all "1"s above the remaining "1" in row i
        for k in reversed(range(0, i)):
            if Matrix[k, first_j]:
                append_gate_lite(cx_instructions_rows, Matrix, i, k)

    # Apply only U instructions to get permutated L
    for inst in cx_instructions_rows:
        el_op_all(Matrix_t, Matrix_inv_t, inst[0], inst[1])
    return Matrix_t, Matrix_inv_t


def get_label_arr(n, Matrix_t):
    # For each row in Matrix_t, save the column index of the last "1"
    label_arr = []
    for i in range(n):
        j = 0
        while not Matrix_t[i, n - 1 - j]:
            j += 1
        label_arr.append(j)
    return label_arr


def in_W(label_arr_t, Matrix_inv_t, row, k):
    # Check if "row" is a linear combination of all rows in Matrix_inv_t not including the row labeled by k
    indx_k = label_arr_t[k]
    W_needed = np.zeros(len(row), dtype=bool)
    # Find the linear combination of Matrix_t rows which produces "row"
    for l in range(len(row)):
        if row[l]:
            # Matrix_inv_t can be thought of as a set of instructions. Row l in Matrix_inv_t
            # indicates which rows from Matrix_t are necessery to produce the elementary vector e_l
            W_needed = W_needed ^ Matrix_inv_t[l]
    # If the linear combination requires the row labeled by k
    if W_needed[indx_k]:
        return False
    return True


def get_label_arr_t(n, label_arr):
    # label_arr_t = label_arr^(-1)
    label_arr_t = [None] * n
    for i in range(n):
        label_arr_t[label_arr[i]] = i
    return label_arr_t


def matrix_to_north_west(n, cx_instructions_rows, Matrix, Matrix_inv, is_rows=True):
    # Transform an arbitrary invertable matrix to a north-west triangular matrix as per Proposition 7.3. [1]

    # The rows of Matrix_t hold all w_j vectors [1]. Matrix_inv_t is the inverted matrix of Matrix_t
    Matrix_t, Matrix_inv_t = get_L_transformation(n, Matrix, Matrix_inv)

    # Get all pi(i) labels
    label_arr = get_label_arr(n, Matrix_t)

    # Save the original labels, exchange index <-> value
    label_arr_t = get_label_arr_t(n, label_arr)

    first_qubit = 0
    empty_layers = 0
    done = False
    while not done:
        # At each iteration the values of i switch between even and odd
        i = first_qubit
        at_least_one_needed = False
        while i + 1 < n:
            # "If j < k, we do nothing" [1]
            # "If j > k, we swap the two labels, and we also perform a box" [1]
            if label_arr[i] > label_arr[i + 1]:
                at_least_one_needed = True
                # "Let W be the span of all w_l for l!=k" [1]
                # " We can perform a box on <i> and <i + 1> that writes a vector in W to wire <i + 1>." [1]
                if in_W(label_arr_t, Matrix_inv_t, Matrix[i + 1], label_arr[i + 1]):

                    None

                elif in_W(label_arr_t, Matrix_inv_t, Matrix[i + 1] ^ Matrix[i], label_arr[i + 1]):

                    append_gate_lite(cx_instructions_rows, Matrix, i, i + 1)

                elif in_W(label_arr_t, Matrix_inv_t, Matrix[i], label_arr[i + 1]):

                    append_gate_lite(cx_instructions_rows, Matrix, i + 1, i)

                    append_gate_lite(cx_instructions_rows, Matrix, i, i + 1)

                label_arr[i], label_arr[i + 1] = label_arr[i + 1], label_arr[i]

            i = i + 2

        if not at_least_one_needed:
            empty_layers += 1
            if empty_layers > 1:  # if nothing happened twice in a row, then finished.
                done = True
        else:
            empty_layers = 0

        first_qubit = int(not first_qubit)


def north_west_to_identity(n, cx_instructions_rows, Matrix):
    # Transform a north-west triangular matrix to identity in depth 3n as per Proposition 7.4. [1]

    # At start the labels are in reversed order
    label_arr = list(reversed(range(n)))
    first_qubit = 0
    empty_layers = 0
    done = False
    while not done:
        i = first_qubit
        at_least_one_needed = False
        while i + 1 < n:
            # Exchange the labels if needed
            if label_arr[i] > label_arr[i + 1]:
                at_least_one_needed = True

                # If row i has "1" in colum i+1, swap and remove the "1" (in depth 2)
                # otherwise, only swap (in depth 3)
                if not Matrix[i, label_arr[i + 1]]:
                    # Adding this turns the operation to a SWAP
                    append_gate_lite(cx_instructions_rows, Matrix, i + 1, i)

                append_gate_lite(cx_instructions_rows, Matrix, i, i + 1)

                append_gate_lite(cx_instructions_rows, Matrix, i + 1, i)

                label_arr[i], label_arr[i + 1] = label_arr[i + 1], label_arr[i]

            i = i + 2

        if not at_least_one_needed:
            empty_layers += 1
            if empty_layers > 1:  # if nothing happened twice in a row, then finished.
                done = True
        else:
            empty_layers = 0

        first_qubit = int(not first_qubit)


def optimize_cx_circ_NN_5_for_mix(Matrix, Matrix_inv):
    # Optimize CX circuit in depth <= 5n for LNN connectivity.
    n = len(Matrix)
    cx_instructions_rows_m2nw = []
    cx_instructions_rows_nw2id = []
    # Transform an arbitrary invertible matrix to a north-west triangular matrix as per Proposition 7.3. [1]
    matrix_to_north_west(n, cx_instructions_rows_m2nw, Matrix, Matrix_inv)

    # Transform a north-west triangular matrix to identity in depth 3n as per Proposition 7.4. [1]
    north_west_to_identity(n, cx_instructions_rows_nw2id, Matrix)

    return cx_instructions_rows_m2nw, cx_instructions_rows_nw2id


def optimize_cx_circ_from_cx_matrix_NN_5_n_for_mix(Matrix):
    # Get instructions to implement CX in depth 5n.
    # The algorithm [1] has two steps - a) transform the original Matrix
    # to a North-West matrix (m2nw), b) transform North-west to Identity (nw2id).
    Matrix_inv = calc_inverse_matrix(Matrix)
    return optimize_cx_circ_NN_5_for_mix(deepcopy(Matrix), deepcopy(Matrix_inv))

