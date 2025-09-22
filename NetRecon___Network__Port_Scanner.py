#!/usr/bin/env python3
import socket, argparse, concurrent.futures, json, time
from datetime import datetime

DEFAULT_TIMEOUT = 0.5
def scan_port(target, port, timeout):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            res = s.connect_ex((target, port))
            if res == 0:
                # try to grab banner
                try:
                    s.settimeout(0.8)
                    s.sendall(b"\r\n")
                    banner = s.recv(1024)
                    banner = banner.decode('utf-8', errors='replace').strip()
                except Exception:
                    banner = ''
                return port, True, banner
            else:
                return port, False, ''
    except Exception:
        return port, False, ''

def is_local(target):
    return target in ('localhost','127.0.0.1','::1')

def parse_ports(portspec):
    parts = []
    for p in portspec.split(','):
        p = p.strip()
        if '-' in p:
            a,b = p.split('-',1)
            parts.extend(range(int(a), int(b)+1))
        else:
            parts.append(int(p))
    return sorted(set(parts))

def main():
    parser = argparse.ArgumentParser(description='NetRecon — safe local port scanner')
    parser.add_argument('target', help='target host (default localhost allowed)')
    parser.add_argument('--ports', default='1-1024', help='ports e.g. 22,80,443,8000-8100')
    parser.add_argument('--timeout', type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument('--workers', type=int, default=200)
    parser.add_argument('--json', help='save json output to file')
    parser.add_argument('--force', action='store_true', help='allow scanning non-localhost targets (use only with permission)')
    args = parser.parse_args()

    target = args.target
    if not is_local(target) and not args.force:
        print('Refusing to scan non-local targets without --force. Use only on systems you own or with permission.')
        return

    ports = parse_ports(args.ports)
    print(f'Starting scan {target} ports {ports[0]}..{ports[-1]} threads={args.workers} timeout={args.timeout}')
    start = time.time()
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(scan_port, target, p, args.timeout): p for p in ports}
        for fut in concurrent.futures.as_completed(futures):
            port, open_, banner = fut.result()
            results.append({'port': port, 'open': open_, 'banner': banner})
            if open_:
                print(f'Open: {port} {(" | " + banner) if banner else ""}')
    elapsed = time.time() - start
    print(f'Scan complete in {elapsed:.2f}s')
    summary = {
        'target': target,
        'ports_scanned': len(ports),
        'open_ports': sorted([r for r in results if r['open']], key=lambda x: x['port']),
        'elapsed': elapsed,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        print('Saved JSON to', args.json)

if __name__ == '__main__':
    main()

