#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from scipy.linalg import eigvals
from ..hb.hbcommon import hb_signal
from copy import deepcopy


def phase(y, yd, dof=0, fig=None, ax=None, *args, **kwargs):
    if fig is None:
        fig, ax = plt.subplots()
        ax.clear()
    dof = np.atleast_1d(dof)
    for i in dof:
        ax.plot(y[i], yd[i], label=str(i))#, **kwargs)
    ax.set_title('Phase space, dof: {}'.format(dof))
    ax.set_xlabel('Displacement (m)')
    ax.set_ylabel('Velocity (m/s)')
    ax.ticklabel_format(axis='both', style='sci', scilimits=(-2,2))
    ax.legend(loc=1)
    # ax.axis('equal')
    return fig, ax

def periodic(t, y, dof=0, ptype='displ', fig=None, ax=None, *args, **kwargs):
    """ To set ptype when used with the plotlist, use:
    from functools import partial
    periodic2 = partial(periodic,ptype='acc')
    """
    if ptype == 'displ':
        ystr = 'Displacement (m)'
    elif ptype == 'vel':
        ystr = 'Velocity (m/s)'
    else:
        ystr = 'Acceleration (m/s²)'

    if fig is None:
        fig, ax = plt.subplots()
        ax.clear()
    dof = np.atleast_1d(dof)
    for i in dof:
        ax.plot(t, y[i], label=r'$x_{{{x}}}$'.format(x=i))#, **kwargs)

    ax.axhline(y=0, ls='--', lw='0.5',color='k')
    ax.set_title('Displacement vs time')
    ax.set_xlabel('Time (t)')
    ax.set_ylabel(ystr)
    # use sci format on y axis when figures are out of the [0.01, 99] bounds
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
    ax.legend()
    return fig, ax

def harmonic(cnorm, dof=0, fig=None, ax=None, *args, **kwargs):
    if fig is None:
        fig, ax = plt.subplots()
        ax.clear()

    dof = np.atleast_1d(dof)
    M = len(dof)
    colors = ['steelblue', 'firebrick', 'darksage', 'goldenrod', 'gray'] * \
        int(M/5. + 1)

    width = 0.25
    alpha = 0.5
    nh = cnorm.shape[1] - 1
    ind = np.arange(nh+1)
    for j, i, color in zip(range(M), dof, colors):
        kwargs = {'width':width, 'color':color, 'label':r'$x_{{{x}}}$'.format(x=i)}
        ax.bar(ind+width*j, cnorm[i], alpha=alpha if j else 1, **kwargs)

    ax.set_xticks(ind+width/M)
    ax.set_xticklabels(ind)
    ax.set_title('Displacement harmonic component, dof: {}'.format(dof))
    ax.set_xlabel('Harmonic index (-)')
    # use double curly braces to "escape" literal curly braces...
    ax.set_ylabel(r'Harmonic coefficient $C_{{{dof}-h}}$'.format(dof=dof))
    ax.set_xlim([-0.5, nh+0.5])
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
    ax.legend()
    return fig, ax

