#!/usr/bin/env python
'''

'''

import networkx


class Grapher(list):

    def __init__(self, name, typename='graph', **kwds):
        super(Grapher, self).__init__()
        self.append((typename, (name,), kwds))
        
    def __call__(self, typename, *args, **kwds):
        if typename == 'subgraph':
            g = Grapher(args[0], typename, **kwds)
            self.append(g)
            return g
        self.append((typename, args, kwds))

    


def test():
    g = Grapher("foo","digraph" )
    g('node','n1',color='red')
    g('edge','n1','n2', color='blue')
    s = g('subgraph','cluster_1',color='green')
    s('edge','a','b',color='purple')
    g('node','n3',color='gray')
    g('edge','a','n3',style='dotted')
    g('edge','n3','b',style='dashed')
    return g

