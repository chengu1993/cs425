README

In this project, I implemented two routing strategies. There exists a common part of both routing strategies, which is the north to south routing (e.g. from core switches to aggregation switches, from aggregation switches to edge switches and from edge switches to hosts). Because only one path is available for north to south traffic. For those north to south traffic, I use destination address to match the flows. Every switch has certain number of hosts under their control. For every edge switch, it has K / 2 hosts connected to them directly and I will make K / 2 rules to forward packet to these hosts, where K is the scale of fat tree topology. For every aggregation switch, it has K ^ 2 / 4 hosts connected to them indirectly. I will make K ^ 2 / 4 rules for every host. Last but not least, for every core switch, it has K ^ 3 / 4 hosts connected indirectly. So there will be K ^ 3 / 4 rules in every core switch to forward packet to any host. However, multiple paths are available for south to north traffic. So I use two method to distribute the traffic to different paths evenly. I will describe the routing strategies in the following two section respectively.

Topology Background

For edge and aggregation switches, the lower K / 2 ports are connected to lower part and the upper K / 2 ports are connected to upper part. So for south to north traffic, packets enter edge and aggregation switches in lower K / 2 ports and leaves switches in upper K /2 ports.


1 Static Routing

The related .py files are fat_tree.py and routing.py. I use OpenFlow 1.0 as the south bound protocol. The basic idea of how to distribute south to north traffic is fairly simple, the output port is determined by in port. More specific, output_port = in_port + K / 2.


2 ECMP using group

The related .py files are fat_tree_ecmp.py and routin_ecmp.py. Since OpenFlow 1.0 does not support group action, I change the protocol to OpenFlow to 1.3 in this implementation. I define K / 2 buckets within a group, and each of the buckets is assigned an equal weight. We can just use in_port ranging from 1 to K / 2 to match south to north traffic. And For each bucket in the group, it is associated with output action which forward the packets to specific ports ranging from K/2+1 to K.  If switches find any south to north traffic, It will forward this packet using action randomly within this group.


Thoughts about these two methods

Both two methods fully utilize the bi-sectional bandwidth fat tree topology provides. But one drawback is they cannot handle elephant flow very well. 

