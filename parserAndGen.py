from dataclasses import dataclass
import json
import numpy as np 

WAVEFORM_MAP = {
    "ARB-SINE": "ARB-SINE",
    "ARB-TRI": "ARB-TRI",
    "ARB-SQUARE": "ARB-SQUARE",
    "ARB-NOISE": "ARB-NOISE",
    "ARB-EXP": "ARB-EXP",
    "ARB-DECAY": "ARB-DECAY",
    "ARB-SAW": "ARB-SAW",
    "ARB-RAMP": "ARB-RAMP",
    "ARB-PULSE": "ARB-PULSE",
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

    return WaveformCommand(wf, freq, amp, offset, phase)

def generate_ARBMEM(cmd: WaveformCommand, sample_rate=1e9, duration=1e-3):
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

    def operations_ARB(waveform1, waveform2, operation):
        if operation == "add":
            if len(waveform1) != len(waveform2):
                if
                raise ValueError("Waveforms must have the same length for addition.")
            return waveform1 + waveform2
        elif operation == "subtract":
            if len(waveform1) != len(waveform2):
                raise ValueError("Waveforms must have the same length for subtraction.")
            return waveform1 - waveform2
        elif operation == "multiply":
            if len(waveform1) != len(waveform2):
                raise ValueError("Waveforms must have the same length for multiplication.")
            return waveform1 * waveform2
        elif operation == "divide":
            if len(waveform1) != len(waveform2):
                raise ValueError("Waveforms must have the same length for division.")
            with np.errstate(divide='ignore', invalid='ignore'):
                result = np.true_divide(waveform1, waveform2)
                result[~np.isfinite(result)] = 0  # Set inf and NaN to 0
                return result
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        t = np.arange(0, duration, 1/sample_rate)
        return result
    
    if cmd.type == "ARB-SINE":
        ARB-SINE =np.array(cmd.amplitude * np.sin(2 * np.pi * cmd.frequency * t + np.radians(cmd.phase)) + cmd.offset)
    elif cmd.type == "ARB-TRI":
        ARB-TRI =np.array(cmd.amplitude * (2 * np.abs(2 * (t * cmd.frequency - np.floor(t * cmd.frequency + 0.5))) - 1) + cmd.offset)
    elif cmd.type == "ARB-SQUARE":
        ARB-SQUARE =np.array(cmd.amplitude * np.sign(np.sin(2 * np.pi * cmd.frequency * t + np.radians(cmd.phase))) + cmd.offset)
    elif cmd.type == "ARB-NOISE":
        ARB-NOISE =np.array(cmd.amplitude * np.random.normal(0, 1, len(t)) + cmd.offset)
    elif cmd.type == "ARB-EXP":
        ARB-EXP =np.array(cmd.amplitude * (1 - np.exp(-t * cmd.frequency)) + cmd.offset)
    elif cmd.type == "ARB-DECAY":
        ARB-DECAY =np.array(cmd.amplitude * np.exp(-t * cmd.frequency) + cmd.offset)
    elif cmd.type == "ARB-SAW":
        ARB-SAW =np.array(cmd.amplitude * (t * cmd.frequency - np.floor(t * cmd.frequency)) + cmd.offset)
    elif cmd.type == "ARB-RAMP":
        ARB-RAMP =np.array(cmd.amplitude * (t * cmd.frequency - np.floor(t * cmd.frequency)) + cmd.offset)
    elif cmd.type == "ARB-PULSE":
        ARB-PULSE =np.array(cmd.amplitude * (np.where((t % (1/cmd.frequency)) < (0.5/cmd.frequency), 1, 0)) + cmd.offset)
    else:
        raise ValueError(f"Unsupported waveform type: {cmd.type}")
   

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

def save_waveform_to_file(waveform, filename):
    """    
    :param waveform: Array of samples representing the arbitrary waveform.
    :type waveform: np.ndarray
    :param filename: Name of the file to save the waveform data.
    :type filename: str
    """
    np.savetxt(filename, waveform, delimiter=",")
def load_waveform_from_file(filename):
    """    
    :param filename: Name of the file to load the waveform data from.
    :type filename: str

    Returns:
        np.ndarray: Array of samples representing the arbitrary waveform.
    """
    return np.loadtxt(filename, delimiter=",")  

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
    

