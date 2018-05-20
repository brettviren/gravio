// a simple gravio.ported graph

// some shared port attributes 
local p1 = {
    bandwidth: 10.0,
    protocol: "Super Fast v2.0",
};
local p2 = {
    bandwidth: 1.0,
    protocol: "Control Flow v42",
};

// some nodes
local source = {
    name: "source",
    attr: {
        rate: 0.5,
    },
    ports: [
        {
            name: "out",
            ptype: "oport",
            attr: p1,
        },
        {
            name: "control",
            ptype: "iport",
            attr: p2,
        },
    ],
};
local sink = {
    name: "sink",
    attr: {
        max_rate: 0.7,
    },
    ports: [
        {
            name: "in",
            ptype: "iport",
            attr: p1,
        },
        {
            name: "command",
            ptype: "oport",
            attr: p2,
        },
    ],
};

{
    attr: {
        title: "Simple ported example",
    },
    nodes: [source, sink],
    edges: [
        {
            tail: ["source","out"],
            head: ["sink","in"],
        },
        {
            tail: "sink:command",
            head: "source:control",
        },
    ]
}
