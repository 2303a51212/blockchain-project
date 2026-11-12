"""
Standalone demo: a tiny blockchain for certificate verification.
No libraries needed. Run:  python demo_blockchain.py
"""
import hashlib, json, time


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class Block:
    def __init__(self, index, cert_data, prev_hash):
        self.index = index
        self.timestamp = time.time()
        self.cert_data = cert_data                      # dict with student, course, etc.
        self.cert_hash = sha256(json.dumps(cert_data, sort_keys=True))
        self.prev_hash = prev_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        return sha256(f"{self.index}{self.timestamp}{self.cert_hash}{self.prev_hash}")


class CertificateChain:
    def __init__(self):
        self.chain = [Block(0, {"genesis": True}, "0")]

    def issue(self, student, course, year):
        data = {"student": student, "course": course, "year": year}
        block = Block(len(self.chain), data, self.chain[-1].hash)
        self.chain.append(block)
        return block.cert_hash                           # give this ID / QR to the student

    def verify(self, student, course, year):
        h = sha256(json.dumps({"student": student, "course": course, "year": year}, sort_keys=True))
        return any(b.cert_hash == h for b in self.chain[1:])

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            cur, prev = self.chain[i], self.chain[i - 1]
            if cur.hash != cur.compute_hash() or cur.prev_hash != prev.hash:
                return False
        return True


if __name__ == "__main__":
    ledger = CertificateChain()
    cert_id = ledger.issue("Ravi Kumar", "B.Tech Computer Science", 2025)
    print("Certificate ID :", cert_id)

    print("Genuine cert   :", ledger.verify("Ravi Kumar", "B.Tech Computer Science", 2025))   # True
    print("Fake cert      :", ledger.verify("Ravi Kumar", "B.Tech Computer Science", 2020))   # False
    print("Chain valid    :", ledger.is_chain_valid())                                        # True

    ledger.chain[1].cert_hash = "tampered"               # simulate an attack
    print("After tampering:", ledger.is_chain_valid())                                        # False
