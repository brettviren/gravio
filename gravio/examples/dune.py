#!/usr/bin/env python

import numpy

# throughput of one ASIC in Gbps
asictp = 16* 2e6 * 12 / 1e9
# throughput of one FEMB
fembtp = 8 * asictp
# throughput of one entire APA face
facetp = 10 * fembtp

def part_color(part):
    scheme = '/bupu6/'
    ranks = dict(apa=1, face=2, femb=3, wib=4, rce=5, felix=6)
    num = ranks.get(part, 1)
    return scheme + str(num)

def subgraph_color(part):
    '''
    This function encapsulates my inability to pick nice colors.

    https://graphviz.gitlab.io/_pages/doc/info/colors.html
    '''

    if part == 'wibbundle':
        return 'white'
    if part == 'wibconns':
        return 'white'
    if part == 'wibface':
        return 'cornsilk3'
    if part.startswith("wib"):
        part = "wib"

    if part == 'rce':
        return 'white'
    if part.startswith('rce'):
        part = 'rce'

    return part_color(part)

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
    kwds.setdefault('color', subgraph_color(part))
    sg = g.subgraph(ctx, label=label, **kwds)
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

    cable = node(sg, 'cable', label='Cable Bundle\n(%d wires)'%ntxs)

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
            # total number of incoming cold conductors entering the wibface
            nconductors = 40,
            # total number of outgoing fibers leaving the wibface
            nfibers = 5,
            # total number of outgoing fiber bundles leaving the wibface
            nbundles = 5, 
            # number of wibs participating (partly) in the wibface
            nwibs=5,
            # number of connectors on these wibs servicing this wibface
            nconns=2):
    '''
    Make a "WIB face" which is 1/2 of the connectors of all WIBs which
    are servicing one APA face.
    '''

    nbundlesperwib=nbundles//nwibs
    nfibersperbundle = nfibers//nbundles
    nconductorsperconnector = nconductors//(nwibs*nconns)

    sg = subgraph(g, 'wibface', iface, 'WIB (APA face %d)' % iface)

    iconns = range(iface*nconns, (iface+1)*nconns)
    gconns = [subgraph(sg, 'wibconns', ind, 'Connectors #%d'%ind, ordering='out') for ind in iconns]
    gmx = subgraph(sg, 'wibmxs', ordering='out')
    # gfiber = subgraph(sg, 'wibfibers')
    gbundle = subgraph(sg, 'wibbundle', ordering='out')

    conns = list()
    for iconn, gconn in zip(iconns, gconns):
        for iwib in range(nwibs):
            lab = 'WIB %d\nConnector %d'%(iwib, iconn)
            n = node(gconn, 'conn', iwib, lab)
            conns.append(n)

    mxs = list()
    for iwib in range(nwibs):
        n = node(gmx, 'mx', iwib, 'WIB %d\nrx/mx/tx'%iwib)
        mxs.append(n)

    #for mx1, mx2 in zip(mxs[:-1], mxs[1:]):
    #    edge(gmx, mx1, mx2, weight=2) # force ordering

    # fibers = list()
    # for iwib in range(nwibs):
    #     for ifiber in range(nfibersperwf):
    #         ident_fiber = iwib * nfibersperwf + ifiber
    #         n = node(gfiber, 'fiber', ident_fiber,
    #                  label='WIB %d\nfiber%d'%(iwib, ifiber))
    #         fibers.append(n)


    bundles = list()
    for iwib in range(nwibs):
        for ibundle in range(nbundlesperwib):
            ident = iwib*nbundlesperwib + ibundle
            b = node(gbundle, 'bundle', ident,
                     label='WIB%d\nBundle %d\n(%dx fibers)'%(iwib, ident, nfibersperbundle))
            bundles.append(b)

    condtp = facetp/nconductors
    for ind, wc in enumerate(conns):
        mx = mxs[ind%nwibs]
        for icond in range(nconductorsperconnector):
            edge(sg, wc, mx, 'asiclink', reverse, linktp=condtp)

    fibertp = facetp/nfibers
    for iwib in range(nwibs):
        mx = mxs[iwib]
        for ibundle in range(nbundlesperwib):
            ident = iwib*nbundlesperwib + ibundle
            bundle = bundles[ident]
            for ifiber in range(nfibersperbundle):
                edge(sg, mx, bundle, 'fiber', reverse, linktp = fibertp)

    # for ind, fiber in enumerate(fibers):
    #     iwib = ind//nfibersperwf
    #     mx = mxs[iwib]
    #     edge(sg, mx, fiber, 'fiber', reverse, linktp=facetp/len(fibers))

    #     # fixme: the math below is wrong when just felix is used so just punt
    #     if len(fibers) == len(bundles):
    #         edge(sg, fiber, bundles[ind], 'bundle', reverse, linktp=facetp/len(bundles))
    #         continue

    #     ibundle = iwib*2 + ind%nbundlesperwf
    #     bundle = bundles[ibundle]
    #     edge(sg, fiber, bundle, 'bundle', reverse, linktp=facetp/len(fibers))
        

    return (conns, bundles)
        
