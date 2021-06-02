import pytest
import sys
import numpy as np
import swan_vis as swan
import networkx as nx
import math
import pandas as pd

###########################################################################
###################### Related to data analysis ############################
###########################################################################
class TestSGAnalysis(object):

# tests find_ir_genes, find_es_genes

    # tests find_ir_genes - requires edges to be in order...
    # also requires the swangraph
    def test_find_ir_genes(self):
        sg = swan.SwanGraph()
        sg.annotation = True

        # t_df
        data = [[0, [0,1,2], True, 'g1', 't1'],
                [1, [3], False, 'g1', 't2']]
        cols = ['vertex_id', 'path', 'annotation', 'gid', 'tid']
        sg.t_df = pd.DataFrame(data=data, columns=cols)

        # edge
        data = [[0, 'exon', True, 0, 1],
                [1, 'intron', True, 1, 2],
                [2, 'exon', True, 2, 3],
                [3, 'exon', False, 0, 3]]
        cols = ['edge_id', 'edge_type', 'annotation', 'v1', 'v2']
        sg.edge_df = pd.DataFrame(data=data, columns=cols)

        # loc
        data = [0,1,2,3]
        cols = ['vertex_id']
        sg.loc_df = pd.DataFrame(data=data, columns=cols)

        ctrl_edges = [3]
        ctrl_tids = ['t2']
        ctrl_gids = ['g1']

        sg.get_loc_path()
        sg.create_graph_from_dfs()
        gids, tids, edges = sg.find_ir_genes()

        print('edges')
        print('control')
        print(ctrl_edges)
        print('test')
        print(edges)
        assert set(ctrl_edges) == set(edges)

        print('transcripts')
        print('control')
        print(ctrl_tids)
        print('test')
        print(tids)
        assert set(ctrl_tids) == set(tids)

        print('genes')
        print('control')
        print(ctrl_gids)
        print('test')
        print(gids)
        assert set(ctrl_gids) == set(gids)
