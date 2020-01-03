import numpy as np
from scipy.sparse import lil_matrix, diags
import scipy.sparse as sp
from scipy.sparse.linalg import inv, spsolve
from enum import Enum

np.set_printoptions(precision=2)


class DcType(Enum):
    P = 0
    V = 1


# line data
R = np.array([90, 100, 75, 50, 35]) * 0.0121
F = np.array([1, 2, 3, 3, 4]) - 1
T = np.array([3, 4, 4, 5, 6]) - 1

# node data
V0 = np.array([400, 400, 400, 400, 400, 399])
P0 = np.array([200, -120, 0, 0, 0, 0])
types = np.array([DcType.P.value, DcType.P.value, DcType.P.value, DcType.P.value, DcType.V.value, DcType.V.value])

p_idx = np.where(types == DcType.P.value)[0]
v_idx = np.where(types == DcType.V.value)[0]

m = len(R)
n = len(V0)
Cf = lil_matrix((m, n))
Ct = lil_matrix((m, n))
for i, val in enumerate(zip(R, F, T)):
    r, f, t = val
    Cf[i, f] = 1
    Ct[i, t] = 1
Gs = 1 / R
# Gtt = Gs / 2
# Gff = Gs / 2
# Gft = - Gs / 2
# Gtf = - Gs / 2

Gtt = Gs
Gff = Gs
Gft = - Gs
Gtf = - Gs

Gf = diags(Gff) * Cf + diags(Gft) * Ct
Gt = diags(Gtf) * Cf + diags(Gtt) * Ct
G = (Cf.T * Gf + Ct.T * Gt).tocsc()

# split G
Gk = G[np.ix_(p_idx, p_idx)]
Gamma_k = -G[np.ix_(p_idx, v_idx)]
Ank = G[np.ix_(v_idx, v_idx)]

print(G.todense())
print(Gk.todense())
print(Gamma_k.todense())

# set initial condition
V = V0
P = P0

# form the jacobian
DV = diags(-P[p_idx] / (V[p_idx] * V[p_idx]), format='csc')
VV = diags(V[p_idx], format='csc')
WW = diags(V[v_idx], format='csc')
FI = diags(P[v_idx] / V[v_idx], format='csc')

J11 = inv(Gk - DV) * inv(VV)
J12 = inv(Gk - DV) * Gamma_k
J21 = -WW * Gamma_k.T * J11
J22 = FI + WW * (Ank - Gamma_k.T * J12)

J = sp.vstack([sp.hstack([J11, J12]),
               sp.hstack([J21,   J22])], format="csr")

print("J:\n", J.todense())

P = V * (G * V)

df = np.r_[P0[p_idx] - P[p_idx], V0[v_idx] - V[v_idx]-10]
dx = spsolve(J, df)

print("dx:\n", dx)

print()