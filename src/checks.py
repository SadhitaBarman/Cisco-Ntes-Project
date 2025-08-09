import json
import pathlib
from collections import defaultdict
from ipaddress import IPv4Network

PARSED_DIR = pathlib.Path("out/parsed")
OUT_DIR = pathlib.Path("out")
OUT_DIR.mkdir(exist_ok=True)

def load_nodes():
    return [json.load(p.open()) for p in PARSED_DIR.glob("*.json")]

def ip_to_net(ip):
    try:
        return IPv4Network(f"{ip}/24", strict=False)
    except Exception:
        return None

def run_checks():
    nodes = load_nodes()
    ip_map = defaultdict(list)
    for n in nodes:
        for ifc in n["interfaces"]:
            if ifc.get("ip"):
                ip_map[ifc["ip"]].append((n["name"], ifc["iface"]))
    dup_ips = {ip: locs for ip, locs in ip_map.items() if len(locs) > 1}
    name_set = set(n["name"] for n in nodes)
    missing = []
    for n in nodes:
        for ifc in n["interfaces"]:
            desc = ifc.get("description")
            if desc:
                for p in desc.split():
                    if p.startswith("to-"):
                        cand = p.replace("to-", "")
                        if cand not in name_set:
                            missing.append((n["name"], ifc["iface"], cand))
    try:
        topo = json.load(open("out/topology.json"))
        edges = topo.get("links", [])
    except Exception:
        edges = []
    mtu_mismatches = []
    for e in edges:
        a = e.get("source")
        b = e.get("target")
        sd = e.get("mtu_a")
        td = e.get("mtu_b")
        if sd and td and sd != td:
            mtu_mismatches.append((a, b, sd, td))
    net_loads = defaultdict(int)
    iface_bw = defaultdict(int)
    for n in nodes:
        for ifc in n["interfaces"]:
            if ifc.get("ip"):
                net = ip_to_net(ifc["ip"])
                if net:
                    if n.get("meta", {}).get("load_kbps"):
                        net_loads[str(net.network_address)] += n["meta"]["load_kbps"]
                    if ifc.get("bandwidth"):
                        iface_bw[str(net.network_address)] = max(iface_bw[str(net.network_address)], ifc.get("bandwidth"))
    overloaded = []
    for net, load in net_loads.items():
        bw = iface_bw.get(net, None)
        if bw and load > bw:
            overloaded.append((net, load, bw))
    recs = []
    for net, load, bw in overloaded:
        recs.append(f"Network {net} overloaded: {load} kbps > {bw} kbps. Suggest secondary path.")
    if dup_ips:
        recs.append(f"Duplicate IPs: {dup_ips}")
    if missing:
        recs.append(f"Missing components: {missing}")
    if mtu_mismatches:
        recs.append(f"MTU mismatches: {mtu_mismatches}")
    rpt = OUT_DIR / "report.txt"
    with open(rpt, "w") as f:
        f.write("=== Network Validation Report\\n\\n")
        f.write("\n".join(recs))
    print("Report written to:", rpt)

if __name__ == "__main__":
    run_checks()