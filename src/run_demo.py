import os
print("Running demo: parser -> topology -> checks -> simulator")
os.system("python src/parser.py")
os.system("python src/topology.py")
os.system("python src/checks.py")
os.system("python src/simulator.py")
print("Demo complete. Check the 'out/' folder for outputs.")