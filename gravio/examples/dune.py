#!/usr/bin/env python

def subgraph_color(what):
    '''
    This function encapsulates my inability to pick nice colors.

    https://graphviz.gitlab.io/_pages/doc/info/colors.html
    '''
    scheme = '/bupu6/'
    if what.startswith("wib"):
        what = "wib"
    ranks = dict(apa=1, face=2, femb=3, wib=4, rce=5, felix=6)
    num = ranks.get(what, 1)
    return scheme + str(num)

def edge_style(what):
    widths = dict(asic=1, asictx=2, asiclink=4)
    d = dict(color='black', style='solid',
             penwidth=widths.get(what, 1))
    return d


def node_shape(what):
    special = dict(tx='hexagon', mx='hexagon', rx='hexagon',
                   fpga='octagon',
                   conn='circle', uplink='circle', bundle='circle',
                   cable='circle', fiber='circle', link='circle')
    return special.get(what, 'box')

def subctx(ctx, what, ident=''):
    return "%s_%s%s" % (ctx, what, ident)

# Make a dressed subgraph
def subgraph(g, what='', ident='', label='', **kwds):
    '''
    Create a subgraph in graph g and context ctx made unique by name
    "what" and identififer 'ident".  
    '''
    ctx = subctx(g.name, what, ident)
    sg = g.subgraph(ctx, label=label, color=subgraph_color(what), **kwds)
    if what:
        sg.attr['part'] = what
    if ident is not None and ident is not '':
        sg.attr['ident'] = ident
    return sg

# Make a dressed node
#
def node(g, what, ident='', label="", **kwds):
    ctx = subctx(g.name, what, ident)
    n = g.node(ctx, label=label,
               shape = node_shape(what), **kwds)
    if what:
        n.attr['part'] = what
    if ident is not None and ident is not '':
        n.attr['ident'] = ident
    return n

# Make a dressed edge
#
def edge(g, tail, head, what='', reverse=False, **kwds):
    params = edge_style(what)
    if reverse:
        tail, head = head, tail
        params['dir']='back'
    params.update(**kwds)
    return g.edge(tail, head, **params)


def zipup(g, upstream, downstream, what='', reverse=False, **kwds):
    for u,d in zip(upstream, downstream):
        edge(g, u,d, what, reverse, **kwds)