def stability(sigma=None, lamb=None, T=None, ptype='exp', tol=1e-12, fig=None,
              ax=None, *args, **kwargs):
    """ Shows the stability based on either Floquet multipliers(σ) or
    exponents(λ). They are related as σ=e^(λ*T) where T is the period.

    Multipliers are the eigenvalues of the monodromy matrix, ie from the
    shooting method.
    Exponents are the estimated eigenvalues found by Hills matrix, ie from HB.

    To set ptype when used with the plotlist, use:
    from functools import partial
    stability2 = partial(stability,ptype='multipliers')
    """
    if fig is None:
        fig, ax = plt.subplots()
        ax.clear()

    if sigma is None and ptype == 'multipliers':
        # called from HB
        sigma = np.exp(lamb*T)
    if lamb is None and ptype == 'exp':
        # called from NNM/shooting
        lamb = np.log(sigma)/T

    if ptype == 'multipliers':
        str1 = 'Floquet multipliers'
        str2 = '$\sigma$'
        xx = np.real(sigma)
        yy = np.imag(sigma)
        idx_s = np.where(np.abs(sigma) <= 1+tol)
        idx_u = np.where(np.abs(sigma) > 1+tol)

        circ = plt.Circle((0, 0), radius=1, ec='k', fc='None', ls='-')
        ax.add_patch(circ)

    else:
        if T is None:
            raise AttributeError('Period T not provided')
        str1 = 'Floquet exponent'
        str2 = '$\lambda$'
        xx = np.real(lamb)
        yy = np.imag(lamb)
        idx_s = np.where(xx <= 0+tol)
        idx_u = np.where(xx > 0+tol)

        ax.axhline(y=0, color='k')
        ax.axvline(x=0, color='k')

    if len(idx_u[0]) != 0:
        ax.plot(xx[idx_u],yy[idx_u],'ro', mfc='none', label='unstable')#, **kwargs)
    if len(idx_s[0]) != 0:
        ax.plot(xx[idx_s],yy[idx_s],'bx', label='stable')#, **kwargs)
    ax.set_title('Stability ({})'.format(str1))
    ax.set_xlabel(r'Real({})'.format(str2))
    ax.set_ylabel(r'Imag({})'.format(str2))
    ax.legend()

    xmax = max(np.max(np.abs(xx))*1.1, 1.1)
    ymax = max(np.max(np.abs(yy))*1.1, 1.1)
    ax.set_xlim(xmax * np.array([-1,1]))
    ax.set_ylim(ymax * np.array([-1,1]))
    ax.grid(True, which='both')
    if ptype == 'multipliers':
        ax.axis('equal')
    return fig, ax


def configuration(y, fig=None, ax=None, *args, **kwargs):
    if fig is None:
        fig, ax = plt.subplots()
        ax.clear()

    x1 = y[0]
    x2 = y[1]
    ax.plot(x1,x2)
    ax.set_title('Configuration space')
    ax.set_xlabel('Displacement x₁ (m)')
    ax.set_ylabel('Displacement x₂ (m)')
    ax.ticklabel_format(axis='both', style='sci', scilimits=(-2,2))
    ax.axis('equal')
    return fig, ax


