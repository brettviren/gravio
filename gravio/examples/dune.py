#!/usr/bin/env python

def colors(what):
    '''
    This function encapsulates my inability to pick nice colors.

    https://graphviz.gitlab.io/_pages/doc/info/colors.html
    '''
    scheme = '/bupu6/'
    ranks = 'apa face femb wib felix'.split()
    ind = ranks.index(what)
    return scheme + str(ind+1)


def femb(g, ctx, ident, reverse=False):

    sg = g.subgraph('cluster_%s_femb%s'%(ctx,ident),
                    label='FEMB %s'%ident,
                    color=colors('femb'),
                    part='femb', ident=int(ident))

    ctx = '%s_femb%s' % (ctx, ident)

    gfe = sg.subgraph('cluster_%s_fes'%ctx, label='',part='fes')
    gadc = sg.subgraph('cluster_%s_adcs'%ctx, label='',part='adcs')
    gtx = sg.subgraph('cluster_%s_txs'%ctx, label='',part='txs')

    cable = sg.node('%s_cable'%ctx, label='cable',
                    shape='circle', part='cable')

    for iasic in range(8):
        nfe = '%s_fe%d'%(ctx, iasic)
        gfe.node(nfe, label='FE%d'%iasic, 
                 part='fe', ident=iasic)
        nadc = '%s_adc%d'%(ctx, iasic)
        gadc.node(nadc, label='ADC%d'%iasic, 
                  part='adc', ident=iasic)

        if iasic%2 == 0:
            ntx = gtx.node('%s_tx%d'%(ctx, iasic//2),
                           shape='hexagon', label='tx',
                           part='tx', ident=iasic//2)
            if reverse:
                sg.edge(cable, ntx, penwidth=2, dir='back')
            else:
                sg.edge(ntx, cable, penwidth=2)

        if reverse:
            sg.edge(nadc, nfe, dir='back')
            sg.edge(ntx, nadc, dir='back')
        else:
            sg.edge(nfe,nadc)
            sg.edge(nadc,ntx)

    return sg

def wib(g, ctx, ident, nconns = 4, nuplinks=2):

    ctx = '%s_wib%s'%(ctx, ident)

    sg = g.subgraph('cluster_%s' % ctx, label="WIB %s" % ident)
    
    gconns = sg.subgraph('cluster_%s_conns' % ctx, label="", part="conns")

    conns = list()
    for iconn in range(nconns):
        n = gconns.node('%s_conn%d'%(ctx, iconn), label="conn%d" % iconn,
                        shape='circle', part='wibconn',ident=iconn)
        conns.append(n)

    for a,b in zip(conns[:-1], conns[1:]):
        gconns.edge(a,b,style='invis')
    return sg

def wibfaces(g, ctx, nwibs, nwibconns):
    gwibfaces = list();
    for iface in [0,1]:
        face_ctx = '%s_wibface%d' % (ctx, iface)
        sg = g.subgraph('cluster_'+face_ctx, label='WIB face %d' % iface,
                        color=colors('wib'))
        gwibfaces.append(sg)
        
        gtxs = sg.subgraph('cluster_%s_txs'%face_ctx, label="",
                           part="wibtxs", iface=iface)
        txs = list()
        fibers = list()
        for iwib in range(nwibs):

            tx = gtxs.node("%s_uplink%d" % (face_ctx, iwib),
                           shape='hexagon', label="rx/mx/tx")
            txs.append(tx)
            fiber = sg.node("%s_fiber%d"%(face_ctx, iwib),
                            part='fiber', shape='circle', label='fiber')
            fibers.append(fiber)


        for iconnhalf in range(nwibconns//2):
            iconn = iconnhalf + iface*2
            grp_ctx = '%s_conns%d' %(face_ctx, iconnhalf)




            gconn = sg.subgraph('cluster_'+grp_ctx,
                                label='WIB connectors #%d'%iconn,
                                part='wibconns')
            for iwib in range(nwibs):
                n = gconn.node('%s_wib%dconn%d' % (ctx, iwib, iconn),
                               label='WIB%d\nconn%d'%(iwib, iconn),
                               shape='circle',
                               part='wibconn', iconn=iconn, iwib=iwib)
                tx = txs[iwib]
                fiber = fibers[iwib]
                if iface:
                    sg.edge(tx, n, penwidth=8, dir='back')
                    if iconnhalf:
                        sg.edge(fiber, tx, penwidth=16, dir='back')
                else:
                    sg.edge(n, tx, penwidth=8)
                    if iconnhalf:
                        sg.edge(tx, fiber, penwidth=16)
                
    return gwibfaces
                
def felix(g, ctx, nlinks=10):
    sg = g.subgraph('cluster_%sfelix' % ctx, label="FELIX",
                    color=colors('felix'))

    gfaces = [list(), list()]
    links = [list(), list()]
    for iface in [0,1]:
        face_ctx = '%sfelixface%d'%(ctx,iface)

        gf = sg.subgraph('cluster_' + face_ctx,
                         label="Face %d" % iface,
                         part='face',iface=iface)
        for ilink in range(nlinks//2):
            n = gf.node('%slink%d'%(face_ctx,ilink),
                        part='link', label="link %d"%ilink, shape="circle")
            links[iface].append(n)

    rs = sg.subgraph('', rank='same')

    fpga = rs.node('%sfelixfpga'%ctx, label='\n  FPGA  \n\n', shape='octagon')
    pcie = rs.node('%sfelixpcie'%ctx, label='\n\nPCIe\n\n\n')
    sg.edge(fpga, pcie, penwidth=32)
    sg.edge(links[0][0], pcie, style='invis', weight=3)
    sg.edge(links[1][0], pcie, style='invis', weight=3)

    for l1,l2 in zip(*links):
        sg.edge(l1,l2, style='invis')
        sg.edge(l1,fpga, penwidth=16)
        sg.edge(fpga,l2, penwidth=16, dir='back')
    return sg

    

def apa(g, ctx, ident, nfembs = 20, nwibs=5, nwibconns=4, nwibuplinks=2):
    assert(nfembs == nwibs*nwibconns)

    sg = g.subgraph('cluster_%s_apa%s'%(ctx, ident),
                    label='APA %s'%ident,
                    color=colors('apa'),
                    part='apa', ident=int(ident))

    fecables = [list(),list()]

    gfaces = list()
    for iface in [0,1]:
        nface = "%s_face%d"%(ctx,iface)
        gface = sg.subgraph("cluster_"+nface,
                            label="Face %d" % iface,
                            color=colors('face'),
                            part='face', iface=iface)
        gfaces.append(gface)
        for ifemb in range(iface*nfembs//2, (iface+1)*nfembs//2):
            gfemb = femb(gface, nface, "%02d"%ifemb, iface)
            cable = gfemb.nodes(part='cable')[0]
            fecables[iface].append(cable)

    # in id order
    all_cables = fecables[0] + fecables[1]

    gwibfaces = wibfaces(sg, ctx, nwibs, nwibconns)
    for g1,g2 in zip(gfaces, gwibfaces):
        g1.append(g2)

    gfelix = felix(sg, ctx, 2*nwibs)


    links = [gfelix.graphs(part='face')[0].nodes(part='link'),
             gfelix.graphs(part='face')[1].nodes(part='link')]

    # stitch together the inner layers
    for iconn in range(nwibconns):
        iface = iconn // 2
        gwibface = gwibfaces[iface]

        
        fibers = gwibface.nodes(part='fiber')

        igrp = iconn %2
        wibconns = gwibface.graphs(part='wibconns')[igrp].nodes(part='wibconn')

        for iwib in range(nwibs):
            wc = wibconns[iwib]
            icab = iwib + iconn*nwibs
            cab = all_cables[icab]
            if iface:
                sg.edge(wc,cab, penwidth=8, dir='back')
                if iconn%2:
                    sg.edge(links[iface][iwib], fibers[iwib], penwidth=16, dir='back')
            else:
                sg.edge(cab,wc, penwidth=8)
                if iconn%2:
                    sg.edge(fibers[iwib], links[iface][iwib], penwidth=16)



    return sg

def main():
    from gravio import gen
    g = gen.Graph("dune", "digraph", label="DUNE",
                  nodesep='.1', ranksep='2',
                  rankdir='LR', style="filled", color='white')
    g.node(shape='box')

    ctx = "top"
    apa(g, ctx, '000')

    return g
