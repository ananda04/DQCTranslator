from parserAndGen import (
    parse_command,
    genSCPI,
    compileFile,
    save_cache,
    run_scpi_file
)

# -------------------------------
# Mock Instrument (VERY IMPORTANT)
# -------------------------------
class MockInstrument:
    def __init__(self):
        self.commands = []

    def write(self, cmd):
        print(f"WRITE → {cmd}")
        self.commands.append(cmd)


# -------------------------------
# Unit Tests
# -------------------------------

def test_parse():
    print("\n[TEST] parse_command")

    cmd = parse_command("SINE-1e6-1.0-0.0-90")

    assert cmd.type == "SINE"
    assert cmd.frequency == 1e6
    assert cmd.amplitude == 1.0
    assert cmd.offset == 0.0
    assert cmd.phase == 90

    print("parse_command passed")


def test_codegen():
    print("\n[TEST] genSCPI")

    cmd = parse_command("SINE-1e6-1.0-0.0-90")
    scpi = genSCPI(cmd)

    for line in scpi:
        print(line)

    assert ":SOUR1:FUNC SIN" in scpi
    assert ":SOUR1:FREQ 1000000.0" in scpi

    print("genSCPI passed")


def test_compile_file():
    print("\n[TEST] compileFile")

    # Create a temporary DSL file
    filename = "test.awg"
    with open(filename, "w") as f:
        f.write("""
# Test waveform file
SINE-1e6-1-0
TRI-2e6-0.5-0
""")

    scpi = compileFile(filename)

    for line in scpi:
        print(line)

    assert len(scpi) > 0
    print("compileFile passed")

    return scpi, filename


def test_cache_and_run(scpi, filename):
    print("\n[TEST] cache + run")

    # Save cache
    save_cache(scpi, filename)

    cache_file = filename + ".cache.json"

    # Run using mock instrument
    instrument = MockInstrument()
    run_scpi_file(cache_file, instrument)

    assert len(instrument.commands) == len(scpi)

    print("cache + run passed")


# -------------------------------
# Run All Tests
# -------------------------------

if __name__ == "__main__":
    test_parse()
    test_codegen()
    scpi, fname = test_compile_file()
    test_cache_and_run(scpi, fname)

    print("\n ALL TESTS PASSED")