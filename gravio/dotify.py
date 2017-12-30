import functools

def node_in_edge(nstr):
    parsed = tuple(nstr.split(':',1))
    if len(parsed) == 1:
        return '"%s"'%parsed[0]
    return '"%s":%s'%parsed

class Dotify(object):

    def __init__(self, graph, indent = '\t'):
        self.indent = indent
        self.arrow = '--'

        if graph.typename == 'digraph':
            self.arrow = '->'
        self.lines = self.subgraph(0, graph)

    def __str__(self):
        return '\n'.join(self.lines)
    __repr__ = __str__

    def tab(self, depth):
        return self.indent*depth

    def sattr(self, depth, what, kwds):
        s = ','.join(['%s="%s"'%kv for kv in kwds.items()])
        return ['%s%s[%s];' % (self.tab(depth), what, s)]

    def node(self, depth, obj):
        return self.sattr(depth, obj.name or 'node', obj.attr)

    def edge(self, depth, obj):
        what = 'edge'
        if obj.tail and obj.head:
            what = '%s %s %s' % (node_in_edge(obj.tail),
                                 self.arrow,
                                 node_in_edge(obj.head))
        return self.sattr(depth, what, obj.attr)

    def subgraph(self, depth, obj):
        name = obj.name
        # don't require user to care about this wonky dot convention
        if name and not name.startswith('cluster_'):
            name = 'cluster_' + name
        lines = ["%s%s %s {" % (self.tab(depth), obj.typename, name)]
        if obj.attr:
            lines += self.sattr(depth+1, 'graph', obj.attr)
        lines += self.next_lines(depth+1, obj)
        lines.append("%s}" % self.tab(depth))
        return lines

    def next_lines(self, depth, objlist):
        if not objlist:
            return list()

        obj = objlist[0]

        render = getattr(self, obj.typename)
        lines = render(depth, obj)
        lines += self.next_lines(depth, objlist[1:]); # continue
        return lines
        
