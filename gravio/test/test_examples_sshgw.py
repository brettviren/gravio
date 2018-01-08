import gravio.examples.sshgw
import gravio.gen
import gravio.dotify

def main():
    from gravio import gen
    g = gen.Graph("sshgw", "digraph", label="")

    gravio.examples.sshgw.main(g)
    d = gravio.dotify.Dotify(g)
    filename = "test_examples_sshgw.dot"
    open(filename,"w").write(str(d))
    print ("wrote:",filename)

if '__main__' == __name__:
    main()
