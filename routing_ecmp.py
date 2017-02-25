from ryu.base import app_manager
from ryu.controller import ofp_event, dpset
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ether

class Controller(app_manager.RyuApp):
    def switch_connected(self, sw):
        ofproto = sw.ofproto
        parser = sw.ofproto_parser
        k = sw.id >> 24
        sw_type = (sw.id & 0xF00) >> 8
        sw_id = sw.id & 0xFF

        buckets = [parser.OFPBucket(weight=1, actions=[parser.OFPActionOutput(i)])
                   for i in range(k / 2 + 1, k + 1)]
        group_id = 29
        group_mod = parser.OFPGroupMod(
            datapath=sw, command=ofproto.OFPGC_ADD,
            type_=ofproto.OFPGT_SELECT, group_id=group_id,
            buckets=buckets)
        sw.send_msg(group_mod)

        def match_action_add(match, inst, priority):
            cmd = parser.OFPFlowMod(
                    datapath=sw, match=match, cookie=0,
                    command=ofproto.OFPFC_ADD, idle_timeout=0,
                    hard_timeout=0, priority=priority,
                    flags=ofproto.OFPFF_SEND_FLOW_REM, instructions=inst)
            sw.send_msg(cmd)

        def route_protocol(base_priority):
            if sw_type == 1:  # edge switches

                #upward
                for i in range(1, k / 2 + 1):
                    ip_match = parser.OFPMatch(in_port=i, eth_type=ether.ETH_TYPE_IP)
                    arp_match = parser.OFPMatch(in_port=i, eth_type=ether.ETH_TYPE_ARP)
                    action = parser.OFPActionGroup(group_id)
                    inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [action])]
                    match_action_add(ip_match, inst, 1100 + base_priority)
                    match_action_add(arp_match, inst, 1100 + base_priority)

                # Downward IP
                base_dst = (10 << 24) + sw_id * (k / 2)
                for i in range(1, k / 2 + 1):
                    ip_match = parser.OFPMatch(ipv4_dst=(base_dst + i), eth_type=ether.ETH_TYPE_IP)
                    arp_match = parser.OFPMatch(arp_tpa=(base_dst + i), eth_type=ether.ETH_TYPE_ARP)
                    action = parser.OFPActionOutput(i)
                    inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [action])]
                    match_action_add(ip_match, inst, 1200 + base_priority)
                    match_action_add(arp_match, inst, 1200 + base_priority)

            elif sw_type == 2:  # aggregation switches

                #upward
                for i in range(1, k / 2 + 1):
                    ip_match = parser.OFPMatch(in_port=i, eth_type=ether.ETH_TYPE_IP)
                    arp_match = parser.OFPMatch(in_port=i, eth_type=ether.ETH_TYPE_ARP)
                    action = parser.OFPActionGroup(group_id)
                    inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [action])]
                    match_action_add(ip_match, inst, 1100 + base_priority)
                    match_action_add(arp_match, inst, 1100 + base_priority)

                # Downward
                base_dst = (10 << 24) + sw_id / (k / 2) * pow(k / 2, 2)
                for i in range(1, pow(k / 2, 2) + 1):
                    ip_match = parser.OFPMatch(ipv4_dst=(base_dst + i), eth_type=ether.ETH_TYPE_IP)
                    arp_match = parser.OFPMatch(arp_tpa=(base_dst + i), eth_type=ether.ETH_TYPE_ARP)
                    action = parser.OFPActionOutput((i - 1) / (k / 2) + 1)
                    inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [action])]
                    match_action_add(ip_match, inst, 1200 + base_priority)
                    match_action_add(arp_match, inst, 1200 + base_priority)

            else:  # core switches

                # Downward
                base_dst = 10 << 24
                for i in range(1,  pow(k / 2, 2) * k + 1):
                    ip_match = parser.OFPMatch(ipv4_dst=(base_dst + i), eth_type=ether.ETH_TYPE_IP)
                    arp_match = parser.OFPMatch(arp_tpa=(base_dst + i), eth_type=ether.ETH_TYPE_ARP)
                    action = parser.OFPActionOutput((i - 1) / pow(k / 2, 2) + 1)
                    inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [action])]
                    match_action_add(ip_match, inst, 1100 + base_priority)
                    match_action_add(arp_match, inst, 1100 + base_priority)

        route_protocol(1)

    @set_ev_cls(dpset.EventDP)
    def switch_events(self, ev):
        if ev.enter:
            print("Switch %d connected!" % ev.dp.id)
            self.switch_connected(ev.dp)
