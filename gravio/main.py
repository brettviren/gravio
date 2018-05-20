import click



@click.group("ported")
@click.pass_context
def cli(ctx):
    '''
    gravio.ported main
    '''


@cli.command("draw")
@click.argument("input_filename")
@click.argument("output_filename")
@click.pass_context
def ported_draw(cfg, input_filename, output_filename):
    '''
    Produce a dot file from a jsonnet file describing a ported graph.
    '''
    import networkx as nx
    import matplotlib.pyplot as plt
    from gravio import ported 
    G = nx.DiGraph()
    pgraph = ported.Ported(G)
    ported.jsonnet_load(input_filename, pgraph)

    print ("Graph: %s" % (str(G.graph),))
    print ("Nodes: %s" % (str(G.nodes),))
    print ("Edges: %s" % (str(G.edges),))

    for n,d in G.node.data():
        print (n,d)

    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G,pos) 
    nx.draw_networkx_edges(G,pos) 
    nx.draw_networkx_labels(G,pos)
    plt.savefig(output_filename)

def main():
    cli(obj=dict())

if '__main__' == __name__:
    main()
    
    
