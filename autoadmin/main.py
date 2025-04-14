import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import autoadmin

def main():
    autoadmin.executeTagCommands()

if __name__ == "__main__":
    main()