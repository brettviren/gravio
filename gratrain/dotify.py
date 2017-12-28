import functools

def node_in_edge(nstr):
    parsed = tuple(nstr.split(':',1))
    if len(parsed) == 1:
        return '"%s"'%parsed[0]
    return '"%s":%s'%parsed

class Dotify(object):

    def __init__(self, cmdlist, indent = '\t'):
        cmdlist = list(cmdlist) # copy
        self.indent = indent
        self.arrow = '--'

        # treat first one special
        typename, args, kwds = cmdlist.pop(0)
        if typename == 'digraph':
            self.arrow = '->'
        self.lines = self.subgraph(0, typename, args, kwds, cmdlist)

    def __str__(self):
        return '\n'.join(self.lines)
        
    def tab(self, depth):
        return self.indent*depth

    def attrs(self, depth, typename, args, kwds):
        s = ','.join(['%s="%s"'%kv for kv in kwds.items()])
        return ['%s%s[%s];' % (self.tab(depth), typename, s)]

    def edge(self, depth, typename, args, kwds):
        if args:
            what = '%s %s %s' % (node_in_edge(args[0]), self.arrow, node_in_edge(args[1]))
        else:
            what = "edge"
        return self.attrs(depth, what, (), kwds)

    def node(self, depth, typename, args, kwds):
        if args:
            what = '"%s"' % (args[0],)
        else:
            what = "node"
        return self.attrs(depth, what, (), kwds)

    def graph(self, depth, typename, args, kwds):
        return self.attrs(depth, 'graph', (), kwds)

    def subgraph(self, depth, typename, args, kwds, cmdlist):
        lines = ["%s%s %s {" % (self.tab(depth), typename, args[0])]
        if kwds:
            lines += self.attrs(depth+1, 'graph', (), kwds)
        lines += self.next_lines(cmdlist, depth+1)
        lines.append("%s}" % self.tab(depth))
        return lines

    def next_lines(self, cmdlist, depth):
        if not cmdlist:
            return list()

        lines = list()
        cmd = cmdlist.pop(0)
        if type(cmd) == tuple:
            typename, args, kwds = cmd

            render = getattr(self, typename, self.attrs)
            lines += render(depth, typename, args, kwds)
        else:                       # its a subgraph
            typename, args, kwds = cmd.pop(0)
            lines = self.subgraph(depth, typename, args, kwds, cmd)

        lines += self.next_lines(cmdlist, depth); # continue
        return lines
        
