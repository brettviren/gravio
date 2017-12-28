#!/usr/bin/env python
'''

'''



class Node(object):

    def __init__ (self, name, **attr):
        self.name = name
        self.attr = attr

    @property
    def typename(self):
        return 'node'

    def __repr__(self):
        return '<node %s>'%self.name

class Edge(object):

    def __init__(self, tail=None, head=None, **attr):
        if isinstance(tail, Node):
            tail = tail.head
        if isinstance(head, Node):
            head = head.head
        self.tail = tail
        self.head = head
        self.attr = attr

    @property
    def typename(self):
        return 'edge'

    def __repr__(self):
        return '<edge (%s,%s))>'%(self.tail, self.head)

class Graph(list):

    def __init__(self, name=None, typename='graph', **attr):
        super(Graph, self).__init__()
        self.name = name
        self.attr = attr
        self.typename = typename

    def __repr__(self):
        return '<%s %s>'%(self.typename, self.name)
        
    def __call__(self, typename, *args, **attr):
        if typename in ['subgraph','graph']:
            g = Graph(args[0], typename, **attr)
            self.append(g)
            return g
        if typename == 'edge':
            e = Edge(args[0], args[1], **attr)
            self.append(e)
            return e
        if typename == 'node':
            n = Node(args[0], **attr)
            self.append(n)
            return n

        other = (typename, args, kwds)
        self.append(other)
        return other

    def graph(self, name=None, **attr):
        return self('subgraph', name, **attr)
    subgraph = graph

    def node(self, name=None, **attr):
        return self('node', name, **attr)

    def edge(self, tail=None, head=None, **attr):
        return self('edge', tail, head, **attr)

    def bytype(self, typename, **kwds):
        '''
        Return a list of entries of given type and with attr matching keywords.
        '''
        ret = list()
        for one in self:
            if isinstance(one, tuple):
                tn = one[0]
            else:
                tn = one.typename
            if tn != typename:
                continue
            try:
                for key in kwds:
                    if kwds[key] != one.attr[key]:
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

    def graphs(self, **kwds):
        '''
        Return a list of subgraphs with matching attributes.
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
            if type(one) == Graph:
                ret.append(one)
        return ret


def test():
    g = Graph("foo","digraph" )
    g('node','n1',color='red')
    g('edge','n1','n2', color='blue')
    s = g('subgraph','cluster_1',color='green')
    s('edge','a','b',color='purple')
    g('node','n3',color='gray')
    g('edge','a','n3',style='dotted')
    g('edge','n3','b',style='dashed')
    return g

