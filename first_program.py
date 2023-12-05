from qiskit import *
circut = QuantumCircuit(2,2)
circut.h(0)
circut.cx(0,1)
circut.measure([0,1],[0,1])
print(circut.draw())