def wibface2(g, iface, reverse=False,
            # total number of incoming cold conductors entering the wibface
            nconductors = 40,
            # total number of outgoing fibers leaving the wibface
            nfibers = 5,
            # total number of outgoing fiber bundles leaving the wibface
            nbundles = 5, 
            # number of wibs participating (partly) in the wibface
            nwibs=5,
            # number of connectors on these wibs servicing this wibface
            nconns=2):
    '''
    Make a "WIB face" which is 1/2 of the connectors of all WIBs which
    are servicing one APA face.
    '''

    nbundlesperwib=nbundles//nwibs
    nfibersperbundle = nfibers//nbundles
    nconductorsperconnector = nconductors//(nwibs*nconns)

    sg = subgraph(g, 'wibface', iface, 'WIB (APA face %d)' % iface)

    gwibs = list()
    conns = list()
    mxs = list()
    bundles = list()

    for iwib in range(nwibs):
        gwib = subgraph(sg, 'wibhalf', iwib, 'WIB %d (APA face %d)'%(iwib, iface))

        gconn = subgraph(gwib, 'wibconns', iwib, 'Connectors for half WIB #%d'%iwib)
        for iconn in range(iface*nconns, (iface+1)*nconns):
            lab = 'WIB %d\nConnector %d'%(iwib, iconn)
            ident = iconn*nwibs + iwib
            n = node(gconn, 'conn', ident, lab)
            conns.append(n)
            
        gmx = subgraph(gwib, 'wibmx')
        mx = node(gmx, 'mx', iwib, 'WIB %d\nrx/mx/tx'%iwib)
        mxs.append(mx)

        gbundle = subgraph(gwib, 'wibbundle', iwib, 'Fiber Bundles')
        for ibundle in range(nbundlesperwib):
            ident = iwib*nbundlesperwib + ibundle
            iconn = ibundle%nbundlesperwib
            bunnum = iface*nconns + iconn
            b = node(gbundle, 'bundle', ident,
                     label='WIB%d\nBundle %d\n(%dx fibers)'%(iwib, bunnum, nfibersperbundle))
            bundles.append(b)
    conns.sort(key=lambda c: c.attr['ident'])


    condtp = facetp/nconductors
    for ind, wc in enumerate(conns):
        mx = mxs[ind%nwibs]
        for icond in range(nconductorsperconnector):
            edge(sg, wc, mx, 'asiclink', reverse, linktp=condtp)

    fibertp = facetp/nfibers
    for iwib in range(nwibs):
        mx = mxs[iwib]
        for ibundle in range(nbundlesperwib):
            ident = iwib*nbundlesperwib + ibundle
            bundle = bundles[ident]
            for ifiber in range(nfibersperbundle):
                edge(sg, mx, bundle, 'fiber', reverse, linktp = fibertp)

    # for ind, fiber in enumerate(fibers):
    #     iwib = ind//nfibersperwf
    #     mx = mxs[iwib]
    #     edge(sg, mx, fiber, 'fiber', reverse, linktp=facetp/len(fibers))

    #     # fixme: the math below is wrong when just felix is used so just punt
    #     if len(fibers) == len(bundles):
    #         edge(sg, fiber, bundles[ind], 'bundle', reverse, linktp=facetp/len(bundles))
    #         continue

    #     ibundle = iwib*2 + ind%nbundlesperwf
    #     bundle = bundles[ibundle]
    #     edge(sg, fiber, bundle, 'bundle', reverse, linktp=facetp/len(fibers))
        

    return (conns, bundles)
        


