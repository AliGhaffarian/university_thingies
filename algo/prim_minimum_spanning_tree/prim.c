#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "graph_ops.h"
#include "prim.h"
#include "defined_options.h"


int connects_selected_to_notselected(
				int*selected_vertices, 
				int src, 
				int dst)
{
		return selected_vertices[src] != selected_vertices[dst];
}

struct edge lightest_edge_from_selected_v_to_remaining_v(
				int *selected_vertices, 
				int **graph, 
				int size)
{
		struct edge res = make_default_edge();
		res.weight = MAX_EDGE_WEIGHT + 1;

		for( int i = 0; i < size; i++)
				for(int j = 0; j < size; j++)
						if( connects_selected_to_notselected(selected_vertices, i, j) 
							&& graph[i][j] != 0
							&& graph[i][j] < res.weight){
								res = (struct edge){
										.src = i,
										.dst = j,
										.weight = graph[i][j]
								};	
						}
#ifdef PRIM_DEBUG
		printf("%sselected node from %d to %d weight %d\n", PRIM_DEBUG_PREFIX, res.src, res.dst, res.weight);
#endif

		return res;
}

int **prim_minimum_spanning_tree(int **graph, int size)
{
		int **mst = malloc(size * sizeof(int*));
		for (int i = 0; i < size; i++){
				mst[i] = malloc(size * sizeof(int));
		}

		int *selected_vertices = malloc(size * sizeof(int));
		memset(selected_vertices, 0, size * sizeof(int));

		selected_vertices[rand() % size] = 1;
		int number_of_selected_vertices = 1;

#ifdef PRIM_DEBUG
		printf("%srandomly selected vertex : %d\n", PRIM_DEBUG_PREFIX, selected_vertices[0]);
#endif

		while (number_of_selected_vertices < size){
				struct edge lightest_edge = 
						lightest_edge_from_selected_v_to_remaining_v(
										selected_vertices, 
										graph, 
										size
										);

				set_bidirectional_edge(mst, lightest_edge);
				selected_vertices[lightest_edge.src] = 1;
				selected_vertices[lightest_edge.dst] = 1;
				number_of_selected_vertices++;
		}
	return mst;	
}
