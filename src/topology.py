import json
import pathlib
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ipaddress import IPv4Network

PARSED_DIR = pathlib.Path("out/parsed")
OUT_DIR = pathlib.Path("out")
OUT_DIR.mkdir(exist_ok=True)

def load_nodes():
    return [json.load(p.open()) for p in PARSED_DIR.glob("*.json")]

def network_of(ip, mask):
    try:
        return IPv4Network(f"{ip}/24", strict=False)
    except Exception:
        return None

def infer_links(nodes):
    G = nx.Graph()
    for n in nodes:
        role = "endpoint" if (n.get("meta", {}).get("load_kbps") is not None) else ("switch" if any(ifc.get("vlan") for ifc in n["interfaces"]) else "router")
        G.add_node(n["name"], role=role, data=n)
    for a in nodes:
        for b in nodes:
            if a["name"] == b["name"]: continue
            for ia in a["interfaces"]:
                for ib in b["interfaces"]:
                    if ia.get("description") and b["name"] in ia.get("description"):
                        G.add_edge(a["name"], b["name"], ifaces=(ia["iface"], ib["iface"]), mtu_a=ia.get("mtu"), mtu_b=ib.get("mtu"), bw_a=ia.get("bandwidth"), bw_b=ib.get("bandwidth"))
                    elif ia.get("ip") and ib.get("ip"):
                        na = network_of(ia["ip"], ia.get("netmask") or "255.255.255.0")
                        nb = network_of(ib["ip"], ib.get("netmask") or "255.255.255.0")
                        if na and nb and na.network_address == nb.network_address:
                            G.add_edge(a["name"], b["name"], ifaces=(ia["iface"], ib["iface"]), mtu_a=ia.get("mtu"), mtu_b=ib.get("mtu"), bw_a=ia.get("bandwidth"), bw_b=ib.get("bandwidth"))
    return G

if __name__ == "__main__":
    nodes = load_nodes()
    if not nodes:
        print("No parsed nodes found.")
        raise SystemExit(1)
    G = infer_links(nodes)
    adj = nx.readwrite.json_graph.node_link_data(G)
    open(OUT_DIR / "topology.json", "w").write(json.dumps(adj, indent=2))
    plt.figure(figsize=(8,6))
    pos = nx.spring_layout(G, seed=42)
    labels = {n: f"{n}\\n({G.nodes[n]['role']})" for n in G.nodes}
    nx.draw(G, pos, with_labels=True)
    nx.draw_networkx_labels(G, pos, labels)
    plt.title("Inferred Topology")
    plt.savefig(OUT_DIR / "topology.png")
    print("Topology written to out/topology.png and out/topology.json")