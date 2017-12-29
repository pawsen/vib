#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# common python libraries
import numpy as np
import matplotlib.pyplot as plt
from collections import namedtuple
import pickle

# vibration libraries
from vib.signal import Signal
from vib.fnsi import FNSI
from vib.modal import modal_ac, frf_mkc
from vib.helper.modal_plotting import (plot_knl, plot_frf, plot_svg)
from vib.frf import FRF
from vib.fnsi import NL_force, NL_polynomial, NL_spline

# Parameters for 2dof model
from parameters import par

show_periodicity = True

# conversion between Hz and rad/s
sca = 2*np.pi

# load data
path = 'data/'
filename = 'pyds_multisinevrms'
Nm = namedtuple('Nm', 'y yd ydd u t finst fs ns')
lin = pickle.load(open(path + filename + '0.01' + '.pkl', 'rb'))
nlin = pickle.load(open(path + filename + '2'  + '.pkl', 'rb'))

# which dof to get H1 estimate from/show periodicity
dof = 0

# Frequency interval of interest
fmin = 0
fmax = 5/2/np.pi
# Setup the signal/extract periods
slin = Signal(lin.u, lin.fs, lin.y)
snlin = Signal(nlin.u, nlin.fs, nlin.y)

# show periodicity, to select periods from
if show_periodicity:
    slin.periodicity(lin.ns, dof, offset=0)
    snlin.periodicity(nlin.ns, dof, offset=0)

per = [7,8]
slin.cut(lin.ns, per)
snlin.cut(lin.ns, per)

# inl: connection. -1 is ground. enl: exponent. knl: coefficient. Always 1.
inl = np.array([[0,-1],
                [1,-1]])
enl = np.array([3,3])
knl = np.array([1,1])
nl_pol = NL_polynomial(inl, enl, knl)
nl = NL_force(nl_pol)

# zero-based numbering of dof
# idof are selected dofs.
# iu are dofs of force
iu = 0
idof = [0,1]

# ims: matrix block order. At least n+1
# nmax: max model order for stabilisation diagram
# ncur: model order for estimation
ims = 22
nmax = 20
ncur = 4
nlist = np.arange(2, nmax+3, 2)

## nonlinear identification at high level
# Calculate stabilization diagram
fnsi = FNSI(snlin, nl, idof, fmin, fmax)
fnsi.calc_EY()
fnsi.svd_comp(ims)
sd = fnsi.stabilization(nlist)
# Do estimation
fnsi.id(ncur)
fnsi.nl_coeff(iu, dof)

## linear identification at high level
nl = NL_force()
fnsi2 = FNSI(snlin, nl, idof, fmin, fmax)
fnsi2.calc_EY()
fnsi2.svd_comp(ims)
fnsi2.id(ncur)
fnsi2.nl_coeff(iu, dof)

## linear identification at low level
fnsi3 = FNSI(slin, nl, idof, fmin, fmax)
fnsi3.calc_EY()
fnsi3.svd_comp(ims)
fnsi3.id(ncur)
fnsi3.nl_coeff(iu, dof)

def print_modal(fnsi):
    # calculate modal parameters
    modal = modal_ac(fnsi.A, fnsi.C)
    natfreq = modal['wn']
    dampfreq = modal['wd']
    damping = modal['zeta']
    nw = min(len(natfreq), 8)

    print('Undamped ω: {}'.format(natfreq[:nw]*sca))
    print('damped ω: {}'.format(dampfreq[:nw]*sca))
    print('damping: {}'.format(damping[:nw]))
    return modal

print('## nonlinear identified at high level')
modal = print_modal(fnsi)
print('## linear identified at high level')
modal2 = print_modal(fnsi2)
print('## linear identified at low level')
modal3 = print_modal(fnsi3)

# Stabilization plot
fnsi.plot_stab(sca=sca)

## Compare FRFs
frf = FRF(snlin, fmin=1e-3, fmax=5/2/np.pi)
frf_freq, frf_H = frf.periodic()

## MCK
M, C, K = par['M'], par['C'], par['K']
freq_mck, H_mck = frf_mkc(M, K, C=C, fmin=1e-3, fmax=fmax, fres=0.01)

fH1, ax = plt.subplots()
plot_frf(frf_freq, frf_H, dof, sca, ax=ax, ls='-', c='k', label='From high signal')
plot_frf(freq_mck, H_mck[0,:], dof, sca, ax=ax, label='mck', ls=':', c='b')
fnsi.plot_frf(dof, sca, ax=ax, label='nl high', ls='--', c='C1')
fnsi2.plot_frf(dof, sca, ax=ax, label='lin high', ls='--', c='C2')
fnsi3.plot_frf(dof, sca, ax=ax, label='lin low', ls='-.', c='C3')
ax.legend()
#ax.legend_ = None
ax.set_xlabel('Frequency (rad/s)')
# For linear scale: 'Amplitude (m/N)'
ax.set_ylabel('Amplitude (dB)')

# The phase from FRF is shown as:
frfl = FRF(slin,fmin=1e-3,fmax=5/2/np.pi)
frfl_freq, frfl_H = frfl.periodic()
plt.figure()
plt.plot(frf_freq*sca, np.angle(frfl_H[dof]) / np.pi * 180)
plt.xlabel('Frequency (rad/s)')
plt.ylabel('Phase angle (deg)')
plt.yticks(np.linspace(-180, 180, 360//90))


plt.show()

# ## nonlinear identified at high level
# Undamped ω: [ 1.          3.31662479]
# damped ω: [ 0.99874922  3.31624788]
# damping: [ 0.05        0.01507557]
# ## linear identified at high level
# Undamped ω: [ 1.45233167  3.49273364]
# damped ω: [ 1.45152709  3.49244239]
# damping: [ 0.03328181  0.01291384]
# ## linear identified at low level
# Undamped ω: [ 1.0000266   3.31663515]
# damped ω: [ 0.99877587  3.31625824]
# damping: [ 0.04999828  0.0150755 ]
