from mininet.topo import Topo

class FatTopo(Topo):
    def __init__(self, k):
        Topo.__init__(self)

        core_num = k * k / 4
        aggr_num = edge_num = k * k / 2
        host_num = edge_num * k / 2


        # add core switches
        self.cores_ = [self.addSwitch('cs%d' % switchId, dpid=("%X" % ((k << 24) + (3 << 8) + switchId))
                                      , protocols='OpenFlow13') for switchId in range(core_num)]


        # add aggregation switches
        self.aggrs_ = [self.addSwitch('as%d' % switchId, dpid=("%X" % ((k << 24) + (2 << 8) + switchId))
                                      , protocols='OpenFlow13') for switchId in range(aggr_num)]

        # add edge switches
        self.edges_ = [self.addSwitch('es%d' % switchId, dpid=("%X" % ((k << 24) + (1 << 8) + switchId))
                                      , protocols='OpenFlow13') for switchId in range(edge_num)]

        # add hosts
       # self.hosts_ = [self.addHost('h%d' % idx) for idx in range(host_num)]
        self.hosts_ = [self.addHost('h%d' % (switchId+1)) for switchId in range(host_num)]

        # add links between hosts and edge switches
       # self.links_ = [self.addLink(self.hosts_[idx], self.edges_[idx / (k / 2)])
        #             for idx in range(host_num)]

        self.links_ = [self.addLink(self.hosts_[idx], self.edges_[idx / (k / 2)]) for idx in range(host_num)]

        # add links between edge switches and aggregation switches
       # self.links_ += [self.addLink(self.edges_[i], self.aggrs_[j])
        #             for i in range(edge_num) for j in range(i / (k / 2), i / (k / 2) + k / 2)]
        self.links_ += [self.addLink(self.edges_[i], self.aggrs_[j])
                        for i in range(edge_num) for j in range(i / (k / 2) * (k / 2), i / (k / 2) * (k / 2) + k / 2)]

        # add links between aggregation switches and core switches
       # self.links_ += [self.addLink(self.aggrs_[i], self.cores_[j])
        #             for i in range(aggr_num) for j in range(core_num)]
        self.links_ += [self.addLink(self.cores_[i], self.aggrs_[j])
                        for i in range(core_num) for j in range(i / (k / 2), aggr_num, k / 2)]


    @classmethod
    def create(cls, k):
        return cls(k)

topos = {'fat_topo': FatTopo.create}
