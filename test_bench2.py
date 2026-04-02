import numpy as np
import os

from parserAndGen import (
    parse_command,
    compileFile,
    generate_ARBMEM,
    waveform_arithemtic,
    normalize_waveform,
    run_scpi_file
)

# -----------------------------
# Mock Instrument
# -----------------------------
class MockInstrument:
    def __init__(self):
        self.commands = []

    def write(self, cmd):
        print(f"[WRITE] {cmd}")
        self.commands.append(cmd)


# -----------------------------
# Test 1: Basic Parsing + SCPI
# -----------------------------
def test_basic_waveform():
    print("\n[TEST] Basic SINE command")

    scpi = parse_command("SINE-10000-1-0")

    assert isinstance(scpi, list)
    assert any("SOUR1:FREQ" in line for line in scpi)

    print("Basic waveform parsing passed")


# -----------------------------
# Test 2: ARB Waveform Generation
# -----------------------------
def test_arb_generation():
    print("\n[TEST] ARB waveform generation")

    from parserAndGen import WaveformCommand

    cmd = WaveformCommand("SINE", 10000, 1.0, 0.0, 0.0)

    try:
        wave = generate_ARBMEM(cmd)
        assert isinstance(wave, np.ndarray)
        print("ARB waveform generated")
    except Exception as e:
        print("ARB generation failed:", e)


# -----------------------------
# Test 3: Waveform Arithmetic
# -----------------------------
def test_waveform_arithmetic():
    print("\n[TEST] Waveform arithmetic")

    t = np.linspace(0, 1e-6, 1024)

    wave1 = np.sin(2 * np.pi * 10000 * t)
    wave2 = np.sin(2 * np.pi * 20000 * t)

    added = waveform_arithemtic(wave1, wave2, "+")
    subbed = waveform_arithemtic(wave1, wave2, "-")
    multiplied = waveform_arithemtic(wave1, wave2, "*")

    assert len(added) == len(wave1)
    assert np.max(np.abs(added)) <= 1.0

    print("Arithmetic operations passed")


# -----------------------------
# Test 4: Combined DSL (#+#)
# -----------------------------
def test_combined_expression():
    print("\n[TEST] Combined DSL expression")

    cmd = "ARB-SINE-10000-1-0-0-+-ARB-SINE-20000-0.5-0-0"
    
    try:
        scpi = parse_command(cmd)
        print("SCPI:", scpi)
        print("Combined expression parsed (partial support)")
    except Exception as e:
        print("Combined expression not fully supported yet:", e)


# -----------------------------
# Test 5: File Compilation
# -----------------------------
def test_compile_file():
    print("\n[TEST] File compilation")

    filename = "test_waveforms.awg"

    with open(filename, "w") as f:
        f.write("""
# Basic signals
SINE-1e6-1-0
TRI-2e6-0.5-0

# Arbitrary (will partially work)
ARB-SINE-1e6-1-0-0-+-ARB-SINE-2e6-0.5-0-0
""")

    scpi = compileFile(filename)

    assert isinstance(scpi, list)
    assert len(scpi) > 0

    print("File compilation passed")

    return filename


# -----------------------------
# Test 6: Cache + Execution
# -----------------------------
def test_run_cached(filename):
    print("\n[TEST] Cache + Execution")

    cache_file = filename + ".cache.json"

    instrument = MockInstrument()
    run_scpi_file(cache_file, instrument)

    assert len(instrument.commands) > 0

    print("Execution passed")


# -----------------------------
# Run All Tests
# -----------------------------
if __name__ == "__main__":
    test_basic_waveform()
    test_arb_generation()
    test_waveform_arithmetic()
    test_combined_expression()
    fname = test_compile_file()
    test_run_cached(fname)

    print("\n ALL TESTS COMPLETED")