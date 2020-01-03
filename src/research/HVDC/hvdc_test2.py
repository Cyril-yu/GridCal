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
R = np.array([82, 102, 51, 20, 65]) * np.array([0.44, 0.55, 0.27, 0.11, 1])
F = np.array([1, 1, 2, 2, 4]) - 1
T = np.array([2, 3, 3, 4, 5]) - 1

# node data
V0 = np.array([320, 320, 320, 320, 320])
P0 = np.array([0, -758, 616, 384, 238])
types = np.array([DcType.V.value, DcType.P.value, DcType.P.value, DcType.P.value, DcType.P.value])

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
Gtt = Gs
Gff = Gs
Gft = - Gs
Gtf = - Gs

Gf = diags(Gff) * Cf + diags(Gft) * Ct
Gt = diags(Gtf) * Cf + diags(Gtt) * Ct
G = Cf.T * Gf + Ct.T * Gt

# split G
Gk = G[np.ix_(p_idx, p_idx)]
Gamma_k = -G[np.ix_(p_idx, v_idx)]
Ank = G[np.ix_(v_idx, v_idx)]

print(G.todense())
print(Gk.todense())
print(Gamma_k.todense())

# set initial condition
V = V0.copy()
P = P0.copy()

converged = False
it = 0
max_it = 10
tol = 1e-3
while not converged and it < max_it:

    # form the jacobian
    # P = V * (G.dot(V))
    # dP = P0[p_idx] - P[p_idx]
    P[p_idx] = V[p_idx] * (Gk * V[p_idx])
    dP = P0[p_idx] - P[p_idx]

    converged = max(abs(dP)) < tol

    J = diags(P[p_idx]) + Gk * V[p_idx].dot(V[p_idx])
    # J = diags(P[p_idx]) + diags(V[p_idx]) * Gk * diags(V[p_idx])
    dx = spsolve(J, dP)

    V[p_idx] = V[p_idx] * (1 + dx)

    print(it, converged)
    print('\tV', V)
    print('\tP', P)
    print('\tdP', dP)
    print('\tdx', dx)

    it += 1


print()