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

    def bytype(self, typename, **kwds):
        '''
        Return a list of entries of given type.
        '''
        ret = list()
        for one in self:
            if type(one) != tuple:
                continue
            if one[0] != typename:
                continue
            try:
                for key in kwds:
                    if kwds[key] != one[2][key]:
                        raise KeyError
            except KeyError:
                continue
            ret.append(one)
        return ret

    def nodes(self, **kwds):
        '''
        Return nodes with kwds matching kwds
        '''
        return self.bytype('node', **kwds)

    def match(self, **kwds):
        '''
        Return a list of subgraphs with matching attributes. Fixme: make it handle non-subgraph
        '''
        ret = list()
        for sg in self.subgraphs:
            try:
                for key in kwds:
                    if kwds[key] != sg.attr[key]:
                        raise KeyError
            except KeyError:
                continue
            ret.append(sg)
        return ret

    @property
    def subgraphs(self):
        '''
        Return list of top level subgraphs.
        '''
        ret = list()
        for one in self:
            if type(one) != tuple:
                ret.append(one)
        return ret

    @property
    def name(self):
        return self[0][1][0]

    @property
    def type(self):
        return self[0][0]

    @property
    def attr(self):
        return self[0][2]

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

