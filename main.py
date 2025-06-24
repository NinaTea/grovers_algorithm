
from qiskit.quantum_info import Statevector, Operator
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import MCMTGate, CZGate
import matplotlib.pyplot as plt
from numpy import sqrt, floor, pi
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram

'''
TODO: Add brief explanation of Grover's algorithm
'''


def mcz4() -> QuantumCircuit:
    """
    Multicontrolled Z gate with 3 control qubits and 1 target qubit.
    """
    return MCMTGate(gate=CZGate(), num_ctrl_qubits=3, num_target_qubits=1, label="MCZ4")


def oracle(n_qubits: int) -> QuantumCircuit:
    """
    n_qubits: circuit size

    Marked stats:

    O|y> =  |y > iff y != |1110> or |1101>
    O|y> = -|y > iff y == |1110> or |1101>:

    """
    circuito = QuantumCircuit(n_qubits)

    # |1110>
    circuito.x(0)  # |1110> -> |1111>
    cccz = mcz4()
    circuito.compose(cccz, qubits=[0, 1, 2, 3], inplace=True)
    circuito.x(0)

    # |1101>
    circuito.x(1)  # |1101> -> |1111>
    cccz = mcz4()
    circuito.compose(cccz, qubits=[0, 1, 2, 3], inplace=True)
    circuito.x(1)  # restaurar

    return circuito


def diffuser(n_qubits: int) -> QuantumCircuit:
    """
    n_qubits: circuit size

    D = 2 |I0><I0| - Id
    To apply a reflextion about the state |I0> we need to apply to all qubits:

    H 
    X
    MCZ
    X
    H 

    """
    circuito = QuantumCircuit(n_qubits)
    qubits = range(n_qubits)
    circuito.h(qubits)
    circuito.x(qubits)
    cccz = mcz4()
    circuito.compose(cccz, qubits=[0, 1, 2, 3], inplace=True)
    circuito.x(qubits)
    circuito.h(qubits)

    return circuito


# Qubits
n = 4
qubits = range(n)
circuito = QuantumCircuit(n, n)

circuito.h(qubits)
circuito.barrier()

# Optimum number of iterations
iterations = int(floor((pi / 4) * sqrt(2 ** n))-1)

# Oracle and Diffuser
ora = oracle(n)
dif = diffuser(n)

for _ in range(iterations):
    # Oracle
    circuito = circuito.compose(ora)
    circuito.barrier()

    # Diffuser
    circuito = circuito.compose(dif)
    circuito.barrier()

# Measure
circuito.measure(qubits, qubits)
circuito.draw("mpl")

# Simulation
simulador = Aer.get_backend("aer_simulator")
job = simulador.run(transpile(circuito, simulador), shots=1024)
resultados = job.result()
counts = resultados.get_counts(circuito)
plot_histogram(counts)
