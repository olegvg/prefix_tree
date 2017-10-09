# -*- coding: utf-8 -*-

from __future__ import division

__author__ = 'ogaidukov'

from bisect import bisect_left, bisect_right
import ipaddress


# total_ordering is not necessary because bisect uses __lt__ and algorithm itself uses __eq__ only
# @total_ordering
class Prefix(object):
    def __init__(self, prefix_def, strict=False, prefix_type='IPv4', data=None):
        self.data = data
        self.prefix_type = prefix_type
        if self.prefix_type == 'IPv4':
            self._prefix = ipaddress.IPv4Network(prefix_def, strict=strict)
        elif self.prefix_type == 'IPv6':
            self._prefix = ipaddress.IPv6Network(prefix_def, strict=strict)
        else:
            self._prefix = None
            return
        self.network_address = self._prefix.network_address
        self.broadcast_address = self._prefix.broadcast_address

    def check_right_instance(self, inst):
        if self.prefix_type != inst.prefix_type:
            raise TypeError

    def covers(self, other):
        """
        Checks whether self covers other
        :param other: Other network represented by IPvxNetwork
        :return: boolean value
        """
        self.check_right_instance(other)
        if self.network_address <= other.network_address and self.broadcast_address >= other.broadcast_address:
            return True
        else:
            return False

    def __lt__(self, other):
        """
        Checks whether self is less than other
        :param other: Other network represented by IPvxNetwork
        :return: boolean value
        """
        self.check_right_instance(other)
        if int(self.network_address) < int(other.network_address) or \
                int(self.network_address) == int(other.network_address) and \
                int(self.broadcast_address) > int(other.broadcast_address):
            return True
        else:
            return False

    def __eq__(self, other):
        self.check_right_instance(other)
        if int(self.network_address) == int(other.network_address) and \
                int(self.broadcast_address) == int(other.broadcast_address):
            return True
        else:
            return False

    def __repr__(self):
        return "{}-{}".format(int(self.network_address), int(self.broadcast_address), self.data)

    __str__ = __repr__


class BPlusPrefixTreeNode(object):
    def __init__(self):
        self.keys = []       # sorted array of keys which are Prefix objects
        self.children = []   # sorted array of children which are MMSPTNode objects
        self.cover = []      # sorted array of prefixes which cover keys. See Prefix.covers()

    def __repr__(self):
        return "<keys: {}, children: {}, cover: {}>".format(self.keys, self.children, self.cover)


class BPlusPrefixTree(object):
    def __init__(self, arity=16):
        self._root = BPlusPrefixTreeNode()
        self.arity = arity
        self.split_pos = int(arity/2+.5)

    def search(self, address):
        node = self._root
        cover_collection = []
        while True:
            search_idx = bisect_right(node.keys, address)
            if search_idx > 0 and node.keys[search_idx-1].covers(address):
                return node.keys[search_idx-1]
            if len(node.cover) > 0:
                cover_collection[0:0] = node.cover
            if 0 < len(node.children) > search_idx:
                node = node.children[search_idx]
            else:
                break
        for cover_prefix in reversed(cover_collection):
            if cover_prefix.covers(address):
                return cover_prefix
        return None

    def insert(self, prefix):
        node = self._root
        bottom_up_chain = [[0, self._root]]
        while True:
            bisect_pos = bisect_left(node.keys, prefix)
            if bisect_pos > 0:
                bisect_prefix = node.keys[bisect_pos-1]
                if prefix.covers(bisect_prefix):
                    node.cover.append(prefix)
                    return
                if bisect_prefix == prefix:
                    node.keys[bisect_pos] = prefix
                    return
                if bisect_prefix.covers(prefix):
                    node.cover.append(bisect_prefix)
                    node.keys[bisect_pos-1] = prefix
                    return
            if bisect_pos < len(node.children):
                next_child = node.children[bisect_pos]
                bottom_up_chain.insert(0, [bisect_pos, next_child])
                node = next_child
            else:
                node.keys.insert(bisect_pos, prefix)
                break

        for idx, (pos, inode) in enumerate(bottom_up_chain):
            if len(inode.keys) == self.arity:
                right_child = BPlusPrefixTreeNode()
                right_child.keys.extend(inode.keys[self.split_pos:])
                del inode.keys[self.split_pos:]

                if idx+1 == len(bottom_up_chain):
                    # create the new root of tree
                    parent_node = BPlusPrefixTreeNode()
                    self._root = parent_node
                    parent_node.children.append(inode)
                else:
                    (_, parent_node) = bottom_up_chain[idx+1]

                middle_key = inode.keys.pop()
                parent_node.keys.insert(pos, middle_key)
                parent_node.children.append(right_child)

                # check the order of inode.cover array and split if necessary
                orig_cover = inode.cover[:]
                inode.cover = []
                for c in orig_cover:
                    if c.covers(middle_key):
                        parent_node.cover.append(c)
                        continue
                    if [True for x in right_child.keys if c.covers(x)]:
                        right_child.cover.append(c)
                        continue
                    if [True for x in inode.keys if c.covers(x)]:
                        inode.cover.append(c)


if __name__ == '__main__':
    # lst = range(0, 10)
    # print lst
    # print lst[-4::-1]
    # exit()

    p1 = Prefix(u'0.0.0.0/28', data='p1')
    p2 = Prefix(u'0.0.0.16/28', data='p2')
    p3 = Prefix(u'0.0.0.4/30', data='p3')
    p4 = Prefix(u'0.0.0.32/27', data='p4')
    p5 = Prefix(u'0.0.0.22/31', data='p5')
    p6 = Prefix(u'0.0.0.48/28', data='p6')
    p7 = Prefix(u'0.0.0.48/30', data='p7')
    p8 = Prefix(u'0.0.0.55/32', data='p8')
    p9 = Prefix(u'0.0.0.32/29', data='p9')
#    print p1, p2, p3, p4, p5, p6, p7, p8, p9

    bppt = BPlusPrefixTree(arity=3)
    bppt.insert(p1)     #
    bppt.insert(p2)     #
    bppt.insert(p3)
    bppt.insert(p4)     #
    bppt.insert(p5)
    bppt.insert(p6)     #
    bppt.insert(p7)
    bppt.insert(p8)
    bppt.insert(p9)
    # mmspt.insert(Prefix('0.0.0.0/32', data='boom'))
    print bppt._root

    for i in xrange(0, 70):
        s = Prefix(i)
        p = bppt.search(s)
        if p:
            print "{} - {} ({})".format(i, p, p.data)
        else:
            print "{} - None".format(i)

