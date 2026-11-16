from importlib.metadata import version

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError

# Mostrar las versiones instaladas
print("Qiskit:", version("qiskit"))
print("Qiskit Aer:", version("qiskit-aer"))

# Crear un circuito de 2 qubits
circuito = QuantumCircuit(2)

# Preparar un estado de Bell
circuito.h(0)
circuito.cx(0, 1)
circuito.measure_all()

print("\nCircuito:")
print(circuito.draw(output="text"))

# Simulacion ideal
simulador_ideal = AerSimulator(seed_simulator=42)

circuito_ideal = transpile(circuito, simulador_ideal)

resultado_ideal = simulador_ideal.run(
    circuito_ideal,
    shots=1024
).result()

print("\nResultados ideales:")
print(resultado_ideal.get_counts())

# Modelo de ruido: 5% de error de lectura
modelo_ruido = NoiseModel()

error_lectura = ReadoutError([
    [0.95, 0.05],
    [0.05, 0.95]
])

modelo_ruido.add_all_qubit_readout_error(error_lectura)

simulador_ruido = AerSimulator(
    noise_model=modelo_ruido,
    seed_simulator=42
)

circuito_ruido = transpile(circuito, simulador_ruido)

resultado_ruido = simulador_ruido.run(
    circuito_ruido,
    shots=1024
).result()

print("\nResultados con ruido:")
print(resultado_ruido.get_counts())
