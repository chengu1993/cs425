from mininet.topo import Topo

class FatTopo(Topo):
    def __init__(self, k):
        Topo.__init__(self)

        core_num = k * k / 4
        aggr_num = edge_num = k * k / 2
        host_num = edge_num * k / 2

        # add core switches
        self.cores = [self.addSwitch(idx, protocols='OpenFlow10')
                     for idx in range(core_num)]
        # add aggregation switches
        self.aggrs = [self.addSwitch(idx, protocols='OpenFlow10')
                     for idx in range(aggr_num)]

        # add edge switches
        self.edges = [self.addSwitch(idx, protocols='OpenFlow10')
                     for idx in range(edge_num)]

        # add hosts
        self.hosts = [self.addHost(idx) for idx in range(host_num)]

        # add links between hosts and edge switches
        self.links = [self.addLink(self.hosts[idx], self.edges[idx / 2])
                      for idx in range(host_num)]

        # add links between edge switches and aggregation switches
        self.links += [self.addLink(self.edges[i], self.aggrs[j])
                       for i in range(edge_num) for j in range(i / 2, i / 2 + 2)]

        # add links between aggregation switches and core switches
        self.links += [self.addLink(self.aggrs[i], self.cores[j])
                       for i in range(aggr_num) for j in range(core_num)]


    @classmethod
    def create(cls, k):
        return cls(k)

topos = {'fat_tree': FatTopo.create}