class Anim(object):

    def __init__(self, x, y, dof=0, title='', xstr='', ystr='',
                 xmin=None,xmax=None,ymin=None,ymax=None,
                 xscale=1,yscale=1):

        self.dof = dof

        self.xscale = xscale
        self.yscale = yscale
        x = np.asarray(x) * self.xscale
        y = np.asarray(y) * self.yscale

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.clear()
        ax.set_title(title)
        ax.set_xlabel(xstr)
        ax.set_ylabel(ystr)

        scale = 1.5
        if xmin is None:
            xmin = min(x)
            xmin = xmin*scale if xmin < 0 else xmin*(scale-1)
        if xmax is None:
            xmax = max(y)
            xmax = xmax*(scale-1) if xmax < 0 else xmax*scale
        if ymin is None:
            ymin = 0
        if ymax is None:
            ymax = max(y)*1.5
        ax.set_xlim((xmin, xmax))
        ax.set_ylim((ymin,ymax))
        ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))

        plt.show(False)
        fig.canvas.draw()

        # cache the clean background
        self.background = fig.canvas.copy_from_bbox(ax.bbox)
        self.points = ax.plot(x, y, '-')[0]
        self.cur_point = ax.plot(x[-1], y[-1], 'o')[0]
        self.ax = ax
        self.fig = fig
        self.ims = []

    def update(self, x,y):
        """The purpose of blit'ing is to avoid redrawing the axes, and all the ticks
        and, more importantly, avoid redrawing the text, which is relatively
        expensive.

        One way to do it, could be to initialize the axes with limits 50%
        larger than data. When data exceed limits, then redraw and copy
        background
        """

        dof = self.dof
        ax = self.ax
        fig = self.fig

        x = np.asarray(x) * self.xscale
        y = np.asarray(y) * self.yscale

        axes_update = False
        scale = 1.5
        ax_xmin, ax_xmax = ax.get_xlim()
        xmin, xmax = min(x), max(x)
        ax_ymin, ax_ymax = ax.get_ylim()
        ymin, ymax = min(y), max(y)
        if xmin <= ax_xmin:
            xmin = xmin*scale if xmin < 0 else xmin*(scale-1)
        else: xmin = ax_xmin
        if xmax >= ax_xmax:
            xmax = xmax*(scale-1) if xmax < 0 else xmax*scale
        else: xmax = ax_xmax
        if (xmin < ax_xmin or xmax > ax_xmax):
            ax.set_xlim((xmin, xmax))
            axes_update = True

        if ymin <= ax_ymin:
            ymin = ymin*scale if ymin < 0 else ymin*(scale-1)
        else: ymin = ax_ymin
        if ymax >= ax_ymax:
            ymax = ymax*(scale-1) if ymax < 0 else ymax*scale
        else: ymax = ax_ymax
        if (ymin < ax_ymin or ymax > ax_ymax):
            ax.set_ylim((ymin, ymax))
            axes_update = True

        if axes_update:
            fig.canvas.draw()
            self.background = fig.canvas.copy_from_bbox(ax.bbox)
        else:
            # restore the clean slate background
            fig.canvas.restore_region(self.background)

        self.points.set_data(x, y)
        self.cur_point.set_data(x[-1], y[-1])
        # redraw just the points
        ax.draw_artist(self.points)
        ax.draw_artist(self.cur_point)
        # fill in the axes rectangle
        fig.canvas.blit(ax.bbox)

        #self.ims.append([deepcopy(self.points), deepcopy(self.cur_point)])

    def save(self):
        # Set up formatting for the movie files
        Writer = animation.writers['ffmpeg'] # ['imagemagick'] #
        writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)

        #im_ani = animation.ArtistAnimation(self.fig, self.ims, interval=50, repeat_delay=3000,
        #                                   blit=True)
        #im_ani.save('im.mp4', writer=writer)

