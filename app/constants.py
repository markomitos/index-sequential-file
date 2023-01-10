#!/usr/bin/python

HEADER = ["index_address","overflow_address"]
LEAF = ["block_value","block_address","overflow_value","overflow_address"]
ATTRIBUTES = ["id", "sending_address", "date","time","receiving_address","price", "status"]
OVERFLOW = ["id", "sending_address", "date","time","receiving_address","price","next", "status"]
LFMT="iiii"
HFMT = "ii"
FMT = "i50s11s5s50s9si"
OFMT = "i50s11s5s50s9sii"
CODING = "ascii"

SERIAL_FILENAME="data/serial.dat"
SEQUENTIAL_FILENAME="data/sequental.dat"
INDEX_SEQUENTIAL_FILENAME="data/index_sequential.dat"

F = 5  # Broj slogova u bloku
N = 2
