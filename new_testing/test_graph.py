import pytest
import sys
import numpy as np
import swan_vis as swan
import networkx as nx
import math
import pandas as pd

###########################################################################
###################### Utilities in graph.py ##############################
###########################################################################
class TestGraph(object):

    # done
    # test get_ordered_id_map, dfs_to_dicts, dicts_to_dfs, update_loc_df_ids,
    # update_edge_df_ids, , create_graph_from_dfs, subset_on_gene

    # todo
    # order_edge_df, is_empty, has_novelty, check_datsets
    # subset_on_gene - ADD SUBSET FOR ABUNDANCE INFO

    # test check_datasets - dataset is in SwanGraph, non-list dataset
    def test_check_datasets_1(self):
        sg = swan.SwanGraph()
        sg.datasets = 'test1'
        query = 'test1'
        sg.check_datasets(query)

    # test check_datasets - datasets are in SwanGraph, list datasets
    def test_check_datasets_2(self):
        sg = swan.SwanGraph()
        sg.datasets = ['test1', 'test2']
        query = ['test1', 'test2']
        sg.check_datasets(query)

    # test check_datasets - dataset is not in the SwanGraph
    def test_check_datasets_3(self):
        sg = swan.SwanGraph()
        sg.datasets = ['test1', 'test2']
        query = 'test3'
        with pytest.raises(Exception) as e:
            sg.check_datasets(query)
        assert 'Dataset test3 not' in str(e.value)



    # test get_ordered_id_map
    # should order locations by their chromosome, and coordinate
    # make sure that it fixes a) out of order chromosomes b) out of order coords
    def test_get_ordered_id_map(self):
        sg = swan.SwanGraph()

        # loc
        data = [[0, 'chr3', 20],
                [1, 'chr1', 500],
                [2, 'chr1', 20]]
        cols = ['vertex_id', 'chrom', 'coord']
        sg.loc_df = pd.DataFrame(data=data, columns=cols)
        id_map = sg.get_ordered_id_map()
        ctrl_id_map = {2: 0, 1: 1, 0: 2}
        assert id_map == ctrl_id_map

    # test dicts_to_dfs
    def test_dicts_to_dfs(self):
        sg = swan.SwanGraph()
        # loc
        data = [[0, 'chr3', 20],
             [1, 'chr1', 500],
             [2, 'chr1', 20]]
        cols = ['vertex_id', 'chrom', 'coord']
        ctrl_loc_df = pd.DataFrame(data=data, columns=cols)
        ctrl_loc_df.set_index('vertex_id', inplace=True)
        sg.loc_df = {0: {'chrom': 'chr3', 'coord': 20},
                     1: {'chrom': 'chr1', 'coord': 500},
                     2: {'chrom': 'chr1', 'coord': 20}}

        # edge
        data = [[0, 0, 1],
                [1, 1, 2],
                [2, 0, 2]]
        cols = ['edge_id', 'v1', 'v2']
        ctrl_edge_df = pd.DataFrame(data=data, columns=cols)
        ctrl_edge_df.set_index('edge_id', inplace=True)
        sg.edge_df = {0: {'v1': 0, 'v2': 1},
                      1: {'v1': 1, 'v2': 2},
                      2: {'v1': 0, 'v2': 2}}

        # t
        data = [[0, [0,1], [0,1,2]],
                [1, [2], [0,2]]]
        cols = ['tid', 'path', 'loc_path']
        ctrl_t_df = pd.DataFrame(data=data, columns=cols)
        ctrl_t_df.set_index('tid', inplace=True)
        sg.t_df = {0: {'path': [0,1], 'loc_path': [0,1,2]},
                   1: {'path': [2], 'loc_path': [0,2]}}

        sg.dicts_to_dfs()

        check_dfs(sg.loc_df, ctrl_loc_df,
                  sg.edge_df, ctrl_edge_df,
                  sg.t_df, ctrl_t_df)

    # test dfs_to_dicts
    def test_dfs_to_dicts(self):
        sg = swan.SwanGraph()

        # loc
        data = [[0, 'chr3', 20],
             [1, 'chr1', 500],
             [2, 'chr1', 20]]
        cols = ['vertex_id', 'chrom', 'coord']
        sg.loc_df = pd.DataFrame(data=data, columns=cols)
        sg.loc_df = swan.set_dupe_index(sg.loc_df, 'vertex_id')

        ctrl_loc_df = {0: {'chrom': 'chr3', 'coord': 20},
                       1: {'chrom': 'chr1', 'coord': 500},
                       2: {'chrom': 'chr1', 'coord': 20}}

        # edge
        data = [[0, 0, 1],
                [1, 1, 2],
                [2, 0, 2]]
        cols = ['edge_id', 'v1', 'v2']
        sg.edge_df = pd.DataFrame(data=data, columns=cols)
        sg.edge_df = swan.set_dupe_index(sg.edge_df, 'edge_id')
        ctrl_edge_df = {0: {'v1': 0, 'v2': 1},
                        1: {'v1': 1, 'v2': 2},
                        2: {'v1': 0, 'v2': 2}}

        # t
        data = [[0, [0,1], [0,1,2]],
                [1, [2], [0,2]]]
        cols = ['tid', 'path', 'loc_path']
        sg.t_df = pd.DataFrame(data=data, columns=cols)
        sg.t_df = swan.set_dupe_index(sg.t_df, 'tid')
        ctrl_t_df = {0: {'path': [0,1], 'loc_path': [0,1,2]},
                     1: {'path': [2], 'loc_path': [0,2]}}

        sg.dfs_to_dicts()

        print('t_df')
        print('test')
        print(sg.t_df)
        print('control')
        print(ctrl_t_df)
        assert ctrl_t_df == sg.t_df

        print('edge_df')
        print('test')
        print(sg.edge_df)
        print('control')
        print(ctrl_edge_df)
        assert ctrl_edge_df == sg.edge_df

        print('loc_df')
        print('test')
        print(sg.loc_df)
        print('control')
        print(ctrl_loc_df)
        assert ctrl_loc_df == sg.loc_df

    # tests update_loc_df_ids
    def test_update_loc_df_ids(self):
        sg = swan.SwanGraph()

        # loc
        sg.loc_df = {0: {'chrom': 'chr3', 'coord': 20},
                     1: {'chrom': 'chr1', 'coord': 500},
                     2: {'chrom': 'chr1', 'coord': 20}}
        id_map = {2: 0, 1: 1, 0: 2}
        sg.update_loc_df_ids(id_map, False)
        ctrl_loc_df = {2: {'chrom': 'chr3', 'coord': 20, 'vertex_id': 2},
                       1: {'chrom': 'chr1', 'coord': 500, 'vertex_id': 1},
                       0: {'chrom': 'chr1', 'coord': 20, 'vertex_id': 0}}

        display_test_ctrl(sg.loc_df, ctrl_loc_df)
        assert sg.loc_df == ctrl_loc_df

    # tests update_edge_df_ids
    def test_update_edge_df_ids(self):
        sg = swan.SwanGraph()
        id_map = {2: 0, 1: 1, 0: 2}
        sg.edge_df = {0: {'v1': 0, 'v2': 1},
                      1: {'v1': 1, 'v2': 2},
                      2: {'v1': 0, 'v2': 2}}
        ctrl_edge_df = {0: {'v1': 2, 'v2': 1, 'edge_id': 0},
                        1: {'v1': 1, 'v2': 0, 'edge_id': 1},
                        2: {'v1': 2, 'v2': 0, 'edge_id': 2}}
        sg.update_edge_df_ids(id_map, False)
        display_test_ctrl(sg.edge_df, ctrl_edge_df)
        assert sg.edge_df == ctrl_edge_df

    # tests get_loc_path
    def get_loc_path(self):
        sg = swan.SwanGraph()
        data = [[0, [0,1]],
                [1, [2,3]],
                 [2, [4,5]]]
        sg.t_df = pd.DataFrame(data=data, columns=['tid', 'path'])

        data = [[0,0,1], [1,1,2], [2,2,3], [3,3,4],
                [4,4,5], [5,5,6]]
        sg.edge_df = pd.DataFrame(data=data, columns=['edge_id', 'v1', 'v2'])

        data = [0,1,2,3,4,5,6]
        sg.loc_df = pd.DataFrame(data=data, columns=['vertex_id'])

        sg.get_loc_path()

        ctrl_loc_paths = [[0,1,2],[3,4,5],[6,7,8]]
        loc_paths = sg.t_df.loc_path.tolist()
        assert ctrl_loc_paths == loc_paths

    # tests update_ids with id_map=None
    def test_update_ids(self):
        sg = swan.SwanGraph()

        # loc
        data = [[0, 'chr3', 20],
             [1, 'chr1', 500],
             [2, 'chr1', 20]]
        cols = ['vertex_id', 'chrom', 'coord']
        sg.loc_df = pd.DataFrame(data=data, columns=cols)
        sg.loc_df = swan.create_dupe_index(sg.loc_df, 'vertex_id')
        sg.loc_df = swan.set_dupe_index(sg.loc_df, 'vertex_id')
        # ctrl_id_map = {2: 0, 1: 1, 0: 2}
        data = [[2, 'chr3', 20],
                       [1, 'chr1', 500],
                       [0, 'chr1', 20]]
        cols = ['vertex_id', 'chrom', 'coord']
        ctrl_loc_df = pd.DataFrame(data=data, columns=cols)
        ctrl_loc_df = swan.create_dupe_index(ctrl_loc_df, 'vertex_id')
        ctrl_loc_df = swan.set_dupe_index(ctrl_loc_df, 'vertex_id')

        # edge
        data = [[0, 0, 1],
                [1, 1, 2],
                [2, 0, 2]]
        cols = ['edge_id', 'v1', 'v2']
        sg.edge_df = pd.DataFrame(data=data, columns=cols)
        sg.edge_df = swan.create_dupe_index(sg.edge_df, 'edge_id')
        sg.edge_df = swan.set_dupe_index(sg.edge_df, 'edge_id')
        # ctrl_id_map = {2: 0, 1: 1, 0: 2}
        data = [[0, 2, 1],
                [1, 1, 0],
                [2, 2, 0]]
        cols = ['edge_id', 'v1', 'v2']
        ctrl_edge_df = pd.DataFrame(data=data, columns=cols)
        ctrl_edge_df = swan.create_dupe_index(ctrl_edge_df, 'edge_id')
        ctrl_edge_df = swan.set_dupe_index(ctrl_edge_df, 'edge_id')

        # t
        data = [[0, [0,1], [0,1,2]],
                [1, [2], [0,2]]]
        cols = ['tid', 'path', 'loc_path']
        sg.t_df = pd.DataFrame(data=data, columns=cols)
        sg.t_df = swan.create_dupe_index(sg.t_df, 'tid')
        sg.t_df = swan.set_dupe_index(sg.t_df, 'tid')        # ctrl_id_map = {2: 0, 1: 1, 0: 2}
        data = [[0, [0,1], [2,1,0]],
                [1, [2], [2,0]]]
        cols = ['tid', 'path', 'loc_path']
        ctrl_t_df = pd.DataFrame(data=data, columns=cols)
        ctrl_t_df = swan.create_dupe_index(ctrl_t_df, 'tid')
        ctrl_t_df = swan.set_dupe_index(ctrl_t_df, 'tid')

        sg.update_ids()
        check_dfs(sg.loc_df, ctrl_loc_df,
                  sg.edge_df, ctrl_edge_df,
                  sg.t_df, ctrl_t_df)

    # tests update_ids with a given id_map
    def test_update_ids_id_map(self):
        sg = swan.SwanGraph()

        # loc
        data = [[0, 'chr3', 20],
             [1, 'chr1', 500],
             [2, 'chr1', 20]]
        cols = ['vertex_id', 'chrom', 'coord']
        sg.loc_df = pd.DataFrame(data=data, columns=cols)
        sg.loc_df = swan.create_dupe_index(sg.loc_df, 'vertex_id')
        sg.loc_df = swan.set_dupe_index(sg.loc_df, 'vertex_id')
        # id_map = {2: 7, 1: 5, 0: 6}
        data = [[6, 'chr3', 20],
                       [5, 'chr1', 500],
                       [7, 'chr1', 20]]
        cols = ['vertex_id', 'chrom', 'coord']
        ctrl_loc_df = pd.DataFrame(data=data, columns=cols)
        ctrl_loc_df = swan.create_dupe_index(ctrl_loc_df, 'vertex_id')
        ctrl_loc_df = swan.set_dupe_index(ctrl_loc_df, 'vertex_id')

        # edge
        data = [[0, 0, 1],
                [1, 1, 2],
                [2, 0, 2]]
        cols = ['edge_id', 'v1', 'v2']
        sg.edge_df = pd.DataFrame(data=data, columns=cols)
        sg.edge_df = swan.create_dupe_index(sg.edge_df, 'edge_id')
        sg.edge_df = swan.set_dupe_index(sg.edge_df, 'edge_id')
        # id_map = {2: 7, 1: 5, 0: 6}
        data = [[0, 6, 5],
                [1, 5, 7],
                [2, 6, 7]]
        cols = ['edge_id', 'v1', 'v2']
        ctrl_edge_df = pd.DataFrame(data=data, columns=cols)
        ctrl_edge_df = swan.create_dupe_index(ctrl_edge_df, 'edge_id')
        ctrl_edge_df = swan.set_dupe_index(ctrl_edge_df, 'edge_id')

        # t
        data = [[0, [0,1], [0,1,2]],
                [1, [2], [0,2]]]
        cols = ['tid', 'path', 'loc_path']
        sg.t_df = pd.DataFrame(data=data, columns=cols)
        sg.t_df = swan.create_dupe_index(sg.t_df, 'tid')
        sg.t_df = swan.set_dupe_index(sg.t_df, 'tid')
        # id_map = {2: 7, 1: 5, 0: 6}
        data = [[0, [0,1], [6,5,7]],
                [1, [2], [6,7]]]
        cols = ['tid', 'path', 'loc_path']
        ctrl_t_df = pd.DataFrame(data=data, columns=cols)
        ctrl_t_df = swan.create_dupe_index(ctrl_t_df, 'tid')
        ctrl_t_df = swan.set_dupe_index(ctrl_t_df, 'tid')

        id_map = {2: 7, 1: 5, 0: 6}
        sg.update_ids(id_map=id_map)
        check_dfs(sg.loc_df, ctrl_loc_df,
                  sg.edge_df, ctrl_edge_df,
                  sg.t_df, ctrl_t_df)


    # tests create_graph_from_dfs
    def test_create_graph_from_dfs(self):
        sg = swan.SwanGraph()

        data = [[0, 'chr3', 20],
             [1, 'chr1', 500],
             [2, 'chr1', 20]]
        cols = ['vertex_id', 'chrom', 'coord']
        sg.loc_df = pd.DataFrame(data=data, columns=cols)
        sg.loc_df = swan.create_dupe_index(sg.loc_df, 'vertex_id')
        sg.loc_df = swan.set_dupe_index(sg.loc_df, 'vertex_id')
        data = [[2, 'chr3', 20],
                       [1, 'chr1', 500],
                       [0, 'chr1', 20]]
        cols = ['vertex_id', 'chrom', 'coord']

        # edge
        data = [[0, 0, 1],
                [1, 1, 2],
                [2, 0, 2]]
        cols = ['edge_id', 'v1', 'v2']
        sg.edge_df = pd.DataFrame(data=data, columns=cols)
        sg.edge_df = swan.create_dupe_index(sg.edge_df, 'edge_id')
        sg.edge_df = swan.set_dupe_index(sg.edge_df, 'edge_id')

        # t
        data = [[0, [0,1], [0,1,2]],
                [1, [2], [0,2]]]
        cols = ['tid', 'path', 'loc_path']
        sg.t_df = pd.DataFrame(data=data, columns=cols)
        sg.t_df = swan.create_dupe_index(sg.t_df, 'tid')
        sg.t_df = swan.set_dupe_index(sg.t_df, 'tid')

        sg.create_graph_from_dfs()

        ctrl_locs = [0,1,2]
        ctrl_edges = [(0,1), (0,2), (1,2)]

        display_test_ctrl(list(sg.G.nodes), ctrl_locs, 'graph nodes')
        assert set(list(sg.G.nodes)) == set(ctrl_locs)

        display_test_ctrl(sg.G.edges, ctrl_edges, 'graph edges')
        assert set(sg.G.edges) == set(ctrl_edges)

    # tests subset_on_gene_1
    def test_subset_on_gene_1(self):
        sg = swan.SwanGraph()

        # loc_df
        data = [[0, 1, 0],
                [1, 1, 1],
                [2, 1, 2],
                [3, 1, 3],
                [4, 1, 4],
                [5, 1, 5],
                [6, 1, 6]]
        cols = ['vertex_id', 'chrom', 'coord']
        sg.loc_df = pd.DataFrame(data=data, columns=cols)
        sg.loc_df = swan.create_dupe_index(sg.loc_df, 'vertex_id')
        sg.loc_df = swan.set_dupe_index(sg.loc_df, 'vertex_id')

        data = [[0, 1, 0],
                [1, 1, 1],
                [2, 1, 2],
                [3, 1, 3]]
        cols = ['vertex_id', 'chrom', 'coord']
        ctrl_loc_df = pd.DataFrame(data=data, columns=cols)
        ctrl_loc_df = swan.create_dupe_index(ctrl_loc_df, 'vertex_id')
        ctrl_loc_df = swan.set_dupe_index(ctrl_loc_df, 'vertex_id')

        # edge_df
        data = [[0, 0, 1],
                [1, 1, 2],
                [2, 2, 3],
                [3, 0, 3],
                [4, 4, 5],
                [5, 5, 6],
                [6, 1, 4]]
        cols = ['edge_id', 'v1', 'v2']
        sg.edge_df = pd.DataFrame(data=data, columns=cols)
        sg.edge_df = swan.create_dupe_index(sg.edge_df, 'edge_id')
        sg.edge_df = swan.set_dupe_index(sg.edge_df, 'edge_id')

        data = [[0, 0, 1],
                [1, 1, 2],
                [2, 2, 3],
                [3, 0, 3]]
        cols = ['edge_id', 'v1', 'v2']
        ctrl_edge_df = pd.DataFrame(data=data, columns=cols)
        ctrl_edge_df = swan.create_dupe_index(ctrl_edge_df, 'edge_id')
        ctrl_edge_df = swan.set_dupe_index(ctrl_edge_df, 'edge_id')

        # t_df
        data = [[0, 1, [0,1,2], [0,1,2,3]],
                [1, 1, [3], [0,3]],
                [2, 2, [4,5], [1,4,5,6]]]
        cols = ['tid', 'gid', 'path', 'loc_path']
        sg.t_df = pd.DataFrame(data=data, columns=cols)
        sg.t_df = swan.create_dupe_index(sg.t_df, 'tid')
        sg.t_df = swan.set_dupe_index(sg.t_df, 'tid')

        data = [[0, 1, [0,1,2], [0,1,2,3]],
                [1, 1, [3], [0,3]]]
        cols = ['tid', 'gid', 'path', 'loc_path']
        ctrl_t_df = pd.DataFrame(data=data, columns=cols)
        ctrl_t_df = swan.create_dupe_index(ctrl_t_df, 'tid')
        ctrl_t_df = swan.set_dupe_index(ctrl_t_df, 'tid')

        sg_subset = sg.subset_on_gene(1)

        check_dfs(sg_subset.loc_df, ctrl_loc_df,
                  sg_subset.edge_df, ctrl_edge_df,
                  sg_subset.t_df, ctrl_t_df)

    # tests subset_on_gene_2
    def test_subset_on_gene_2(self):
        sg = swan.SwanGraph()

        # loc_df
        data = [[0, 1, 0],
                [1, 1, 1],
                [2, 1, 2],
                [3, 1, 3],
                [4, 1, 4],
                [5, 1, 5],
                [6, 1, 6]]
        cols = ['vertex_id', 'chrom', 'coord']
        sg.loc_df = pd.DataFrame(data=data, columns=cols)
        sg.loc_df = swan.create_dupe_index(sg.loc_df, 'vertex_id')
        sg.loc_df = swan.set_dupe_index(sg.loc_df, 'vertex_id')

        # data = [[0, 1, 0],
        #         [0 (1), 1, 1],
        #         [2, 1, 2],
        #         [3, 1, 3],
        #         [1 (4), 1, 4],
        #         [2 (5), 1, 5],
        #         [3 (6), 1, 6]]
        data = [[0, 1, 1],
                [1, 1, 4],
                [2, 1, 5],
                [3, 1, 6]]
        cols = ['vertex_id', 'chrom', 'coord']
        ctrl_loc_df = pd.DataFrame(data=data, columns=cols)
        ctrl_loc_df = swan.create_dupe_index(ctrl_loc_df, 'vertex_id')
        ctrl_loc_df = swan.set_dupe_index(ctrl_loc_df, 'vertex_id')

        # edge_df
        data = [[0, 0, 1],
                [1, 0, 1],
                [2, 2, 3],
                [3, 0, 3],
                [4, 4, 5],
                [5, 5, 6],
                [6, 1, 4]]
        cols = ['edge_id', 'v1', 'v2']
        sg.edge_df = pd.DataFrame(data=data, columns=cols)
        sg.edge_df = swan.create_dupe_index(sg.edge_df, 'edge_id')
        sg.edge_df = swan.set_dupe_index(sg.edge_df, 'edge_id')

        # data = [[0, 0, 1],
        #         [1, 1, 2],
        #         [2, 2, 3],
        #         [3, 0, 3],
        #         [4, 1(4), 2(5)],
        #         [5, 2(5), 3(6)],
        #         [6, 0(1), 1(4)]]
        data = [[4, 1, 2],
                [5, 2, 3],
                [6, 0, 1]]
        cols = ['edge_id', 'v1', 'v2']
        ctrl_edge_df = pd.DataFrame(data=data, columns=cols)
        ctrl_edge_df = swan.create_dupe_index(ctrl_edge_df, 'edge_id')
        ctrl_edge_df = swan.set_dupe_index(ctrl_edge_df, 'edge_id')

        # t_df
        data = [[0, 1, [0,1,2], [0,1,2,3]],
                [1, 1, [3], [0,3]],
                [2, 2, [6,4,5], [1,4,5,6]]]
        cols = ['tid', 'gid', 'path', 'loc_path']
        sg.t_df = pd.DataFrame(data=data, columns=cols)
        sg.t_df = swan.create_dupe_index(sg.t_df, 'tid')
        sg.t_df = swan.set_dupe_index(sg.t_df, 'tid')

        data = [[2, 2, [6,4,5], [0,1,2,3]]]
        cols = ['tid', 'gid', 'path', 'loc_path']
        ctrl_t_df = pd.DataFrame(data=data, columns=cols)
        ctrl_t_df = swan.create_dupe_index(ctrl_t_df, 'tid')
        ctrl_t_df = swan.set_dupe_index(ctrl_t_df, 'tid')

        sg_subset = sg.subset_on_gene(2)

        check_dfs(sg_subset.loc_df, ctrl_loc_df,
                  sg_subset.edge_df, ctrl_edge_df,
                  sg_subset.t_df, ctrl_t_df)

