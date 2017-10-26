local bluebox = {
    color: "blue",
    shape: "box",
};

local merge = function(g1, g2) g1+g2 + { 
    nodes: g1.nodes + g2.nodes,
    edges: g1.edges + g2.edges, 
};

local g1 = {
    type: "digraph",
    name: "graph1",
    nodes: { node1: {foo:"bar"}, node2: {}, node3: bluebox},
    edges: [ ["node1","node2"], ["node3","node1"] ],
    thing1: "thing1",
};
local g2 = {
    name: "graph2",
    nodes: { node1: {foo:"baz"}, node2: {}, node4: {}},
    edges: [ ["node2","node4"], ["node1","node4"], ["node1","node2"] ],
    thing2: "thing2",
};

local g3 = merge(g1,g2) { name: "graph3"};

[g1, g2, g3 ]
