def subgraph(g, name, **kwds):
    return g.subgraph(name, **kwds)
def node(g, name, **kwds):
    return g.node(name, **kwds)
def edge(g, n1, n2, **kwds):
    return g.edge(n1,n2, **kwds)

def main(g):
    g.node(shape='box')

    gr = subgraph(g, 'racf', label='RACF Network', labelloc='bottom')
    gc = subgraph(g, 'campus', label='Campus Network', labelloc='bottom')
    gi = subgraph(g, 'outside', label='Internet / BNL WiFi')

    rgw = node(gr, 'rssh', shape='house', label="RACF SSH GW\n(rssh.rhic.bnl.gov)\n\n\n\n")
    cgw = node(gc, 'cssh', shape='house', label="Campus SSH GWs\n(cssh.rhic.bnl.gov)\n(gateway.phy.bnl.gov)\n(physsh.phy.bnl.gov)\n(ssh.bnl.gov)")
    
    rin = node(gr, 'rin', label='interactive node\n(abcd0001)')
    cws = node(gc, 'cws', label='workstation\n(mycomp.phy.bnl.gov)')
    lap = node(gi, 'lap', label='laptop')

    edge(g, lap, cgw)
    edge(g, cgw, cws)
    edge(g, lap, rgw)
    edge(g, rgw, rin)

    edge(g, rin, cgw)
    edge(g, cws, rgw)
    return g


    
