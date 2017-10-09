# -*- coding: utf-8 -*-

__author__ = 'ogaidukov'

import unittest
import logging
from prefix_tree.tree import Prefix, BPlusPrefixTree


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


class SimpleTreeTestCase(unittest.TestCase):
    prefixes = [
        Prefix(u'0.0.0.0/28', data='p1'),
        Prefix(u'0.0.0.16/28', data='p2'),
        Prefix(u'0.0.0.4/30', data='p3'),
        Prefix(u'0.0.0.32/27', data='p4'),
        Prefix(u'0.0.0.22/31', data='p5'),
        Prefix(u'0.0.0.48/28', data='p6'),
        Prefix(u'0.0.0.48/30', data='p7'),
        Prefix(u'0.0.0.55/32', data='p8'),
        Prefix(u'0.0.0.32/29', data='p9')
    ]

    def test_tree_search(self):
        tree = BPlusPrefixTree(arity=3)
        for p in self.prefixes:
            tree.insert(p)
            self.assertEqual(1, 1)
        logger.debug(tree._root)

        search_data = {
            0: 'p1',
            3: 'p1',
            4: 'p3',
            7: 'p3',
            8: 'p1',
            15: 'p1',
            16: 'p2',
            21: 'p2',
            22: 'p5',
            23: 'p5',
            24: 'p2',
            31: 'p2',
            32: 'p9',
            39: 'p9',
            40: 'p4',
            47: 'p4',
            48: 'p7',
            51: 'p7',
            52: 'p6',
            54: 'p6',
            55: 'p8',
            56: 'p6',
            62: 'p6'
        }

        for i in xrange(0, 70):
            s = Prefix(i)
            p = tree.search(s)
            if p:
                logging.debug("{} - {} ({})".format(i, p, p.data))
            else:
                logging.debug("{} - None".format(i))

        for i in search_data:
            s = Prefix(i)
            p = tree.search(s)
            self.assertEqual(search_data[i], p.data, msg="different at {} index".format(i))