def display_test_ctrl(test, ctrl, kind=None):
    if kind:
        print(kind)
    print('control')
    print(ctrl)
    print('test')
    print(test)

def check_dfs(loc_df, ctrl_loc_df,
              edge_df, ctrl_edge_df,
              t_df, ctrl_t_df):

    # first order to make them comparable
    # sort all values by their IDs
    loc_df.sort_index(inplace=True)
    edge_df.sort_index(inplace=True)
    t_df.sort_index(inplace=True)
    ctrl_loc_df.sort_index(inplace=True)
    ctrl_edge_df.sort_index(inplace=True)
    ctrl_t_df.sort_index(inplace=True)

    # and order columns the same way
    ctrl_loc_df = ctrl_loc_df[loc_df.columns]
    ctrl_edge_df = ctrl_edge_df[edge_df.columns]
    ctrl_t_df = ctrl_t_df[t_df.columns]

    print('test')
    print(loc_df)
    print('control')
    print(ctrl_loc_df)
    print(ctrl_loc_df == loc_df)
    assert (loc_df == ctrl_loc_df).all(axis=0).all()

    print('test')
    print(edge_df)
    print('control')
    print(ctrl_edge_df)
    assert (edge_df == ctrl_edge_df).all(axis=0).all()

    print('test')
    print(t_df)
    print('control')
    print(ctrl_t_df)
    assert (t_df == ctrl_t_df).all(axis=0).all()