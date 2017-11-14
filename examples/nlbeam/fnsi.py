#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scipy import io
import numpy as np
import matplotlib.pyplot as plt
from collections import namedtuple

from vib.signal import Signal
from vib.fnsi import FNSI
from vib.fnsi import NL_force, NL_polynomial
from vib.common import modal_properties, db, frf_mkc
from vib.helper.fnsi_plots import (plot_modes, plot_knl, plot_linfrf,
                                   plot_stab)
from vib.frf import FRF

sca = 1
def print_modal(fnsi):
    # calculate modal parameters
    modal = modal_properties(fnsi.A, fnsi.C)
    natfreq = modal['wn']
    dampfreq = modal['wd']
    damping = modal['zeta']
    nw = min(len(natfreq), 8)
    print('Undamped ω: {}'.format(natfreq[:nw])*sca)
    print('damped ω: {}'.format(dampfreq[:nw])*sca)
    print('damping: {}'.format(damping[:nw]))
    return modal

def load(nonlin):
    path = 'data/'
    if nonlin:
        mat_u = io.loadmat(path + 'u_15.mat')
        mat_y = io.loadmat(path + 'y_15.mat')
    else:
        mat_u = io.loadmat(path + 'u_01.mat')
        mat_y = io.loadmat(path + 'y_01.mat')

    fs = mat_u['fs'].item()  # 3000
    fmin = mat_u['fmin'].item()  # 5
    fmax = mat_u['fmax'].item()  # 500
    iu = mat_u['iu'].item()  # 2 location of force
    nper = mat_u['P'].item()
    nsper = mat_u['N'].item()
    u = mat_u['u'].squeeze()
    y = mat_y['y']

    # zero-based numbering of dof
    # iu are dofs of force
    sig = namedtuple('sig', 'u y fs fmin fmax iu nper nsper')
    return sig(u,y,fs,fmin,fmax,iu-1,nper,nsper)

lin = load(nonlin=False)
slin = Signal(lin.u, lin.fs, lin.y)
per = [4,5,6,7,8,9]
slin.cut(lin.nsper, per)

# idof are selected dofs, ie. all dofs here
idof = np.arange(7)
# dof where nonlinearity is
nldof = 6

# ims: matrix block order. At least n+1
# nmax: max model order for stabilisation diagram
# ncur: model order for erstimation
ims = 40
nmax = 20
ncur = 6
nlist = np.arange(2,nmax+3,2)

nl = NL_force()
fnsi = FNSI(slin, nl, idof, lin.fmin, lin.fmax)
fnsi.calc_EY()
fnsi.svd_comp(ims)
fnsi.stabilisation_diagram(nlist)
# Do identification
fnsi.id(ncur)
fnsi.calc_modal()
fnsi.nl_coeff(lin.iu, nldof)

# Load nonlinear signal
nlin = load(nonlin=True)
snlin = Signal(nlin.u, nlin.fs, nlin.y)
snlin.cut(nlin.nsper, per)

# Linear identification on nonlinear signal
fnsi_nl1 = FNSI(snlin, nl, idof, nlin.fmin, nlin.fmax)
fnsi_nl1.calc_EY()
fnsi_nl1.svd_comp(ims)
fnsi_nl1.stabilisation_diagram(nlist)
fnsi_nl1.id(ncur)
fnsi_nl1.calc_modal()
fnsi_nl1.nl_coeff(nlin.iu, nldof)


enl = np.array([3,2])
knl = np.array([1,1])
inl = np.array([[6,-1], [6,-1]])
nl_pol = NL_polynomial(inl, enl, knl)
nl = NL_force(nl_pol)

fnsi_nl2 = FNSI(snlin, nl, idof, nlin.fmin, nlin.fmax)
fnsi_nl2.calc_EY()
fnsi_nl2.svd_comp(ims)
fnsi_nl2.stabilisation_diagram(nlist)
fnsi_nl2.id(ncur)
fnsi_nl2.calc_modal()
fnsi_nl2.nl_coeff(nlin.iu, nldof)

# print modal characteristics
print('## linear identified at low level')
print_modal(fnsi)
print('## linear identified at high level')
print_modal(fnsi_nl1)
print('## nonlinear identified at high level')
print_modal(fnsi_nl2)

# FRF
frf = FRF(snlin, fmin=nlin.fmin, fmax=nlin.fmax)
frf_freq, frf_H = frf.periodic()

# Do some plotting
dof = 6

# periodicity
slin.periodicity(lin.nsper, dof)
fper, ax = snlin.periodicity(nlin.nsper, dof)
#ax.set_title(''); ax.legend_ = None
ax.yaxis.label.set_size(20)
ax.xaxis.label.set_size(20)
ax.tick_params(labelsize=20)

# FRF
fH1, ax = plt.subplots()
ax.plot(frf_freq*sca, db(np.abs(frf_H[dof])), '-.k', label='From signal')
plot_linfrf(fnsi, dof, fig=fH1, ax=ax, label='lin')
plot_linfrf(fnsi_nl1, dof, fig=fH1, ax=ax, label='nl_1')
plot_linfrf(fnsi_nl2, dof, fig=fH1, ax=ax, ls='--', label='nl2')
#ax.set_title(''); ax.legend_ = None
ax.legend()

# Modes
fmodes, ax = plt.subplots()
plot_modes(idof, fnsi.modal, sca, fig=fmodes)
plot_modes(idof, fnsi_nl1.modal, sca, fig=fmodes)
plot_modes(idof, fnsi_nl2.modal, sca, fig=fmodes)
#ax.set_title(''); ax.legend_ = None

# stab diagram
# fstab, ax1 = plt.subplots()
# ax2 = ax1.twinx()

fsdlin, ax = plot_stab(fnsi, nlist, sca)
ax.set_title('Linear at low level')  #; ax.legend_ = None
fsdnlin1, ax = plot_stab(fnsi_nl1, nlist, sca)
ax.set_title('Linear at high level')  #; ax.legend_ = None
fsdnlin2, ax = plot_stab(fnsi_nl2, nlist, sca)
ax.set_title('Nonlinear at high level')  #; ax.legend_ = None

# knl
fknl, axknl = plot_knl(fnsi_nl2, sca)
for ax in axknl:
    ax[0].legend().remove()
    ax[0].set_title('')
axknl[0][0].set_ylim(np.array([0.99, 1.01])*7.996e9)
axknl[1][0].set_ylim(-np.array([0.99, 1.01])*1.049e7)

plt.show()