def rceface(g, iface, nrce=2, nfpga=2, nbundles_in=10, nfibers_in=40, nbundles_out=4, nfibers_out=8, reverse=False):
    '''
    Produce one RCE fragment servicing one WIB-face
    '''
    sg = subgraph(g, 'rceface', iface, 'RCE (APA face %d)' % iface)

    grtm_in = subgraph(sg, 'rtmin', iface, 'RTM-face\nHalf-input\n(optical to electrical)')

    grtm_out = subgraph(sg, 'rtmout', iface, 'RTM-face\nHalf-output\n(electrical to optical)')

    grces = list()
    for irce in range(nrce):
        grce = subgraph(sg, 'rce', iface*nrce + irce, 'RCE %d'%(nrce*iface + irce))
        grces.append(grce)

    bundles_in = list()
    nbundleperrce = nbundles_in // nrce
    for irce in range(nrce):
        gb = subgraph(grtm_in, 'rtmrce', iface*nrce+irce)
        for ibundle in range(nbundleperrce):
            ident = irce*nbundleperrce + ibundle
            n = node(gb, 'bundle', ident, lable='bundle')
            bundles_in.append(n)
        
    bundles_out = list()
    for ibundle in range(nbundles_out):
        n = node(grtm_out, 'bundle', ibundle, lable='bundle')
        bundles_out.append(n)

    nfpgasperrce = nfpga//nrce
    fpgas = list()
    for irce, grce in enumerate(grces):
        for ifpga in range(nfpgasperrce):
            fpga = node(grce, 'rce', irce*nfpgasperrce + ifpga, label='FPGA')
            fpgas.append(fpga)

    fibertp = facetp/nfibers_in
    nfibersperbundle = nfibers_in // nbundles_in
    nbundlesperfpga = nbundles_in // nfpga
    for ifpga,fpga in enumerate(fpgas):
        for ibundle in range(nbundlesperfpga):
            bundle = bundles_in[ifpga*nbundlesperfpga + ibundle]
            for ifiber in range(nfibersperbundle):
                edge(sg, bundle, fpga, 'fiber', reverse, linktp=fibertp)

    fibertp = facetp/nfibers_out
    nfibersperbundle = nfibers_out // nbundles_out
    nbundlesperfpga = nbundles_out // nfpga
    for ifpga,fpga in enumerate(fpgas):
        for ibundle in range(nbundlesperfpga):
            bundle = bundles_out[ifpga*nbundlesperfpga + ibundle]
            for ifiber in range(nfibersperbundle):
                edge(sg, fpga, bundle, 'fiber', reverse, linktp=fibertp)

    # nfibersperbundle = nfibers//nbundles
    # nbundlesperrtm = nbundles//nrce
    # for ibundle, bundle in enumerate(bundles):
    #     for ifiber in range(nfibersperbundle):
    #         edge(sg, bundle, rtm, 'fiber', reverse, linktp=fibertp)

    # for ifpga, fpga in enumerate(fpgas):
    #     ntraces = nfibersperbundle*nbundles//nrce
    #     for ifiber in range(ntraces):
    #         edge(sg, rtm, fpga, 'fiber', reverse, linktp=fibertp, dir='both')

    # for up in upbundles:
    #     edge(sg, rtm, up, 'upbundle', reverse, linktp = facetp//len(upbundles))

    return (bundles_in, bundles_out)


