#!/usr/bin/env python

from gravio import gen, dotify

g = gen.Graph("simple", "digraph", label="my graph", style="filled")
assert g.typename == 'digraph'
n = g('node', 'a', color='red')
assert n.name == 'a'
g.node(None, shape='box')

n = g.node('b', color='blue', special=True)
assert n.attr['color'] == 'blue'
e = g('edge', 'a', 'b', style='dashed', weight=0.1)
assert e.tail == 'a'
assert e.head == 'b'
g.edge(style='dotted')
g.edge('a','c', color='green')
sg = g.subgraph('cluster_sg', style='solid', label="my subgraph")
assert sg.typename == 'subgraph'
sg.node('d')
g.edge('a','d')
print (g.name, g.typename, len(g.subgraphs))
print (g.nodes(color='red'))

g2 = gen.Graph("cluster_external","subgraph",label="external")
g2.edge("aa","bb")
g2.append(gen.Node("cc"))
g2.append(gen.Edge("aa","cc"))

g.append(g2)
e = g.edge("a","aa", constraint=False)
assert e.attr['constraint'] == False # not "False"

d = dotify.Dotify(g, indent='  ')
print (d)
print ('writing')
open("test_simple.dot","w").write(str(d))

print ('RED nodes:',g.nodes(color='red'))
print ('special nodes:',g.nodes(special=True))
print (g.subgraphs)
print (g.graphs(style='solid'))
