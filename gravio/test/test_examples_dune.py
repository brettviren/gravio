import gravio.examples.dune
import gravio.gen
import gravio.dotify

def main():

    views = [
        "felix",
        "rce_felix",
        #"oneface_rce_felix",
        "wibface_rce_felix",
        #"rceface_felix"
    ]
    for which in views:
        g = gravio.examples.dune.main(which)
        d = gravio.dotify.Dotify(g)
        filename = "test_examples_dune_%s.dot"%which
        open(filename,"w").write(str(d))
        print ("wrote:",filename)


    #gv = gravio.graphvizio.dump(g)
    #gv.view()
    #return gv

if '__main__' == __name__:
    main()
    
