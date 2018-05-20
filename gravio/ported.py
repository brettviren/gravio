#!/usr/bin/env python3
'''
A ported graph adds the concept of a labeled point on a node to which
an edge connects.  That is, a node is defined as a collection of ports
and an edge in terms of the (node,port) pair it connects.  Like
graphs, nodes and edges, ports may carry arbitrary attributes.

In a directed graph, a node's ports are separated into an "input" set
and an "output" set and an edge connects from an output to an input
port.

A ported multigraph allows more than one edge to attach to a port
otherwise a connection to a port is exclusive to one edge.  A "capped"
ported graph has no ports lacking a connection.  A node with only
output ports is a "source" and one with only input ports a "sink".

For now, this module only supports directed graphs.
'''


class Ported(object):
    '''
    Add some methods and semantics to underlying graph storage to
    support ported graphs.

    A "node" is a represented in the graph as vertex with attribute
    "vtype" of "node".  It is identified by a label (abreviated 'nid'
    in methods) which is any string that does not contain a ":".
    Note, the term "node" is not a synonym for "vertex".

    A "port" is represented in the graph as a vertex with attribute
    "vtype" of "port".  It is identified by the node to which it
    belongs and a label wihch is any string that does not contain a
    ":".  This pair may be represented by a tuple or a string as
    returned by portid().
    '''
    def __init__(self, G):
        '''Create with existing graph (eg, networkx.DiGraph instance)'''
        self.G = G

    def find(self, **attr):
        '''Return list of vertex IDs with matching attribute'''
        ret = list()
        for vid, dat in self.G.nodes.data():
            def maybe():
                for key in attr:
                    if not key in dat:
                        return False
                    if dat[key] != attr[key]:
                        return False
                return True
            if maybe():
                ret.append(vid)
        return ret

    def update(self, ident=None, **attr):
        '''
        Update the attributes of something.  If ident is None, update
        the graph attributes.
        '''
        if ident is None:
            self.G.graph.update(**attr)
        else:
            self.G.node[ident].update(**attr)
        

    def add_vertex(self, vid, **attr):
        print ('adding vertex: "%s"' % vid)
        self.G.add_node(vid)
        self.update(vid, **attr)
        return vid

    def add_node(self, nid, **attr):
        '''
        Add a node vertex to the graph.
        '''
        return self.add_vertex(nid, vtype='node', **attr)

    def portid(self, ident, label=None):
        '''
        Return the port ID as a string.  

        ident may be a string or a tuple
        '''
        if isinstance(ident, tuple) or isinstance(ident, list):
            return "%s:%s" % tuple(ident)
        if ":" in ident:
            return ident;
        if label:
            return "%s:%s" % (ident, label)
        raise ValueError("Bad arguments to portid: ident=\"%s\" label=\"%s\"" % (ident, label))

    def add_port(self, nid, label, ptype=None, **attr):
        '''Make a port on a node.'''
        if ptype not in ["oport", "iport"]:
            raise ValueError('No port type for nid="%s" label="%s"' % (nid,label))
        self.add_node(nid);
        pid = self.portid(nid, label)
        self.add_vertex(pid, vtype='port', ptype=ptype, **attr)
        if ptype == "iport":
            self.G.add_edge(pid, nid)
        if ptype == "oport":
            self.G.add_edge(nid,pid)
        return pid

    def add_oport(self, nid, label, **attr):
        '''Make an output port on a node.'''
        pid = self.add_port(nid, label, ptype="oport", **attr)
        self.add_edge(nid, pid)
        return pid

    def add_iport(self, nid, label, **attr):
        '''Make an input port on a node.'''
        pid = self.add_port(nid, label, ptype="iport", **attr)
        self.G.add_edge(pid, nid)
        return pid

    def oports(self, nid):
        '''Return the port IDs for all output ports of given node ID'''
        return self.find(vtype='port', ptype='oport')
    def iports(self, nid):
        '''Return the port IDs for all input ports of given node ID'''
        return self.find(vtype='port', ptype='iport')

    def connect(self, tail, head, **attr):
        '''Connect two nodes via ports.

        Nodes and ports must already be created.

        The tail and head are ports either in the form of (nid,label)
        tuples or valid port IDs.
        '''
        tail = self.portid(tail)
        head = self.portid(head)
        if self.G.nodes[tail]['ptype'] != 'oport':
            raise ValueError("tail port \"%s\" is not an output port"%tail)
        if self.G.nodes[head]['ptype'] != 'iport':
            raise ValueError("head port \"%s\" is not an input port"%head)
        self.G.add_edge(tail, head, **attr)

def jsonnet_load(filename, ported):
    '''
    Load into a ported.Ported, the information in Jsonnet file.
    
    File must follow schema for one graph object:
    {
      attr: { /*graph attributes*/ },
      nodes: [ /*list of node obj*/ },
      edges: [ /*list of edge obj*/},
    }

    A node object:
    {
       name: "node id string",
       ports: [ /*list of port obj*/],
       attr: { /*node attributes*/ }
    }

    A port object:
    {
       name: "port label string",
       ptype: "oport"|"iport",
       attr: { /*port attributes*/ },
    }

    An edge object:
    {
       tail: "portID"|[nodeID,port label],
       head: "portID"|[nodeID,port label],
       attr: { /* edge attributes */ }
    }

    A attr object is arbitrary.
    '''
    import _jsonnet as jsonnet
    import json
    jtext = jsonnet.evaluate_file(filename)
    dat = json.loads(jtext)

    ported.update(**dat.get('attr', {}))

    for node in dat['nodes']:
        nid = node['name']
        ported.add_node(nid, **node.get('attr', {}))
        for port in node['ports']:
            label = port['name']
            ptype = port['ptype']
            ported.add_port(nid, label, ptype=ptype, **port.get('attr',{}))
    for edge in dat.get('edges', list()):
        ported.connect(edge['tail'],edge['head'], **edge.get('attr',{}))
    return ported

            

