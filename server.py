import numpy as np
from flask import Flask, render_template, request, jsonify
import json

# importing matplotlib modules
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

import base64


#quantum hardware
from qiskit import(
    execute,
    QuantumCircuit,
    IBMQ)
from qiskit.tools.monitor import job_monitor

#simulator
from qiskit import QuantumCircuit
from qiskit import Aer, transpile
from qiskit.tools.visualization import plot_histogram, plot_state_city
import qiskit.quantum_info as qi
from qiskit.compiler import assemble

def quantumBackend(circuit, token):
    IBMQ.save_account(token, overwrite=True)
    IBMQ.load_account()
    provider = IBMQ.get_provider('ibm-q')
    qcomp = provider.get_backend('ibmq_lima') # 5 qubits, 8 quantum volume
    job = execute(circuit, backend=qcomp, shots = 20)
    job_monitor(job)
    return job.result()

def simulationBackend(circuit, token):
    simulator = Aer.get_backend('qasm_simulator')
    circuit = transpile(circuit, simulator)
    my_qobj = assemble(circuit) 
    return simulator.run(my_qobj).result()

optionsBackend =  {
    'simulation': simulationBackend,
    'quantum': quantumBackend
}

def deutschBackend(input):
    f = input['f']
    #quantum circuit
    #before oracle
    circuit = QuantumCircuit(2, 2)
    circuit.x(1)
    circuit.h(0)
    circuit.h(1)

    #oracle
    #if f[0] and f[1]:
    #    do nothing

    if f[0] and f[1]:
        circuit.x(1)

    if f[0] and (not f[1]):
        circuit.cx(0,1)
    
    if (not f[0]) and f[1]:
        circuit.x(1)
        circuit.cx(0,1)

    #after oracle  
    circuit.h(0)
    circuit.measure([0, 1], [0, 1])

    #measurement
    result = optionsBackend[input['backend']](circuit, input['token'])

    # Returns counts
    counts = result.get_counts(circuit)
    keys = list(counts)
    max_val = 0
    max_index = 0

    
    # after measurement
    for j in range(len(keys)):
        if counts[ keys[j] ] > max_val:
            max_val = counts[ keys[j] ]
            max_index = j

    circuit.draw( output='mpl', filename = 'circ.png' )

    return json.dumps({'const': (keys[max_index][1] == '0'), 'circ': str(base64.b64encode(open("circ.png", "rb").read())) })



# client-server
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

options =  {
    'Deutsch': deutschBackend
}

@app.route('/api', methods=['POST'])
def main():
    return options[request.get_json()['selection']](request.get_json()['input'])

if __name__ == '__main__':
    app.run()
