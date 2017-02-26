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

        def match_action_add(match, action, priority):
            cmd = parser.OFPFlowMod(
                    datapath=sw, match=match, cookie=0,
                    command=ofproto.OFPFC_ADD, idle_timeout=0,
                    hard_timeout=0, priority=priority,
                    flags=ofproto.OFPFF_SEND_FLOW_REM, actions=[action])
            sw.send_msg(cmd)

        def route_protocol(base_priority, **spec):
            if sw_type == 1:  # edge switches

                for i in range(1, k / 2 + 1):
                    match = parser.OFPMatch(in_port=i, **spec)
                    action = parser.OFPActionOutput(i + k / 2)
                    match_action_add(match, action, 1100 + base_priority)

                # Downward
                base_dst = (10 << 24) + sw_id * (k / 2)
                for i in range(1, k / 2 + 1):
                    match = parser.OFPMatch(nw_dst=(base_dst + i), **spec)
                    action = parser.OFPActionOutput(i)
                    match_action_add(match, action, 1200 + base_priority)

            elif sw_type == 2:  # aggregation switches

                for i in range(1, k / 2 + 1):
                    match = parser.OFPMatch(in_port=i, **spec)
                    action = parser.OFPActionOutput(i + k / 2)
                    match_action_add(match, action, 1100 + base_priority)

                # Downward
                base_dst = (10 << 24) + sw_id / (k / 2) * pow(k / 2, 2)
                for i in range(1, pow(k / 2, 2) + 1):
                    match = parser.OFPMatch(nw_dst=(base_dst + i), **spec)
                    action = parser.OFPActionOutput((i - 1) / (k / 2) + 1)
                    match_action_add(match, action, 1200 + base_priority)

            else:  # core switches

                # Downward
                base_dst = 10 << 24
                for i in range(1,  pow(k / 2, 2) * k + 1):
                    match = parser.OFPMatch(nw_dst=(base_dst + i), **spec)
                    action = parser.OFPActionOutput((i - 1) / pow(k / 2, 2) + 1)
                    match_action_add(match, action, 1100 + base_priority)

        route_protocol(1, dl_type=ether.ETH_TYPE_IP)
        route_protocol(1, dl_type=ether.ETH_TYPE_ARP)

    @set_ev_cls(dpset.EventDP)
    def switch_events(self, ev):
        if ev.enter:
            print("Switch %d connected!" % ev.dp.id)
            self.switch_connected(ev.dp)
