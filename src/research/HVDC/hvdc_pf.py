import time
import scipy
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
import numpy as np


def dcnetworkpf(Ybusdc, Vdc, Pdc, slack, noslack, droop, PVdroop, Pdcset, Vdcset, dVdcset, pol, tol, itmax):
    """
    Runs the dc network power flow, possibly including several dc grids.
    Each dc networks can have dc slack buses or several converters in dc
    voltage control.

    MatACDC
    Copyright (C) 2012 Jef Beerten
    University of Leuven (KU Leuven)
    Dept. Electrical Engineering (ESAT), Div. ELECTA
    Kasteelpark Arenberg 10
    3001 Leuven-Heverlee, Belgium

    :param Ybusdc: dc network bus matrix, possibly including multiple dc grids
    :param Vdc: vector with voltages at each dc bus
    :param Pdc: vector with dc power extractions at each dc bus
    :param slack: bus number of dc slack buses
    :param noslack: bus numbers of non-dc slack buses
    :param droop: bus numbers with distributed voltage control
    :param PVdroop: voltage droop gain
    :param Pdcset: voltage droop power set-point
    :param Vdcset: voltage droop voltage set-point
    :param dVdcset: voltage droop deadband
    :param pol: dc grids topology
                1 = monopolar (asymmetrically grounded)
                2 = monopolar (symmetrically grounded) or bipolar
    :param tol: Newton's method's tolerance
    :param itmax: Newton's method's maximum iterations
    :return: VDC : Updated vector with voltages at each dc bus
             PDC : Updated vector with dc power extractions at each dc bus
    """

    # initialisation
    nb = len(Vdc) # number of dc busses
    Pdc1 = -Pdc # convention on power flow direction
    Pdc1[droop] = -Pdcset[droop] # droop power set - points
    drooplidx = (droop - np.ones(len[droop], 1)) * nb + droop # linear droop indices

    # ----- dc network iteration - ----
    # initialisation
    it = 0
    converged = 0

    # Newton - Raphson iteration
    while not converged and it <= itmax:
        # update iteration counter
        it = it + 1

        # calculate power injections and Jacobian matrix
        Pdccalc = pol * Vdc * (Ybusdc * Vdc)
        J = sp.csc_matrix(pol * Ybusdc * (Vdc * Vdc.T))
        J[(1:nb:nb * nb) + (0:nb-1)] = sp.diag(J) + Pdccalc # replace matrix elements

        # include droop characteristics
        Vdcsetlh = (abs(Vdc - Vdcset) <= dVdcset) * Vdc +  ((Vdc - Vdcset) > dVdcset) * (Vdcset + dVdcset) + ((Vdc - Vdcset) < -dVdcset) * (Vdcset - dVdcset) # define set - point with deadband

        Pdccalc[droop] = Pdccalc[droop] + 1.0 / PVdroop[droop] * (Vdc[droop] - Vdcsetlh[droop]) # droop addition
        J[drooplidx] = J(drooplidx) + 1.0 / PVdroop[droop] * Vdc[droop]

        # dc network solution
        Jr = J(noslack, noslack) # reduce Jacobian
        dPdcr = Pdc1(noslack)-Pdccalc(noslack) # power mismatch vector
        dVr = spsolve(Jr, dPdcr)  # voltage corrections

        # update dc voltages
        Vdc[noslack] = Vdc(noslack) * (np.ones(len(noslack), 1) + dVr)

        # convergence check
        if max(abs(dVr)) < tol:
            converged = 1

    # convergence print
    if not converged:
        print('\nDC network power flow did NOT converge after %d iterations\n', it)


    # ----- Output update -----
    # recalculate slack bus powers
    Pdc1[slack] = pol * Vdc[slack] * (Ybusdc[slack,:] *Vdc)
    Pdc[slack] = -Pdc1[slack]

    # recalculate voltage droop bus powers
    Pdc1[droop] = pol * Vdc[droop] * (Ybusdc[droop,:] * Vdc)
    Pdc[droop] = -Pdc1[droop]

    return Vdc, Pdc