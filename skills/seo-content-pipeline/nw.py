#!/usr/bin/env python3
"""Minimal NeuronWriter client. Key is read from ENV_FILE (default ~/Desktop/WareMatch/.env), var API_KEY_NEURONWRITER."""
import json, os, sys, urllib.request

BASE = "https://app.neuronwriter.com/neuron-api/0.5/writer"
ENV_FILE = os.environ.get("ENV_FILE", os.path.expanduser("~/Desktop/WareMatch/.env"))

def _key():
    for line in open(ENV_FILE):
        if line.startswith("API_KEY_NEURONWRITER="):
            return line.split("=", 1)[1].strip().strip('"\'')
    sys.exit("API_KEY_NEURONWRITER not found")

def call(method, **payload):
    req = urllib.request.Request(f"{BASE}/{method}", data=json.dumps(payload).encode(),
        headers={"X-API-KEY": _key(), "Accept": "application/json", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

if __name__ == "__main__":
    method, payload = sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    print(json.dumps(call(method, **payload), indent=2))