class PointBrowser(object):
    """
    Click on a point to select and highlight it -- the data that
    generated the point will be shown in the lower axes.  Use the 'n'
    and 'p' keys to browse through the next and previous points

    https://matplotlib.org/examples/event_handling/data_browser.html
    """

    def __init__(self, x, y, dof, plotlist, fig, ax, lines, hb=None, nnm=None,
                 titlestr='', xunit='Hz'):

        if len(plotlist) == 0:
            raise ValueError('MUST: len(plotlist)>0',plotlist)
        x = np.asarray(x)
        y = np.asarray(y)

        if hb is not None:
            self.ptype = 'hb'
        if nnm is not None:
            self.ptype = 'nnm'
        self.nnm = nnm
        self.hb = hb
        self.x = x
        self.y = y
        self.dof = dof
        self.lastind = 0
        self.lastchange = 0

        self.plotlist = plotlist
        self.titlestr = titlestr
        self.xunit = xunit

        # line(s) to select from
        self.lines = lines
        # main/selection plot
        self.fig = fig
        self.ax = ax
        self.selected, = self.ax.plot([self.x[0]], [self.y[0]],
                                      'o', ms=12, alpha=0.4, color='yellow',
                                      visible=False)

        # secondary/info plot
        self.fig2, (self.ax1, self.ax2) = plt.subplots(2,1)
        self.fig2.show(False)

    def onpress(self, event):
        if self.lastind is None:
            return

        inc, change = 0, 0
        if event.key in {'n', 'right'}:
            inc = 1
        elif event.key in {'p', 'left'}:
            inc = -1
        elif event.key in {'a', 'up'}:
            change = 1
        elif event.key in {'z', 'down'}:
            change = -1
        else:
            return

        self.lastchange += 2*change
        self.lastchange = np.clip(self.lastchange, 0, len(self.plotlist) - 2)
        self.lastind += inc
        self.lastind = np.clip(self.lastind, 0, len(self.x) - 1)
        self.update()

    def onpick(self, event):
        # For the moment the plot is made from the Collection object with is
        # not iterable.
        # if event.artist not in self.lines:
        #     return True

        N = len(event.ind)
        if not N:
            return True

        # the click locations
        x = event.mouseevent.xdata
        y = event.mouseevent.ydata

        distances = np.hypot(x - self.x[event.ind],
                             y - self.y[event.ind])
        indmin = distances.argmin()
        dataind = event.ind[indmin]

        self.lastind = dataind
        self.update()

    def update(self):
        if self.lastind is None:
            return

        plotind = self.lastchange
        dataind = self.lastind

        try:
            if not plt.fignum_exists(self.fig2.number):
                self.fig2, (self.ax1, self.ax2) = plt.subplots(2,1)
        except AttributeError:  # NameError:
            pass
            #plt.show()
        plotdata = {}
        if self.ptype == 'hb':
            omega = self.hb.omega_vec[dataind]
            omega2 = omega / self.hb.nu
            #t = self.hb.assemblet(omega2)
            z = self.hb.z_vec[dataind]
            t, omegap, zp, cnorm, c, cd, cdd = \
                self.hb.get_components(omega, z)
            lamb = self.hb.lamb_vec[dataind]
            sigma = None
            x = hb_signal(omega, t, *c)
            xd = hb_signal(omega, t, *cd)
            xdd = hb_signal(omega, t, *cdd)
            T = t[-1]

            plotdata.update({'cnorm':cnorm})
            titlestr = '{}\nFreq {:g}{}, Amplitude {:g}(m)'.\
                format(self.titlestr, omega, self.xunit, self.y[dataind])

        elif self.ptype == 'nnm':
            X0 = self.nnm.X0_vec[dataind]
            n = len(X0)
            x0 = X0[:n//2]
            xd0 = X0[n//2:n]
            T = 2*np.pi / self.nnm.omega_vec[dataind]
            dt = T / self.nnm.nppp
            # We want one complete period.
            ns = self.nnm.nppp + 1
            t = np.arange(ns)*dt
            fext = np.zeros(ns)
            x, xd, xdd, Phi = self.nnm.newmark.integrate_nl(x0, xd0, dt, fext,
                                                            sensitivity=True)
            sigma = eigvals(Phi)
            lamb = None
            # change to 'tol':self.nnm.tol_stability on next update
            plotdata.update({'tol':1e-3})
            titlestr = '{}\nFreq {:g}{}, Energy {:g}(log10(J))'.\
                format(self.titlestr, 1/T*2*np.pi, self.xunit, self.x[dataind])

        plotdata.update({'t': t, 'y':x, 'yd':xd, 'ydd':xdd, 'dof':self.dof,
                         'T':T, 'sigma':sigma, 'lamb':lamb})

        self.ax1.clear()
        self.ax2.clear()
        # need to set aspect ratio to auto manual. It is set to equal in
        # stability and clearing the axes does apparently not set the scaling
        # back to auto.
        self.ax1.axis('auto')
        self.ax2.axis('auto')
        plot0 = self.plotlist[plotind]
        plot1 = self.plotlist[plotind+1]
        # for plot1, plot2 in zip(plotlist[:-1], plotlist[1:]):
        plot0(**plotdata, fig=self.fig2, ax=self.ax1)
        plot1(**plotdata, fig=self.fig2, ax=self.ax2)
        self.selected.set_visible(True)
        self.selected.set_data(self.x[dataind], self.y[dataind])
        self.ax.set_title(titlestr)

        self.fig.canvas.draw()
        self.fig2.tight_layout()
        self.fig2.canvas.draw()


def nfrc(dof=0, pdof=0, plotlist=[], hb=None, nnm=None, energy_plot=False,
         interactive=True, detect=True,
         xscale=1/2/np.pi, yscale=1, xunit='(Hz)',
         fig=None, ax=None, *args, **kwargs):

    if fig is None:
        fig, ax = plt.subplots()
        ax.clear()

    if hb is not None:
        ptype = 'hb'
        stab_vec = hb.stab_vec
        x = np.asarray(hb.omega_vec)/hb.scale_t * xscale
        y = np.asarray(hb.xamp_vec).T[dof]
        titlestr = 'Nonlinear FRF for dof {}'.format(dof)
        ystr = 'Amplitude (m)'
        xstr = 'Frequency ' + xunit
        if detect:
            for bif in hb.bif:
                bifargs = {'ls':'None','mfc':'None','marker':bif.marker,'label':bif.stype}
                ax.plot(x[bif.idx[1:]], y[bif.idx[1:]], **bifargs)
        ax.legend()
    if nnm is not None:
        ptype = 'nnm'
        stab_vec = nnm.stab_vec
        if energy_plot:
            energy = np.asarray(nnm.energy_vec)#.T[dof]
            x = np.log10(energy)
            y = np.asarray(nnm.omega_vec) * xscale  # / 2/np.pi
            titlestr = 'Frequency Energy plot (FEP)'
            xstr = 'Log10(Energy) (J)'
            ystr = 'Frequency ' + xunit
        else:
            x = np.asarray(nnm.omega_vec) * xscale
            y = np.asarray(nnm.xamp_vec).T[dof]
            titlestr = 'Amplitude of dof {}'.format(dof)
            ystr = 'Amplitude (m)'
            xstr = 'Frequency ' + xunit


    ax.set_title(titlestr)
    ax.set_xlabel(xstr)
    ax.set_ylabel(ystr)
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))

    # picker: 5 points tolerance
    stab_vec = np.array(stab_vec)
    # idx1 = ~stab_vec
    # idx2 = stab_vec
    # l1 = ax.plot(np.ma.masked_where(idx1, x), np.ma.masked_where(idx1, y),
    #              '-k',ms=1, picker=5, **kwargs)
    # kwargs.pop('label', None)
    # l2 = ax.plot(np.ma.masked_where(idx2, x), np.ma.masked_where(idx2, y),
    #              '--k', ms=1, picker=5, **kwargs)
    # lines = l1 + l2

    from matplotlib.collections import LineCollection
    from matplotlib.lines import Line2D
    # set up colors and line styles
    ls = ['-' if s else '--' for s in stab_vec]
    c = ['k' if s else 'r' for s in stab_vec]
    # convert time series to line segments
    lines = [((x0,y0), (x1,y1)) for x0, y0, x1, y1 in zip(x[:-1], y[:-1], x[1:], y[1:])]
    colored_lines = LineCollection(lines, colors=c, linestyles=ls, linewidths=(2,), picker=5)
    ax.add_collection(colored_lines)
    ax.autoscale_view()
    lines = colored_lines

    def make_proxy(zvalue, scalar_mappable, **kwargs):
        return Line2D([0, 1], [0, 1], **kwargs)
    proxies = [make_proxy(item, lines, linewidth=5) for item in [0]]
    label = kwargs.get('label')
    ax.legend(proxies, [label])

    if interactive:
        browser = PointBrowser(x, y, pdof, plotlist, fig, ax, lines, hb=hb,
                               nnm=nnm, titlestr=titlestr, xunit=xunit)

        fig.canvas.mpl_connect('pick_event', browser.onpick)
        fig.canvas.mpl_connect('key_press_event', browser.onpress)

        plt.show()

    return fig, ax

