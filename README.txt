# NetRecon

**NetRecon** — a safe local port scanner with multithreading and banner grabbing support. Ideal for demonstrating network programming skills.

---

## ⚡ Features

- TCP port scanning
- Multithreading
- Banner grabbing (if available)
- JSON scan reports
- Secure by default: scans only localhost
- `--force` option to scan other hosts (permission required!)

---

## 🚀 Usage

```bash
# Scan local ports 20-1024
python3 netrecon.py localhost --ports 20-1024

# Scan and save results to JSON
python3 netrecon.py 127.0.0.1 --ports 22,80,443 --json out.json

# Scan a remote host (permission required!)
python3 netrecon.py 192.0.2.5 --ports 1-1000 --force
