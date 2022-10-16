# KutinSynthesisPlugin

Synthesis algorithm from [1] for linear functions, implemented as a Qiskit plugin.

---

This package illustrates how to write high level synthesis plugins for Qiskit (see Qiskit documentation at 
https://qiskit.org/documentation/apidoc/transpiler_synthesis_plugins.html).

Here are a few important points:

First, there is a class `KutinSynthesisPlugin` that inherits from `HighLevelSynthesisPlugin`
(see https://qiskit.org/documentation/stubs/qiskit.transpiler.passes.synthesis.plugin.HighLevelSynthesisPlugin.html).
This class has method `run` that accepts an object of type `LinearFunction`, essentially containing a NxN binary invertible 
matrix (see https://qiskit.org/documentation/stubs/qiskit.circuit.library.LinearFunction.html), and returns a 
`QuantumCircuit` (https://qiskit.org/documentation/stubs/qiskit.circuit.QuantumCircuit.html) that realizes this matrix. 
The method `run` is also allowed to return `None` is for some reason synthesis is not possible.

The file `setup.py` has the following "entry_points":
``` 
entry_points={
    "qiskit.synthesis": [
        "linear_function.kutin = qiskit_kutin_synthesis.kutin_synthesis_plugin:KutinSynthesisPlugin",
    ]
}
```
Importantly, "entry_points" include "qiskit.synthesis", and within that 
defines a synthesis method "kutin" for objects with name "linear_function", 
with the implementation in our "KutinSynthesisPlugin"
discussed before.

---

To use this package in some other code, all that's needed to be done is to
"pip install kutin-synthesis-plugin-for-qiskit", and then "kutin"  
will become available as a high-level synthesis method for objects with name "linear_functions".
Here is an explicit example how this can be done: 

```
from qiskit.circuit import QuantumCircuit
from qiskit.circuit.library import LinearFunction
from qiskit.transpiler.passes.synthesis.high_level_synthesis import HLSConfig, HighLevelSynthesis
from qiskit.transpiler import PassManager
from qiskit.compiler import transpile
from qiskit.providers.fake_provider import FakeHanoi

if __name__ == "__main__":
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

    # This only runs the high-level-synthesis pass
    qct = PassManager(HighLevelSynthesis(hls_config=hls_config)).run(qc)
    print(qct)
    
    # This runs the full Qiskit transpilation flow, including the high-level-synthesis pass
    # that uses the specified method
    qc2 = transpile(qc, hls_config=hls_config, optimization_level=3, backend=FakeHanoi())
    print(qc2)
```

---

The code was written by Ben Zindorf, Shelly Garion, and Alexander Ivrii.

---

References:

[1]. S. A. Kutin, D. P. Moulton, and L. M. Smithline, "Computation at a distance," 2007.

