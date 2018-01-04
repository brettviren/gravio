#!/usr/bin/env python

# throughput of one ASIC in Gbps
asictp = 16* 2e6 * 12 / 1e9
# throughput of one FEMB
fembtp = 8 * asictp
# throughput of one entire APA face
facetp = 10 * fembtp

def subgraph_color(part):
    '''
    This function encapsulates my inability to pick nice colors.

    https://graphviz.gitlab.io/_pages/doc/info/colors.html
    '''
    scheme = '/bupu6/'
    if part.startswith("wib"):
        part = "wib"
    if part.startswith("rce"):
        part = "rce"
    ranks = dict(apa=1, face=2, femb=3, wib=4, rce=5, felix=6)
    num = ranks.get(part, 1)
    return scheme + str(num)

def edge_style(part='', **kwds):
    '''
    Return a new dictionary which adds style attributes
    '''
    linktp = kwds.get('linktp', 0.0)
    penwidth = int(linktp/asictp)
    #penwidth = min(penwidth, 40)


    d = dict(color='black', style='solid', penwidth=penwidth)

    for k,v in d.items():
        kwds.setdefault(k,v)

    return kwds


def node_shape(part):
    special = dict(tx='hexagon', mx='hexagon', rx='hexagon',
                   fpga='octagon',
                   conn='circle', uplink='circle', bundle='circle',
                   cable='circle', fiber='circle', link='circle')
    return special.get(part, 'box')

def subctx(ctx, part, ident=''):
    return "%s_%s%s" % (ctx, part, ident)

# Make a dressed subgraph
def subgraph(g, part='', ident='', label='', **kwds):
    '''
    Create a subgraph in graph g and context ctx made unique by name
    "part" and identififer 'ident".  
    '''
    ctx = subctx(g.name, part, ident)
    sg = g.subgraph(ctx, label=label, color=subgraph_color(part), **kwds)
    if part:
        sg.attr['part'] = part
    if ident is not None and ident is not '':
        sg.attr['ident'] = ident
    return sg

# Make a dressed node
#
def node(g, part, ident='', label="", **kwds):
    ctx = subctx(g.name, part, ident)
    n = g.node(ctx, label=label, **kwds)
    # fixme: make node_shape into node_style and work like edge_style
    n.attr.setdefault('shape', node_shape(part))
    if part:
        n.attr['part'] = part
    if ident is not None and ident is not '':
        n.attr['ident'] = ident
    return n

# Make a dressed edge
#
def edge(g, tail, head, part='', reverse=False, **kwds):
    params = edge_style(part=part, reverse=reverse, **kwds)
    if reverse:
        tail, head = head, tail
        params.setdefault('dir', 'back')
    return g.edge(tail, head, **params)


def zipup(g, upstream, downstream, part='', reverse=False, **kwds):
    for u,d in zip(upstream, downstream):
        edge(g, u,d, part, reverse, **kwds)


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
        edge(sg, fe, adc, 'asic', reverse, linktp=asictp)

    for ind,adc in enumerate(adcs):
        tx = txs[ind//2]
        edge(sg, adc, tx, 'asictx', reverse, linktp=asictp)
    for tx in txs:
        edge(sg, tx, cable, 'asiclink', reverse, linktp=nasics*asictp/ntxs)

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
        edge(sg, wc, mx, 'asiclink', reverse, linktp=fembtp)

    fibertp = facetp/(len(fibers)*len(mxs))

    for ind, fiber in enumerate(fibers):
        iwib = ind//nfibersperwf
        mx = mxs[iwib]
        edge(sg, mx, fiber, 'fiber', reverse, linktp=facetp/len(fibers))

        # fixme: the math below is wrong when just felix is used so just punt
        if len(fibers) == len(bundles):
            edge(sg, fiber, bundles[ind], 'bundle', reverse, linktp=facetp/len(bundles))
            continue

        ibundle = iwib*2 + ind%nbundlesperwf
        bundle = bundles[ibundle]
        edge(sg, fiber, bundle, 'bundle', reverse, linktp=facetp/len(fibers))
        

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

    fibertp = facetp/(nfibersperrce*nrce)
    uplinktp = facetp/(nlinksperrce*nrce)

    for ifiber, fiber in enumerate(fibers):
        rce = rces[ifiber//nfibersperrce]
        edge(sg, fiber, rce, 'fiber', reverse, linktp=fibertp)

    for rce, fpga, tx in zip(rces, fpgas, txs):
        edge(sg, rce, fpga, 'rcelink', reverse, linktp=facetp/nrce)
        edge(sg, fpga, tx, 'rcelink', reverse, linktp=facetp/nrce)

    for ilink, link in enumerate(links):
        tx = txs[ilink//nlinksperrce]
        edge(sg, tx, link, 'link', reverse, linktp=uplinktp)

    return (fibers, links)

def felixface(g, iface, nlinks=5, reverse=False): # nlinks=10 for rce
    sg = subgraph(g, 'felixface', iface, 'Felix FACE %d' % iface)

    glinks = subgraph(sg, 'links', iface, 'links')
    links = [node(glinks, 'link', ind, 'link%d'%ind) for ind in range(nlinks)]

    rx = node(sg, 'rx', iface, 'rx')

    linktp = facetp/nlinks
    for link in links:
        edge(sg, link, rx, 'link', reverse=reverse, linktp=linktp)
    return (links, (rx,))

def felixhost(g):
    sg = subgraph(g, 'felixhost', label='FELIX Host')
    fpga = node(sg, 'fpga', label='FPGA')
    ram = node(sg, 'ram', label='RAM')
    edge(sg, fpga, ram, constraint=False, linktp = 2*facetp, dir='none')
    return ((fpga,), (ram,))


def zip_wib_rce(g, wibconns, rces, part='bundle', reverse=False, **kwds):
    '''
    Zip up the output WIB face nodes to input RCE nodes
    
    There should be one WIB face node for each (wib,conn) pair.

    There should be one RCE node for each con
    '''
    nrces = len(rces)
    linktp = facetp/len(wibconns)
    for ind,wibconn in enumerate(wibconns):
        rce = rces[ind%nrces]
        edge(g, wibconn, rce, part=part, reverse=reverse, linktp=linktp, label="4 fibers", **kwds)

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

        zipup(g, fes, wf[0], 'cable', reverse = iface==0, linktp=facetp/len(wf[0]))
        zipup(g, wf[1], fel[0], 'bundle', reverse = iface==0, linktp=facetp/len(wf[1]))
        backends.append(fel[1])

    fh = felixhost(gfelix)
    edge(gfelix, backends[0][0], fh[0][0], reverse=True, linktp=facetp, dir='none')
    edge(gfelix, backends[1][0], fh[0][0], reverse=False, linktp=facetp, dir='none')

    
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

        zipup(g, fes, wf[0], 'cable', reverse = iface==0, label="4 fibers", linktp=facetp/len(wf[0]))
        zip_wib_rce(g, wf[1], rf[0], reverse = iface==0)
        zipup(g, rf[1], fel[0], reverse = iface==0, linktp=facetp/len(fel[0]))
        backends.append(fel[1])

    fh = felixhost(gfelix)
    edge(gfelix, backends[0][0], fh[0][0], reverse=True, linktp=facetp, dir='none')
    edge(gfelix, backends[1][0], fh[0][0], reverse=False, linktp=facetp, dir='none')


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
