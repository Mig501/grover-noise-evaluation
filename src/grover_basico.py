"""Primera prueba del TFG: Grover de 2 qubits, ideal y con ruido.

Requisitos: Qiskit 2.6.0, Qiskit Aer 0.17.2 y Matplotlib.
Ejecucion desde la raiz del repositorio:
    python src/grover_basico.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

SHOTS = 1024
SEMILLA = 42
SOLUCION = "11"
ERROR_1_QUBIT = 0.01   # Parametro despolarizante para puertas H y X
ERROR_2_QUBITS = 0.05  # Parametro despolarizante para puertas CZ

# Crear carpeta de resultados
Path("outputs").mkdir(exist_ok=True)

def crear_circuito_grover():
    """Crea un circuito de Grover con una iteracion que marca |11>."""
    circuito = QuantumCircuit(2, 2)

    # 1. Superposicion uniforme: |00>, |01>, |10>, |11>
    circuito.h([0, 1])
    circuito.barrier()

    # 2. Oraculo de fase: marca |11> cambiando el signo de su amplitud
    circuito.cz(0, 1)
    circuito.barrier()

    # 3. Difusor (equivalente salvo fase global al de Grover habitual)
    circuito.h([0, 1])
    circuito.x([0, 1])
    circuito.cz(0, 1)
    circuito.x([0, 1])
    circuito.h([0, 1])
    circuito.barrier()

    # 4. Medicion
    circuito.measure([0, 1], [0, 1])
    return circuito


def crear_modelo_ruido():
    """Anade ruido despolarizante a las puertas que usa el circuito."""
    modelo = NoiseModel()
    modelo.add_all_qubit_quantum_error(
        depolarizing_error(ERROR_1_QUBIT, 1), ["h", "x"]
    )
    modelo.add_all_qubit_quantum_error(
        depolarizing_error(ERROR_2_QUBITS, 2), ["cz"]
    )
    return modelo


def ejecutar(simulador, circuito):
    # Aer admite directamente H, X y CZ; evitamos reescribir estas puertas
    # mediante transpilation para que el ruido se aplique a las esperadas.
    resultado = simulador.run(circuito, shots=SHOTS).result()
    return resultado.get_counts()


def main():
    circuito = crear_circuito_grover()
    print("Circuito de Grover (2 qubits, solucion 11):")
    fig = circuito.draw(
        output="mpl",
        style="iqp",
        scale=1.3,
        fold=-1
    )
    fig.savefig(
        "outputs/circuito_grover.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.show()
    print("Puertas:", dict(circuito.count_ops()))

    ideal = AerSimulator(method="statevector", seed_simulator=SEMILLA)
    ruido = AerSimulator(
        method="density_matrix",
        noise_model=crear_modelo_ruido(),
        seed_simulator=SEMILLA,
    )

    conteos_ideal = ejecutar(ideal, circuito)
    conteos_ruido = ejecutar(ruido, circuito)

    exito_ideal = conteos_ideal.get(SOLUCION, 0) / SHOTS
    exito_ruido = conteos_ruido.get(SOLUCION, 0) / SHOTS

    print("\nResultados ideales:", conteos_ideal)
    print("Resultados con ruido despolarizante:", conteos_ruido)
    print(f"\nProbabilidad de exito ideal: {exito_ideal:.2%}")
    print(f"Probabilidad de exito con ruido: {exito_ruido:.2%}")

    # Verificacion automatica de la prueba ideal de 2 qubits
    assert conteos_ideal.get(SOLUCION, 0) == SHOTS, (
        "La simulacion ideal no ha encontrado siempre el estado 11"
    )

    estados = ["00", "01", "10", "11"]
    prob_ideal = [conteos_ideal.get(e, 0) / SHOTS for e in estados]
    prob_ruido = [conteos_ruido.get(e, 0) / SHOTS for e in estados]

    posiciones = range(len(estados))
    anchura = 0.35
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar([i - anchura / 2 for i in posiciones], prob_ideal,
           width=anchura, label="Ideal")
    ax.bar([i + anchura / 2 for i in posiciones], prob_ruido,
           width=anchura, label="Con ruido")
    ax.set_xticks(list(posiciones), estados)
    ax.set_ylabel("Frecuencia relativa")
    ax.set_xlabel("Estado medido")
    ax.set_ylim(0, 1.05)
    ax.set_title("Grover (2 qubits): ideal frente a ruido despolarizante")
    ax.legend()
    fig.tight_layout()

    ruta_resultados = Path(__file__).resolve().parent.parent / "outputs"
    ruta_resultados.mkdir(parents=True, exist_ok=True)
    ruta_grafico = ruta_resultados / "grover_2q_ideal_vs_ruido.png"
    fig.savefig(ruta_grafico, dpi=180)
    plt.close(fig)
    print(f"Grafica guardada en: {ruta_grafico}")


if __name__ == "__main__":
    main()
