#!/usr/bin/python

ATTRIBUTES = ["id", "sending_address", "date","time","receiving_address","price", "status"]
FMT = "i50s11s5s50s9si"
CODING = "ascii"

SERIAL_FILENAME="data/serial.dat"
SEQUENTIAL_FILENAME="data/sequental.dat"

F = 5  # Broj slogova u bloku
N = 2
