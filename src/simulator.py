import threading
import queue
import time
import json
import pathlib

OUT_DIR = pathlib.Path("out")
LOG_DIR = OUT_DIR / "sim_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

class Node(threading.Thread):
    def __init__(self, name, neighbors):
        super().__init__(daemon=True)
        self.name = name
        self.inbox = queue.Queue()
        self.neighbors = neighbors
        self.log = []
        self.alive = True
        self.paused = threading.Event()
        self.paused.clear()
    def run(self):
        self.log.append(f"{self.name}: started")
        self.broadcast({"type": "HELLO", "from": self.name, "time": time.time()})
        while self.alive:
            if self.paused.is_set():
                time.sleep(0.1)
                continue
            try:
                msg = self.inbox.get(timeout=0.5)
                self.handle(msg)
            except queue.Empty:
                continue
    def handle(self, msg):
        self.log.append(f"{self.name} received: {msg}")
        if msg.get("type") == "HELLO":
            self.send(msg.get("from"), {"type": "HELLO_ACK", "from": self.name})
    def broadcast(self, msg):
        Simulator.deliver_broadcast(self.name, msg)
    def send(self, target, msg):
        Simulator.deliver_unicast(self.name, target, msg)
    def pause(self):
        self.paused.set()
    def resume(self):
        self.paused.clear()
    def stop(self):
        self.alive = False

class Simulator:
    nodes = {}
    links_up = set()
    @classmethod
    def build_from_topology(cls, topology_file="out/topology.json"):
        data = json.load(open(topology_file))
        links = [(l['source'], l['target']) for l in data['links']]
        for nid in [n['id'] for n in data['nodes']]:
            cls.nodes[nid] = Node(nid, [])
        for a,b in links:
            cls.nodes[a].neighbors.append(b)
            cls.nodes[b].neighbors.append(a)
            cls.links_up.add(frozenset((a,b)))
    @classmethod
    def start_all(cls):
        for n in cls.nodes.values():
            n.start()
        time.sleep(0.5)
    @classmethod
    def deliver_broadcast(cls, sender, msg):
        for nname in cls.nodes:
            if nname != sender and frozenset((sender, nname)) in cls.links_up:
                cls.nodes[nname].inbox.put(msg)
    @classmethod
    def deliver_unicast(cls, sender, target, msg):
        if frozenset((sender, target)) in cls.links_up:
            cls.nodes[target].inbox.put(msg)
    @classmethod
    def inject_link_failure(cls, a, b):
        link = frozenset((a,b))
        if link in cls.links_up:
            cls.links_up.remove(link)
            print(f"Link down: {a} <-> {b}")
    @classmethod
    def dump_logs(cls):
        for n in cls.nodes.values():
            with open(LOG_DIR / f"{n.name}.log", "w") as f:
                f.write("\n".join(n.log))

if __name__ == "__main__":
    Simulator.build_from_topology()
    Simulator.start_all()
    time.sleep(1)
    links = list(Simulator.links_up)
    if links:
        a,b = list(links[0])
        Simulator.inject_link_failure(a,b)
    Simulator.dump_logs()
    print("Sim logs written to out/sim_logs/")