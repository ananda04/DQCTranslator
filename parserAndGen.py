### DSL and translation for AWG control
### Designed by Arnav Nanda, Duke University Quantum Center, 2026-March
### This module provides functionality to parse a custom DSL for AWG waveform generation and translate it into SCPI commands. It also includes utilities for generating arbitrary waveforms, normalizing them, and saving/loading waveform data.
### The DSL supports various waveform types (sine, triangle, square, noise, exponential, decay, sawtooth, ramp, pulse) with parameters for frequency, amplitude, offset, and phase. The generated SCPI commands can be sent to an AWG instrument for waveform generation.
### Example usage:
### 1. Compile a DSL file into SCPI commands:
###    scpi_commands = compileFile("waveforms.dsl")
### 2. Run the compiled SCPI commands on an instrument:
###    run_scpi_file("waveforms.dsl.cache.json", instrument)
### DSL command format: <WAVEFORM_TYPE>-<FREQUENCY>-<AMPLITUDE>-<OFFSET>[-<PHASE>]
### For arbitrary waveforms, the command format is: <ARB_WAVEFORM_TYPE>-<FREQUENCY>-<AMPLITUDE>-<OFFSET>[-<PHASE>]
### To add/mult/div/subtract two arbitrary waveforms: <WAVEFORM1> <OPERATION> <WAVEFORM2>
### DSL changes to add +, -, *, / operations for arbitrary waveforms:
### Example: ARB-SINE-1kHz-1V-0V#+#ARB-TRI-500Hz-0.5V-0V






from dataclasses import dataclass
import json
import numpy as np 

WAVEFORM_MAP = {
    "ARB": "ARB",
    "SINE": "SIN",
    "TRI": "TRI",
    "SQUARE": "SQU"
}

@dataclass
class WaveformCommand:
    type: str
    frequency: float
    amplitude: float
    offset: float
    phase: float = 0.0

def save_cache(scpi_lines, source_file):
    cache = {
        "source": source_file,
        "commands": scpi_lines
    }

    with open(source_file + ".cache.json", "w") as f:
        json.dump(cache, f, indent=2)

def run_scpi_file(filename, instrument):
    with open(filename, "r") as f:
        cache = json.load(f)        
    for line in cache["commands"]:
        instrument.write(line.strip())

def compileFile(filename: str, cache=True):
    compile_scpi = []

    with open(filename, "r") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            try:
                cmd = parse_command(line)
                scpi_lines = genSCPI(cmd)
                compile_scpi.extend(scpi_lines)
            except ValueError as e:
                print(f"[Line {line_num}] Skipping: {line} → {e}")

    if cache:
        save_cache(compile_scpi, filename)

    return compile_scpi



def parse_command(cmd: str) -> WaveformCommand:
    """    
    :param cmd: awg single instruction 
    :type cmd: str
    :return: relevant wave data
    :rtype: WaveformCommand
    """
    parts = cmd.split("-")

    if len(parts) < 4:
        raise ValueError("Invalid command format.")

    wf = parts[0].upper()

    if wf not in WAVEFORM_MAP:
        raise ValueError(f"Unsupported waveform type: {wf}")

    try:
        freq = float(parts[1])
        amp = float(parts[2])
        offset = float(parts[3])
        phase = float(parts[4]) if len(parts) > 4 else 0.0
    except ValueError:
        raise ValueError("Numeric fields must be valid numbers.")

    if freq < 0:
        raise ValueError("Frequency must be non-negative.")

    if amp < 0:
        raise ValueError("Amplitude must be non-negative.")

    if not -360 <= phase <= 360:
        raise ValueError("Phase must be between -360 and 360.")
    if parts[0].startswith("ARB"):
        wf = parts[0][4:].upper()  # Extract the base waveform type for ARB commands
        if wf not in WAVEFORM_MAP:
            raise ValueError(f"Unsupported ARB waveform type: {wf}")
    
    return WaveformCommand(wf, freq, amp, offset, phase)

