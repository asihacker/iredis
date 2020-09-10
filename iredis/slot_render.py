"""
Render cluster slot map as ascii art

Block elements: https://en.wikipedia.org/wiki/Block_Elements
U+2588	█	Full block
U+2589	▉	Left seven eighths block
U+258A	▊	Left three quarters block
U+258B	▋	Left five eighths block
U+258C	▌	Left half block
U+258D	▍	Left three eighths block
U+258E	▎	Left one quarter block
U+258F	▏	Left one eighth block
"""

import logging

UNICODE_MARK = "▏▎▍▌▋▊▉█"
TOTAL_SLOT = 16384
logger = logging.getLogger(__name__)


class SlotCount:
    def __init__(self, host, count):
        self.host = host
        self.count = count

    def __repr__(self):
        return "{}({})".format(self.host, self.count)


class ColorPlate:
    SLOT_COLORS = ["#ff0066", "#44ff00", "#112233", "#ff1100", "#00ffaa"]

    def __init__(self):
        self.color = {}
        self.used_color = 0

    def color_for(self, host):

        if host in self.color:
            return self.color[host]

        self.used_color += 1
        if self.used_color >= len(self.SLOT_COLORS):
            self.used_color = 0
        self.color[host] = self.SLOT_COLORS[self.used_color]
        return self.color[host]


def render_block(block, plate):
    """8 slots are a block"""
    previous = []
    for slot in block:
        if previous and slot == previous[-1].host:
            previous[-1].count += 1
        else:
            previous.append(SlotCount(slot, 1))
    logger.debug("loading slots done, previous={}".format(previous))

    different_hosts_len = len(previous)

    if different_hosts_len == 1:
        return [(plate.color_for(previous[0].host), "█")]

    if different_hosts_len == 2:
        head_host, tail_host = previous[0].host, previous[1].host
        head_color, tail_color = plate.color_for(head_host), plate.color_for(tail_host)
        return [
            (
                "{} bg:{}".format(head_color, tail_color),
                UNICODE_MARK[previous[0].count - 1],
            )
        ]
    # more than 2 colors
    head_host, *middle_host, tail_host = previous
    result = []
    result.append(
        ("{}".format(plate.color_for(head_host.host)), UNICODE_MARK[head_host.count - 1],)
    )
    for host in middle_host + [tail_host]:
        result.append(
            ("{}".format(plate.color_for(host.host)), UNICODE_MARK[host.count - 1],)
        )
    return result



def render_slot_map(redis_cluster_solts_response):
    slot_in_host = [""] * TOTAL_SLOT
    plate = ColorPlate()

    for node in redis_cluster_solts_response:
        start_slot, end_slot, master_node, *_ = node
        host_ip = f"{master_node[0].decode()}:{master_node[1]}"
        slot_in_host[start_slot : end_slot + 1] = [host_ip] * (
            end_slot - start_slot + 1
        )
        logger.info(f"{start_slot} {end_slot} {master_node}")

    ascii_art_pairs = []


if __name__ == "__main__":
    print(
        render_block(
            [
                "127.0.0.1:7001",
                "127.0.0.1:7001",
                "127.0.0.1:7001",
                "127.0.0.1:7001",
                "127.0.0.1:7001",
                "127.0.0.1:7001",
                "127.0.0.1:7001",
                "127.0.0.1:7001",
            ],
            ColorPlate(),
        )
    )
    print(
        render_block(
            [
                "127.0.0.1:7000",
                "127.0.0.1:7001",
                "127.0.0.1:7001",
                "127.0.0.1:7001",
                "127.0.0.1:7002",
                "127.0.0.1:7002",
                "127.0.0.1:7002",
                "127.0.0.1:7002",
            ],
            ColorPlate(),
        )
    )
    print(
        render_block(
            [
                "127.0.0.1:7001",
                "127.0.0.1:7001",
                "127.0.0.1:7001",
                "127.0.0.1:7001",
                "127.0.0.1:7002",
                "127.0.0.1:7002",
                "127.0.0.1:7002",
                "127.0.0.1:7002",
            ],
            ColorPlate(),
        )
    )
