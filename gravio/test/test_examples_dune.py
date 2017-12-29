import gravio.examples.dune
import gravio.gen
import gravio.dotify

def main():
    g = gravio.examples.dune.main()

    #gravio.gen.visit(g, print)

    d = gravio.dotify.Dotify(g)
    open("test_examples_dune.dot","w").write(str(d))
    return g
    #gv = gravio.graphvizio.dump(g)
    #gv.view()
    #return gv

if '__main__' == __name__:
    main()
    
