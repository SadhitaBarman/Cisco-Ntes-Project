import re
import json
import pathlib
from ipaddress import IPv4Network

CONF_DIR = pathlib.Path("Conf")
OUT_DIR = pathlib.Path("out/parsed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

iface_block_re = re.compile(r"^interface (\S+)([\s\S]*?)(?=^interface |\Z)", re.M)
hostname_re = re.compile(r"^hostname (\S+)", re.M)
ip_addr_re = re.compile(r"ip address (\d+\.\d+\.\d+\.\d+) (\d+\.\d+\.\d+\.\d+)")
mtu_re = re.compile(r"mtu (\d+)")
bw_re = re.compile(r"(?:bandwidth|speed) (\d+)")
desc_re = re.compile(r"description (.+)")
sw_vlan_re = re.compile(r"switchport access vlan (\d+)")
route_re = re.compile(r"ip route (\d+\.\d+\.\d+\.\d+) (\d+\.\d+\.\d+\.\d+) (\d+\.\d+\.\d+\.\d+)")
load_meta_re = re.compile(r"#\s*load:\s*(\d+)")

def parse_config(path: pathlib.Path):
    txt = path.read_text()
    hostname_m = hostname_re.search(txt)
    hostname = hostname_m.group(1) if hostname_m else path.parent.name
    interfaces = []

    for m in iface_block_re.finditer(txt):
        name = m.group(1).strip()
        block = m.group(2)
        ipm = ip_addr_re.search(block)
        mtum = mtu_re.search(block)
        bwm = bw_re.search(block)
        descm = desc_re.search(block)
        vlanm = sw_vlan_re.search(block)
        interfaces.append({
            "iface": name,
            "ip": ipm.group(1) if ipm else None,
            "netmask": ipm.group(2) if ipm else None,
            "mtu": int(mtum.group(1)) if mtum else None,
            "bandwidth": int(bwm.group(1)) if bwm else None,
            "description": descm.group(1).strip() if descm else None,
            "vlan": int(vlanm.group(1)) if vlanm else None,
        })

    routes = []
    for rm in route_re.finditer(txt):
        routes.append({"dst": rm.group(1), "mask": rm.group(2), "next_hop": rm.group(3)})

    load = None
    lm = load_meta_re.search(txt)
    if lm:
        load = int(lm.group(1))

    return {
        "name": hostname,
        "path": str(path),
        "interfaces": interfaces,
        "routes": routes,
        "meta": {"load_kbps": load}
    }

if __name__ == "__main__":
    for cfg in CONF_DIR.rglob("config.dump"):
        parsed = parse_config(cfg)
        outf = OUT_DIR / f"{cfg.parent.name}.json"
        open(outf, "w").write(json.dumps(parsed, indent=2))
        print("WROTE:", outf)

    for cfg in CONF_DIR.rglob("endpoint.conf"):
        parsed = parse_config(cfg)
        outf = OUT_DIR / f"{cfg.parent.name}.json"
        open(outf, "w").write(json.dumps(parsed, indent=2))
        print("WROTE:", outf)