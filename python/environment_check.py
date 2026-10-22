import sys
import matplotlib
import numpy
import pandas
import pytest
import openpyxl

def main ():
    print("=== Retail Sales Analytics Environment Check ===")
    print(f"Python      : {sys.version.split()[0]}")
    print(f"Pandas      : {pandas.__version__}")
    print(f"NumPy       : {numpy.__version__}")
    print(f"Matplotlib  : {matplotlib.__version__}")
    print(f"OpenPyXL    : {openpyxl.__version__}")
    print(f"Pytest      : {pytest.__version__}")
    print("STATUS       : Environment ready")


if __name__ == "__main__":
    main()