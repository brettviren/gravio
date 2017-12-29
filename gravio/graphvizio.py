#!/usr/bin/env python
'''
This module is an interface between gravio and the "graphviz" python module.

  https://graphviz.readthedocs.io

See also gravio.dotify for a way to dump a gravio graph to Dot text.
'''

import graphviz

def wash_attr(attr):
    ret = dict()
    for k,v in attr.items():
        ret[k] = str(v)
    return ret

def dump_graph(g, gv):
    '''
    Fill graphviz graph gv with contents from gravio graph g
    '''
    if g.attr:
        gv.graph_attr.update(**wash_attr(g.attr))

    for one in g:

        if one.typename == 'subgraph':
            with gv.subgraph(name=g.name) as sgv:
                dump_graph(one, sgv)
            continue

        if one.typename == 'node':
            if one.name:
                gv.node(one.name, **wash_attr(one.attr))
                continue
            if one.attr:
                gv.node_attr.update(**wash_attr(one.attr))
                continue

        if one.typename == 'edge':
            if one.tail and one.head:
                gv.edge(one.tail, one.head, **wash_attr(one.attr))
                continue
            if one.attr:
                gv.edge_attr.update(**wash_attr(one.attr))

def dump(g):
    '''
    Return a graphviz graph made from the gravio one.
    '''
    if g.typename == 'digraph':
        gv = graphviz.Digraph(g.name)
    else:
        gv = graphviz.Graph(g.name)
        # fixme: there are other graph types...

    dump_graph(g, gv)
    return gv
