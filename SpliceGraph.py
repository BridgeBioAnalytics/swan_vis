import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import copy
from collections import defaultdict
import sqlite3
from utils import *

class SpliceGraph:
	def __init__(self, gtf=None, talon_db=None):

		if not gtf and not talon_db:
			raise Exception('No input to SpliceGraph given.')

		# GTF
		if gtf:
			if not os.path.exists(gtf):
				raise Exception('GTF file not found. Check path.')
			loc_df, edge_df, t_df = self.gtf_create_dfs(gtf)
		if talon_db: 
			if not os.path.exists(talon_db):
				raise Exception('TALON db file not found. Check path.')
			loc_df, edge_df, t_df = self.db_create_dfs(talon_db)

		self.G = self.create_graph_from_dfs(loc_df, edge_df, t_df)
		self.loc_df = loc_df
		self.edge_df = edge_df
		self.t_df = t_df

	# create loc_df (for nodes), edge_df (for edges), and t_df (for paths)
	def gtf_create_dfs(self, gtffile):

		# get dfs by parsing through gtf
		loc_df = pd.DataFrame(columns=['chrom', 'coord',
									   'strand','vertex_id',
									   'TSS', 'alt_TSS',
									   'TES', 'alt_TES',
									   'internal'])
		loc_df.set_index(['chrom', 'coord', 'strand'], inplace=True)

		edge_df = pd.DataFrame(columns=['edge_id', 'edge_type',
									    'strand', 'v1', 'v2'])
		t_df = pd.DataFrame(columns=['tid', 'gid',
									 'gname', 'path'])

		# loop initialization
		vertex_id = 0
		transcript_paths = []
		transcript_path = []

		with open(gtffile, 'r') as gtf:
			for line in gtf:

				# skip header lines
				if '##' in line: continue

				line = line.strip().split('\t')

				# gene entry 
				if line[2] == 'gene':
					curr_gid = utils.get_field_value('gene_id', line[-1])
					curr_gname = utils.get_field_value('gene_name', line[-1])

				# transcript entry
				elif line[2] == 'transcript':
					curr_tid = utils.get_field_value('transcript_id', line[-1])
					
					# start a new transcript path
					if transcript_path != []:

						# add to list of transcript paths and transcript df 
						transcript_paths.append(transcript_path)
						t_df = t_df.append({'tid': prev_tid,
									 'gid': prev_gid,
									 'gname': prev_gname,
									 'path': transcript_path},
									 ignore_index=True)

					transcript_path = []

					# reset some stuff
					terminal_loc = True
					exon = 0
					intron = 1

				# exon entry
				elif line[2] == 'exon':

					# get exon info 
					curr_chr = line[0]
					curr_start = line[3]
					curr_stop = line[4]
					curr_strand = line[6]
					
					if curr_strand == '+': coords = [curr_start, curr_stop]
					else: coords = [curr_stop, curr_start]
					
					for c in coords:

						ind = (curr_chr, int(c), curr_strand)

						# loc not in loc_df already
						if ind not in loc_df.index.tolist():

							# label as not a TSS/TES until further notice
							attr = {'vertex_id': vertex_id,	   
									'TSS': False, 'TES': False,
									'alt_TSS': False,
									'alt_TES': False, 
									'internal': False, 'coord': int(c),
									'strand': curr_strand, 'chrom': curr_chr}

							# update loc_df and increment vertex_id
							loc_df.reset_index(inplace=True)
							loc_df = loc_df.append(attr, ignore_index=True)
							loc_df.set_index(['chrom', 'coord', 'strand'], inplace=True)

							curr_loc = int(vertex_id)
							vertex_id += 1

						# loc was already added to graph
						else: curr_loc = int(loc_df.loc[ind].vertex_id)	
		
						# add an edge to previous loc if not terminal loc 
						# and if the edge doesn't already exist
						if not terminal_loc:
							curr_edge = (prev_loc, curr_loc)
							
							if curr_edge not in edge_df.edge_id.to_list():
								attrs = {'edge_id': (curr_edge[0], curr_edge[1]),
									     'v1': curr_edge[0],
										 'v2': curr_edge[1], 
										 'strand': curr_strand}
								if exon: attrs.update({'edge_type': 'exon'})
								elif intron: attrs.update({'edge_type': 'intron'})

								edge_df = edge_df.append(attrs, ignore_index=True)

						# update transcript path with each loc 
						transcript_path.append(curr_loc)
						prev_loc = curr_loc
						prev_tid = curr_tid
						prev_gid = curr_gid
						prev_gname = curr_gname
						terminal_loc = False
						
						# exon or intron
						exon = abs(exon-1)
						intron = abs(intron-1)
						
		# append last transcript info
		transcript_paths.append(transcript_path)
		t_df = t_df.append({'tid': curr_tid,
						    'gid': curr_gid,
						    'gname': curr_gname,
							'path': transcript_path},
							ignore_index=True)

		# label node/edge types and finish formatting dfs correctly
		loc_df.reset_index(inplace=True)
		loc_df = utils.create_dupe_index(loc_df, 'vertex_id')
		loc_df = utils.set_dupe_index(loc_df, 'vertex_id')
		loc_df = self.get_loc_types(loc_df, t_df)

		edge_df['annotated'] = True # we can assume that since we're working from a gtf, it's an annotation?? (maybe)
		loc_df['annotated'] = True

		t_df = utils.create_dupe_index(t_df, 'tid')
		t_df = utils.set_dupe_index(t_df, 'tid')
		edge_df.set_index('edge_id', inplace=True)

		return loc_df, edge_df, t_df

	# create loc_df (for nodes), edge_df (for edges), and t_df (for paths)
	def db_create_dfs(self, db):

		# open db connection
		conn = sqlite3.connect(db)
		c = conn.cursor()

		# loc_df
		q = 'SELECT loc.* FROM location loc'

		c.execute(q)
		locs = c.fetchall()

		loc_df = pd.DataFrame(locs,
			columns=['location_ID', 'genome_build',
					 'chrom', 'position'])

		# do some df reformatting, add strand
		loc_df.drop('genome_build', axis=1, inplace=True)
		loc_df.rename({'location_ID': 'vertex_id',
					   'position': 'coord'},
					   inplace=True, axis=1)
		loc_df.vertex_id = loc_df.vertex_id.map(int)

		# edge_df
		q = """SELECT e.* 
				FROM edge e 
				JOIN vertex V ON e.v1=v.vertex_ID 
				JOIN gene_annotations ga ON v.gene_ID=ga.ID 
				WHERE ga.attribute='gene_name'
			""" 

		c.execute(q)
		edges = c.fetchall()

		edge_df = pd.DataFrame(edges, 
			columns=['edge_id', 'v1', 'v2',
					 'edge_type', 'strand'])
		edge_df.v1 = edge_df.v1.map(int)
		edge_df.v2 = edge_df.v2.map(int)
		edge_df['talon_edge_id'] = edge_df.edge_id
		edge_df['edge_id'] = edge_df.apply(lambda x: (int(x.v1), int(x.v2)), axis=1)

		# t_df
		t_df = pd.DataFrame()

		# get tid, gid, gname, and paths
		q = """SELECT ga.value, ta.value,
					  t.start_exon, t.jn_path, t.end_exon,
					  t.start_vertex, t.end_vertex
				FROM gene_annotations ga 
				JOIN transcripts t ON ga.ID=t.gene_ID
				JOIN transcript_annotations ta ON t.transcript_ID=ta.ID
				WHERE ta.attribute='transcript_id'
				AND (ga.attribute='gene_name' 
				OR ga.attribute='gene_id')
			"""

		c.execute(q)
		data = c.fetchall()

		# get fields from each transcript and add to dataframe
		gids, tids, paths = zip(*[(i[0], i[1], i[2:]) for i in data[::2]])
		gnames = [i[0] for i in data[1::2]]
		paths = self.get_edge_paths(paths)

		t_df['tid'] = np.asarray(tids)
		t_df['gid'] = np.asarray(gids)
		t_df['gname'] = np.asarray(gnames)
		t_df['path'] = np.asarray(paths)

		t_df = utils.create_dupe_index(t_df, 'tid')
		t_df = utils.set_dupe_index(t_df, 'tid')

		# furnish the last bit of info in each df
		t_df['path'] = [[int(n) for n in path]
						 for path in self.get_vertex_paths(paths, edge_df)]
		loc_df['strand'] = loc_df.apply(lambda x:
				 self.get_strand(x, edge_df), axis=1)
		loc_df = utils.create_dupe_index(loc_df, 'vertex_id')
		loc_df = utils.set_dupe_index(loc_df, 'vertex_id')
		loc_df['internal'] = False
		loc_df['TSS'] = False
		loc_df['alt_TSS'] = False
		loc_df['TES'] = False
		loc_df['alt_TES'] = False
		loc_df['annotated'] = True
		loc_df = self.get_loc_types(loc_df, t_df)

		edge_df['annotated'] = True
		edge_df.drop('talon_edge_id', axis=1, inplace=True)
		edge_df = utils.create_dupe_index(edge_df, 'edge_id')
		edge_df = utils.set_dupe_index(edge_df, 'edge_id')

		return loc_df, edge_df, t_df

	# convert talon query into edge path
	def get_edge_paths(self, paths):
		edge_paths = []
		for p in paths:
			if p[1] == None:
				edge_paths.append([p[0]])
			else:
				edge_paths.append(
					[p[0], *[int(i) for i in p[1].split(',')], p[2]])
		return edge_paths

	# convert edge path to vertex path
	def get_vertex_paths(self, paths, edge_df):
		vertex_paths = []
		for p in paths: 
			path = []
			for i, e in enumerate(p): 
				entry = edge_df.loc[edge_df.talon_edge_id == e]
				if i == 0:
					path.extend([entry.v1.values[0], entry.v2.values[0]])
				else: path.append(entry.v2.values[0])
			vertex_paths.append(path)
		return vertex_paths

	# get the strand of each vertex
	def get_strand(self, x, edge_df):
		# use v1 or v2 depending on where vertex is in edge
		try: 
			strand = edge_df.loc[edge_df.v1 == x.vertex_id, 'strand'].values[0]
		except:
			strand = edge_df.loc[edge_df.v2 == x.vertex_id, 'strand'].values[0]
		return strand

	# add node types (internal, TSS, alt TSS, TES, alt_TES) to loc_df
	def get_loc_types(self, loc_df, t_df):

		# label each location as internal off the bat, and not as TSS/TES
		loc_df['internal'] = False
		loc_df['TSS'] = False
		loc_df['TES'] = False
		loc_df['alt_TSS'] = False
		loc_df['alt_TES'] = False

		# label each TSS and TES
		paths = t_df.path.tolist()
		tss = np.unique([path[0] for path in paths])
		loc_df.loc[tss, 'TSS'] = True
		tes = np.unique([path[-1] for path in paths])
		loc_df.loc[tes, 'TES'] = True
		internal = np.unique([n for path in paths for n in path[1:-1]])
		loc_df.loc[internal, 'internal'] = True

		# label each alt TSS and alt TES for each gene
		for g in t_df.gid.unique().tolist():
			gene_entries = t_df.loc[t_df.gid == g]

			# genes that have more than one transcript are alt TSS/TES candidates
			if len(gene_entries.index) != 1: 

				paths = gene_entries.path.tolist()
				tss = [path[0] for path in paths]
				tes = [path[-1] for path in paths]

				# alt TSS/TES
				if len(set(tss)) > 1: 
					loc_df.loc[tss, 'alt_TSS'] = True
				if len(set(tes)) > 1: 
					loc_df.loc[tes, 'alt_TES'] = True

		return loc_df

	# create the graph object from the dataframes
	def create_graph_from_dfs(self, loc_df, edge_df, t_df):

		# graph initialization
		G = nx.DiGraph()

		# add nodes to graph from transcript paths
		paths = t_df.path.tolist()
		for path in paths:
			nx.add_path(G, path)

		# add node attributes from dfs
		G = utils.label_nodes(G, loc_df, 'internal', 'internal') 
		G = utils.label_nodes(G, loc_df, 'TSS', 'TSS') 
		G = utils.label_nodes(G, loc_df, 'alt_TSS', 'alt_TSS') 
		G = utils.label_nodes(G, loc_df, 'TES', 'TES')
		G = utils.label_nodes(G, loc_df, 'alt_TES', 'alt_TES')
		G = utils.label_nodes(G, loc_df, 'coord', 'coord')
		G = utils.label_nodes(G, loc_df, 'annotated', 'annotated')
		G = utils.label_edges(G, edge_df, 'annotated', 'annotated')
		G = utils.label_edges(G, edge_df, 'strand', 'strand')
		G = utils.label_edges(G, edge_df, 'edge_type', 'edge_type')

		return G