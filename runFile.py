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
fname = "test_waveforms.awg"
if not os.path.exists(fname):
    print("DEBUG: FILE DOES NOT EXIST")

scpi = compileFile(fname)
assert len(scpi) > 0
cache_file = fname + ".cache.json"
run_scpi_file(cache_file)