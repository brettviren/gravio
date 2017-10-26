#!/usr/bin/env python3
'''
'''
import json
import networkx as nx

def loadf(filename):
    return json.loads(open(filename).read())

def jdat2nx(jdat):

    if type(jdat) == list:
        return [jdat2nx(jd) for jd in jdat]

    nodes = jdat.pop("nodes", ())
    edges = jdat.pop("edges", ())
    gtype = jdat.pop("type", "graph")
    Graph = nx.Graph
    if gtype.lower() == "digraph":
        Graph = nx.DiGraph
    g = Graph(**jdat)

    for nodename in nodes:
        if not nodename:
            continue
        nodeattr = nodes[nodename]
        if nodeattr:
            g.add_node(nodename, **nodeattr)
        else:
            g.add_node(nodename)

    for edat in edges:
        if type(edat) == list:
            if len(edat) == 2:
                g.add_edge(edat[0], edat[1])
            elif len(edat) == 3:
                g.add_edge(edat[0], edat[1], **edat[2])
        
    return g

def write(g, filename=None):
    if type(g) == list:
        return [write(one, filename) for one in g]

    print (g)

    # here assume g is singluar
    from networkx.drawing.nx_pydot import write_dot
    if not filename:
        filename = g.graph["name"] + ".dot"
    print ("writing: %s" % filename)
    write_dot(g, filename)
    

if __name__ == '__main__':

    jdat = loadf("graph.json")
    g = jdat2nx(jdat)
    write(g)