def generate_ARBMEM(cmd: str, sample_rate=1e9, duration=1e-3):
    """    
    :param cmd: parsed WaveformCommand
    :type cmd: WaveformCommand
    :param sample_rate: Sample rate for the arbitrary waveform (default: 1 GS/s)
    :type sample_rate: float
    :param duration: Duration of the waveform in seconds (default: 1 ms)
    :type duration: float

    Returns:
        np.ndarray: Array of samples representing the arbitrary waveform.
    """
    # parse the commnad to get the waveform parameters
    cmd = parse_command(cmd)
    # we need to check for the ARB( prefix before generating the waveform --> this allows us to determine if we need to generate an arbitrary wave form / or do some operation on multiple waveforms
    
    if cmd.type == "SIN":
        ARB-SINE =np.array(cmd.amplitude * np.sin(2 * np.pi * cmd.frequency * t + np.radians(cmd.phase)) + cmd.offset)
        return ARB-SINE
    elif cmd.type == "TRI":
        ARB-TRI =np.array(cmd.amplitude * (2 * np.abs(2 * (t * cmd.frequency - np.floor(t * cmd.frequency + 0.5))) - 1) + cmd.offset)
        return ARB-TRI
    elif cmd.type == "SQU":
        ARB-SQUARE =np.array(cmd.amplitude * np.sign(np.sin(2 * np.pi * cmd.frequency * t + np.radians(cmd.phase))) + cmd.offset)
        return ARB-SQUARE
    elif cmd.type == "NOI":
        ARB-NOISE =np.array(cmd.amplitude * np.random.normal(0, 1, len(t)) + cmd.offset)
        return ARB-NOISE
    elif cmd.type == "EXP":
        ARB-EXP =np.array(cmd.amplitude * (1 - np.exp(-t * cmd.frequency)) + cmd.offset)
        return ARB-EXP
    elif cmd.type == "DEC":
        ARB-DECAY =np.array(cmd.amplitude * np.exp(-t * cmd.frequency) + cmd.offset)
        return ARB-DECAY
    elif cmd.type == "SAW":
        ARB-SAW =np.array(cmd.amplitude * (t * cmd.frequency - np.floor(t * cmd.frequency)) + cmd.offset)
        return ARB-SAW
    elif cmd.type == "RAM":
        ARB-RAMP =np.array(cmd.amplitude * (t * cmd.frequency - np.floor(t * cmd.frequency)) + cmd.offset)
        return ARB-RAMP
    elif cmd.type == "PUL":
        ARB-PULSE =np.array(cmd.amplitude * (np.where((t % (1/cmd.frequency)) < (0.5/cmd.frequency), 1, 0)) + cmd.offset)
        return ARB-PULSE
    else:
        raise ValueError(f"Unsupported waveform type: {cmd.type}")
    return None
   

def normalize_waveform(waveform):
    """    
    :param waveform: Array of samples representing the arbitrary waveform.
    :type waveform: np.ndarray

    Returns:
        np.ndarray: Normalized waveform with values scaled to the range [-1, 1].
    """
    max_val = np.max(np.abs(waveform))
    if max_val == 0:
        return waveform
    return waveform / max_val
def concatenate_waveforms(waveforms):
    """    
    :param waveforms: List of arrays representing individual waveforms.
    :type waveforms: list[np.ndarray]

    Returns:
        np.ndarray: Concatenated waveform array.
    """
    return np.concatenate(waveforms)

def waveform_arithemtic(cmd: str, waveforms: dict):
   # This will parse the command and generate the necessary waveforms if they are not already generated
   # need to run delimiters to get the two or more waveforms and the operation
    parts = cmd.split()
    if len(parts) < 2:
        raise ValueError("Invalid command format for waveform arithmetic.")
    generate_ARBMEM(cmd)  
    # need to add support for order of operations and parentheses in the future
    # for now we will just support two waveforms and one operation
    wf1_name = parts[0]
    operation = parts[1]
    wf2_name = parts[2] 

    if operation == "+":
        final = wf1 + wf2
    elif operation == "-":
        final = wf1 - wf2
    elif operation == "*":
        final = wf1 * wf2
    elif operation == "/":
        final = np.divide(wf1, wf2, out=np.zeros_like(wf1), where=wf2!=0)
    else:
        raise ValueError(f"Unsupported operation: {operation}")
    return final

def genSCPI(cmd: WaveformCommand, channel=1):
    """    
    :param cmd: parsed WaveformCommand
    :type cmd: WaveformCommand
    :param channel: AWG output channel 

    Returns: 
        list[str]: List of SCPI command strings.
    """
    scpi_func = WAVEFORM_MAP[cmd.type]

    return [
        f":SOUR{channel}:FUNC {scpi_func}",
        f":SOUR{channel}:FREQ {cmd.frequency}",
        f":SOUR{channel}:VOLT {cmd.amplitude}",
        f":SOUR{channel}:VOLT:OFFS {cmd.offset}",
        f":SOUR{channel}:PHAS {cmd.phase}",
        f":OUTP{channel} ON"
    ]
    