def femb(g, ident, nasics=8, ntxs=4, reverse=False):
    '''
    Make one FEMB and return tuple of (fes, cables)
    '''

    sg = subgraph(g, 'femb', ident, 'FEMB%02d'%ident)

    cable = node(sg, 'cable', label='cable')

    gfe = subgraph(sg, 'fes')
    fes = [node(gfe, 'fe', ind, 'FE%d'%ind) for ind in range(nasics)]

    gadc = subgraph(sg, 'adcs')
    adcs = [node(gfe, 'adc', ind, 'ADC%d'%ind) for ind in range(nasics)]

    gtx = subgraph(sg, 'txs')
    txs = [node(gtx, 'tx', ind, 'tx%d'%ind) for ind in range(ntxs)]

    for fe, adc in zip(fes, adcs):
        edge(sg, fe, adc, 'asic', reverse)

    for ind,adc in enumerate(adcs):
        tx = txs[ind//2]
        edge(sg, adc, tx, 'asictx', reverse)
    for tx in txs:
        edge(sg, tx, cable, 'asiclink', reverse)

    return (fes, (cable,))


def wibface(g, iface, reverse=False,
            nfibersperwf=1, nbundlesperwf=1, nwibs=5, nconns=2):
    '''
    Make a "WIB face" which is 1/2 of the connectors of all WIBs which
    are servicing one APA face.
    '''
    sg = subgraph(g, 'wibface', iface, 'WIB Face %d' % iface)

    iconns = range(iface*nconns, (iface+1)*nconns)
    gconns = [subgraph(sg, 'wibconns', ind, 'WIB conns #%d'%ind) for ind in iconns]
    gmx = subgraph(sg, 'wibmxs')
    gfiber = subgraph(sg, 'wibfibers')
    gbundle = subgraph(sg, 'wibbundle')

    conns = list()
    for iconn, gconn in zip(iconns, gconns):
        for iwib in range(nwibs):
            lab = 'WIB%d\nconn%d'%(iwib, iconn)
            n = node(gconn, 'conn', iwib, lab)
            conns.append(n)

    mxs = list()
    for iwib in range(nwibs):
        n = node(gmx, 'mx', iwib, 'WIB %d\nrx/mx/tx'%iwib)
        mxs.append(n)

    fibers = list()
    for iwib in range(nwibs):
        for ifiber in range(nfibersperwf):
            ident_fiber = iwib * nfibersperwf + ifiber
            n = node(gfiber, 'fiber', ident_fiber,
                     label='WIB %d\nfiber%d'%(iwib, ifiber))
            fibers.append(n)

    #nfibersperwf=8, nbundlesperwf=2
    bundles=list()
    for iwib in range(nwibs):
        for ibundle in range(nbundlesperwf):
            ident = iwib*nbundlesperwf + ibundle
            n = node(gbundle, 'bundle', ident,
                     label='WIB%d\nBundle%d'%(iwib, ibundle))
            bundles.append(n)

    for ind, wc in enumerate(conns):
        mx = mxs[ind%nwibs]
        edge(sg, wc, mx, 'asiclink', reverse)

    for ind, fiber in enumerate(fibers):
        iwib = ind//nfibersperwf
        mx = mxs[iwib]
        edge(sg, mx, fiber, 'fiber', reverse)

        # fixme: the math below is wrong when just felix is used
        if len(fibers) == len(bundles):
            edge(sg, fiber, bundles[ind], 'bundle', reverse)
            continue

        ibundle = iwib*2 + ind%nbundlesperwf
        bundle = bundles[ibundle]
        edge(sg, fiber, bundle, 'bundle', reverse)
        

    return (conns, bundles)
        


def rceface(g, iface, nrce=2, nfibersperrce=5, nlinksperrce=5, reverse=False):
    '''
    Produce one RCE fragment servicing the APA face
    '''
    sg = subgraph(g, 'rceface', iface, 'RCE Face %d' % iface)

    gfiber = subgraph(sg, "fiber", iface, 'fibers')
    grce = subgraph(sg, 'rcefes', iface, 'FEs')
    gfpga = subgraph(sg, 'rcefpgas', iface, 'FPGAs')
    gtx = subgraph(sg, 'rcetx', iface, 'tx')
    gup = subgraph(sg, 'rceups', iface, 'Uplinks')

    ifibers = range(nrce * nfibersperrce)
    fibers = [node(gfiber, 'fiber', ind, label='fiber%02d'%ind) for ind in ifibers]
    irces = range(iface*nrce, (iface+1)*nrce)
    rces = [node(grce, 'rce', ind, label='RCE%d'%ind) for ind in irces]
    fpgas = [node(gfpga, 'fpga', ind, label='FPGA') for ind in irces]
    txs = [node(gtx, 'tx', ind, label='tx') for ind in irces]
    iups = range(nlinksperrce * nrce)
    links = [node(gup, 'uplink', ind, label='uplink') for ind in iups]

    for ifiber, fiber in enumerate(fibers):
        rce = rces[ifiber//nfibersperrce]
        edge(sg, fiber, rce, 'fiber', reverse)

    for rce, fpga, tx in zip(rces, fpgas, txs):
        edge(sg, rce, fpga, 'rcelink', reverse)
        edge(sg, fpga, tx, 'rcelink', reverse)

    for ilink, link in enumerate(links):
        tx = txs[ilink//nlinksperrce]
        edge(sg, tx, link, 'link', reverse)

    return (fibers, links)

def felixface(g, iface, nlinks=5, reverse=False): # nlinks=10 for rce
    sg = subgraph(g, 'felixface', iface, 'Felix FACE %d' % iface)

    glinks = subgraph(sg, 'links', iface, 'links')
    links = [node(glinks, 'link', ind, 'link%d'%ind) for ind in range(nlinks)]

    rx = node(sg, 'rx', iface, 'rx')

    for link in links:
        edge(sg, link, rx, 'link', reverse=reverse)
    return (links, (rx,))

def felixhost(g):
    sg = subgraph(g, 'felixhost', label='FELIX Host')
    fpga = node(sg, 'fpga', label='FPGA')
    pcie = node(sg, 'pcie', label='PCIe')
    edge(sg, fpga, pcie, constraint=False)
    return ((fpga,), (pcie,))


def zip_wib_rce(g, wibconns, rces, what='bundle', reverse=False, **kwds):
    '''
    Zip up the output WIB face nodes to input RCE nodes
    
    There should be one WIB face node for each (wib,conn) pair.

    There should be one RCE node for each con
    '''
    nrces = len(rces)
    for ind,wibconn in enumerate(wibconns):
        rce = rces[ind%nrces]
        edge(g, wibconn, rce, what=what, reverse=reverse, **kwds)

def main_felix(g):
    gdaq = subgraph(g, 'daq', label='RCE')
    gfelix = subgraph(gdaq, 'felix', label='FELIX')

    backends = list()

    for iface in [0,1]:
        fes = list()
        for ident in range(iface*10, (iface+1)*10):
            _, cabs = femb(gdaq, ident, reverse = iface==0)
            fes.append(cabs[0])
        wf = wibface(gdaq, iface, nfibersperwf=1, nbundlesperwf=1,
                     reverse = iface==0)
        fel = felixface(gfelix, iface, nlinks=5, reverse = iface==0)

        zipup(g, fes, wf[0], 'cable', reverse = iface==0)
        zipup(g, wf[1], fel[0], reverse = iface==0)
        backends.append(fel[1])

    fh = felixhost(gfelix)
    edge(gfelix, backends[0][0], fh[0][0], reverse=True)
    edge(gfelix, backends[1][0], fh[0][0], reverse=False)

    
def main_rce_felix(g):
    gdaq = subgraph(g, 'daq', label='RCE')
    gfelix = subgraph(gdaq, 'felix', label='FELIX')

    backends = list()

    for iface in [0,1]:
        fes = list()
        for ident in range(iface*10, (iface+1)*10):
            _, cabs = femb(gdaq, ident, reverse = iface==0)
            fes.append(cabs[0])
        wf = wibface(gdaq, iface, nfibersperwf=8, nbundlesperwf=2, reverse = iface==0)
        rf = rceface(gdaq, iface, reverse = iface==0)

        fel = felixface(gfelix, iface, nlinks=10, reverse = iface==0)

        zipup(g, fes, wf[0], 'cable', reverse = iface==0)
        zip_wib_rce(g, wf[1], rf[0], reverse = iface==0)
        zipup(g, rf[1], fel[0], reverse = iface==0)
        backends.append(fel[1])

    fh = felixhost(gfelix)
    edge(gfelix, backends[0][0], fh[0][0], reverse=True)
    edge(gfelix, backends[1][0], fh[0][0], reverse=False)


def main(which = "felix"):
    from gravio import gen
    g = gen.Graph("dune", "digraph", label="DUNE",
                  nodesep='.1', ranksep='2',
                  rankdir='LR', style="filled", color='white')

    if which == "felix":
        main_felix(g)
    if which == "rce_felix":
        main_rce_felix(g)
    return g
