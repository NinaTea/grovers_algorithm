
from qiskit.quantum_info import Statevector, Operator
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import MCMTGate, CZGate
import matplotlib.pyplot as plt
from numpy import sqrt, floor, pi
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram

'''
Necesitamos el oraculo f que nos va cambiar el signo del estado
si es el que estamos buscando o lo va a dejar igual si no es el que queremos.

Después necesitamos un amplificador que nos va a ir haciendo las reflexiones.

Pasos

Poner todos los qubits en superposición
Aplicar el oráculo
Aplicar el amplificador
Repetir

n = 3 qubits. N = 2^3 = 8 estados en la base computacional.

|000 >, |001 >, |010 >, |011 >,
|100 >, |101 >, |110 >, |111 >

Queremos encontrar x = 110.
'''


def mcz4() -> QuantumCircuit:
    """
    Compuerta multicontrolada Z de 4 qubits
    """
    return MCMTGate(gate=CZGate(), num_ctrl_qubits=3, num_target_qubits=1, label="MCZ4")


def oraculo(n_qubits: int) -> QuantumCircuit:
    """
    n_qubits: int tamaño del circuito

    Acá definimos el oraculo.

    O|y> =  |y > si y != (|1110> o |1101>)
    O|y> = -|y > si y == |1110> o |1101>:

    """
    circuito = QuantumCircuit(n_qubits)

    # Marcamos |1110>
    # Cambiamos el estado del qubit 0 a |1>
    # Si encontramos que todos los qubits son |11>, entonces cambiamos el signo a q2
    # volvemos el qubit 0 a su estado original
    circuito.x(0)
    cccz = mcz4()
    circuito.compose(cccz, qubits=[0, 1, 2, 3], inplace=True)
    circuito.x(0)

    # Marcamos |1101>
    # marca |1111> (que era |1101> original)
    circuito.x(1)  # |1101> -> |1111>
    cccz = mcz4()
    circuito.compose(cccz, qubits=[0, 1, 2, 3], inplace=True)
    circuito.x(1)  # restaurar

    return circuito


def difusor(n_qubits: int) -> QuantumCircuit:
    """
    n_qubits: int tamaño del circuito
    Definimos el difusor

    D = 2 |I0><I0| - Id

    Para lograr una reflexión respecto al estado |I0> tenemos que hacer
    H a todo
    X a todo
    MCZ: z multicontrolada
    X a todo
    H a todo

    """
    circuito = QuantumCircuit(n_qubits)
    qubits = range(n_qubits)
    # Aplicamos Hadamard a todos los qubits
    # Aplicamos NOT a todos los qubits
    # Aplicamos la compuerta multicontrolada Z igual que en el oráculo
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

estado_0 = Statevector(circuito)
# print(f"Estado inicial: {estado_0}")
# Inicializar el estado |I0>
# Esto es, aplicar la compuerta Hadamard a todos los qubits
circuito.h(qubits)
circuito.barrier()


# Para saber cuántas iteraciones necesitamos, usamos la fórmula vista
# en clase y nos queda que iteraciones ~ (pi/4) * sqrt(N) = (pi/4) * sqrt(8) = 2.22
iteraciones = int(floor((pi / 4) * sqrt(2 ** n))-1)
print('Las iteraciones son:', iteraciones)

# 'instanciamos' el oráculo y el difusor
ora = oraculo(n)
dif = difusor(n)

k = 10


for i in range(k):
    # Aplicamos el oráculo
    circuito = circuito.compose(ora)
    circuito.barrier()
    # estado = Statevector(circuito)
    # print(f"Iteración {i+1}: Estado actual: {estado}")

    # Aplicamos el difusor
    circuito = circuito.compose(dif)
    circuito.barrier()
    # estado = Statevector(circuito)
    # print(f"Iteración {i+1}: Estado actual: {estado}")
    # matriz = Operator(circuito)


# Medimos los qubits
circuito.measure(qubits, qubits)
circuito.draw("mpl")
plt.savefig(f'circuito_grover_n4_{k}.pdf')


# Simulamos el circuito
simulador = Aer.get_backend("aer_simulator")
# los shots son cuantas veces vamos a medir el circuito
job = simulador.run(transpile(circuito, simulador), shots=1024)
resultados = job.result()
counts = resultados.get_counts(circuito)
plot_histogram(counts)
plt.savefig(f"k_{k}_iteraciones.pdf")


# Agrego un qubit mas
# Miramos como cambia iteracion a iteracion el histograma

# Curiosidad: Implementacion diccionario