def felixface(g, iface, nlinks=4, reverse=False): # nlinks=10 for rce
    sg = subgraph(g, 'felixface', iface, 'Felix FACE %d' % iface)

    glinks = subgraph(sg, 'links', iface, 'links')
    links = [node(glinks, 'link', ind, 'link%d'%ind) for ind in range(nlinks)]

    rx = node(sg, 'rx', iface, '\nrx\n\n')

    linktp = facetp/nlinks
    for link in links:
        edge(sg, link, rx, 'link', reverse=reverse, linktp=linktp, dir='none')
    return (links, (rx,))

def felixhost(g):
    sg = subgraph(g, 'felixhost', label='FELIX Host')
    fpga = node(sg, 'fpga', label='FPGA')
    ram = node(sg, 'ram', label='RAM')
    edge(sg, fpga, ram, constraint=False, linktp = 2*facetp, dir='none')
    return ((fpga,), (ram,))


def zipup_transpose(g, inputs, outputs, part='bundle', reverse=False, shape=(2,5), **kwds):
    '''
    Connect inputs to outputs assuming a transpose in major ordering and given stride.
    '''
    indices_in = range(len(inputs))
    indices_out = numpy.asarray(indices_in).reshape(shape).T.flatten().tolist()

    for ind_in, ind_out in zip(indices_in, indices_out):
        ip = inputs[ind_in]
        op = outputs[ind_out]
        edge(g, ip, op, part=part, reverse=reverse, **kwds)


def main_felix(g):
    gdaq = subgraph(g, 'daq', label='RCE')
    gfelix = subgraph(gdaq, 'felix', label='FELIX')

    backends = list()

    for iface in [0,1]:
        fes = list()
        for ident in range(iface*10, (iface+1)*10):
            _, cabs = femb(gdaq, ident, reverse = iface==0)
            fes.append(cabs[0])
        wf = wibface2(gdaq, iface, nfibers=5, nbundles=5,
                     reverse = iface==0)
        fel = felixface(gfelix, iface, nlinks=5, reverse = iface==0)

        linktp = facetp/len(wf[0])
        zipup(g, fes, wf[0], 'cable', reverse = iface==0, linktp=linktp)

        linktp = facetp/len(wf[1])
        zipup(g, wf[1], fel[0], 'bundle', reverse = iface==0,
              label="%.1f Gbps\n\n"%linktp, linktp=linktp)
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
        wf = wibface2(gdaq, iface, nfibers=40, nbundles=10, 
                     reverse = iface==0)
        rf = rceface(gdaq, iface, reverse = iface==0)

        fel = felixface(gfelix, iface, nlinks=4, reverse = iface==0)

        linktp = facetp/len(wf[0])
        zipup(g, fes, wf[0], 'cable', reverse = iface==0, linktp=linktp)

        zipup_transpose(g, wf[1], rf[0], reverse = iface==0, linktp=facetp/len(rf[0]))


        linktp = facetp/len(fel[0])
        zipup(g, rf[1], fel[0], reverse = iface==0,
              label='\n\n%.1f Gbps\n\n'%linktp,
              linktp=linktp)
        backends.append(fel[1])

    fh = felixhost(gfelix)
    edge(gfelix, backends[0][0], fh[0][0], reverse=True, linktp=facetp, dir='none')
    edge(gfelix, backends[1][0], fh[0][0], reverse=False, linktp=facetp, dir='none')


def main_oneface_rce_felix(g):
    iface=1
    fel = felixface(g, iface=iface, nlinks=5, reverse = iface==0)
    

def main_wibface_rce_felix(g):
    iface=1
    wf = wibface2(g, iface=iface, nfibers=40, nbundles=5,
                 reverse = iface==0)
    
def main_rceface_felix(g):
    iface=1
    rf = rceface(g, iface, reverse = iface==0)

def main(which = "felix"):
    from gravio import gen
    g = gen.Graph("dune", "digraph", label="DUNE",
                  nodesep='.1', ranksep='2',
                  rankdir='LR', style="filled,rounded", color='white')

    meth = eval("main_" + which)
    meth(g)
    return g
