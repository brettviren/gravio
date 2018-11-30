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

@cli.command("dexnet")
@click.argument("input_filename")
@click.argument("output_filename")
def dotify_dexnet(input_filename, output_filename):
    import json
    dat = json.loads(open(input_filename,'rb').read().decode())
    import networkx as nx
    import matplotlib.pyplot as plt
    from gravio import ported 
    G = nx.DiGraph()
    p = ported.Ported(G)

    for agent in dat:
        agent.setdefault('type', 'agent')
        nid = "{type}:{name}".format(**agent)
        p.add_node(nid)
        for port in agent["ports"]:
            pid = "port:%s"%port["name"]
            # fixme: agent ports are not in/out typed
            p.add_port(nid, pid, ptype='oport')
            for sock in port.get("bind",[]) + port.get("connect",[]):
                p.add_node(b);
                p.connect(pid,sock)
                
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G,pos) 
    nx.draw_networkx_edges(G,pos) 
    nx.draw_networkx_labels(G,pos)
    plt.savefig(output_filename)


def main():
    cli(obj=dict())

if '__main__' == __name__:
    main()
    
    
