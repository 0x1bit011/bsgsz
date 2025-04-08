import hashlib
import random
import sys
from multiprocessing import Pool

# Elliptic curve parameters (using secp256k1 curve)
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A = 0
B = 7
Gx = 0x145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16
Gy = 0x667a05e9a1bdd6f70142b66558bd12ce2c0f9cbc7001b20c8a6a109c80dc5330
G = (Gx, Gy)
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def inverse_mod(k, p):
    if k == 0:
        raise ZeroDivisionError('division by zero')
    if k < 0:
        return p - inverse_mod(-k, p)
    s, old_s = 0, 1
    t, old_t = 1, 0
    r, old_r = p, k
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_s % p

def point_add(point1, point2):
    if point1 is None:
        return point2
    if point2 is None:
        return point1
    x1, y1 = point1
    x2, y2 = point2
    
    if x1 == x2 and y1 != y2:
        return None
    
    if x1 == x2:
        m = (3 * x1 * x1 + A) * inverse_mod(2 * y1, P)
    else:
        m = (y2 - y1) * inverse_mod(x2 - x1, P)
    
    x3 = m * m - x1 - x2
    y3 = y1 + m * (x3 - x1)
    return (x3 % P, -y3 % P)

def point_multiply(k, point):
    n = point
    q = None
    for i in range(k.bit_length()):
        if k & (1 << i):
            q = point_add(q, n)
        n = point_add(n, n)
    return q

def hash_to_int(x):
    return int(hashlib.sha256(x.encode('utf-8')).hexdigest(), 16)

def bsgs(P, Q, k, m):
    results = {}
    for j in range(m):
        point = point_multiply(j, P)
        results[point] = j
    for i in range(m):
        point = point_add(Q, point_multiply(i * m, P))
        if point in results:
            return i * m + results[point]
    return None

if __name__ == '__main__':
    M = 2**20
    k = random.randint(1, N-1)
    Q = point_multiply(k, G)
    
    result = bsgs(G, Q, k, M)
    if result is None:
        print("No solution found.")
    else:
        print(f"Found solution: k = {result}")
