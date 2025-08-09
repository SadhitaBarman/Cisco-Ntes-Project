# Cisco VIP Network Analysis & Simulation Tool

This project is a **complete network parsing, topology generation, validation, and simulation tool**  
built to analyze Cisco network configurations, detect issues, and simulate network behavior.  

---

## 📌 Features
- **Configuration Parsing**  
  Extracts IPs, VLANs, MTU, bandwidth, routes, and load from Cisco device configs.
  
- **Automatic Topology Building**  
  Generates a visual network map (`topology.png`) and JSON representation (`topology.json`).

- **Network Validation Checks**  
  - Duplicate IP detection  
  - Missing devices/components  
  - MTU mismatches  
  - Overloaded links → recommends **load balancing** & activating secondary paths  

- **Simulation Engine**  
  Simulates devices sending messages, handles link failures, and logs activity.

- **Automated Pipeline**  
  One command runs everything: parsing → topology → checks → simulation.

---

## 📂 Project Structure
├── src/ # Python source code
│ ├── parser.py
│ ├── topology.py
│ ├── checks.py
│ ├── simulator.py
│ └── run_demo.py
├── Conf/ # Sample configuration files
├── out/ # Output folder (auto-generated)
│ ├── parsed/ # Parsed config JSON files
│ ├── topology.json
│ ├── topology.png
│ ├── report.txt
│ └── sim_logs/
├── requirements.txt # Python dependencies
├── README.md # Project documentation

# Outputs
>out/topology.png → Network diagram
>out/topology.json → Topology data
>out/report.txt → Network issues & recommendations
>out/sim_logs/*.log → Simulation logs per device

# License
This project is for educational purposes under the Cisco VIP Program guidelines.

# Author
Developed by Sadhita Barman

