#include "graph_ops.h"
#include "prim.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
int main(){
		int graph_size = 0;
		int **graph = generate_random_graph(&graph_size);
		
		printf("random generated graph:\n");
		show_graph(graph, graph_size, 1);

		int **mst = prim_minimum_spanning_tree(graph, graph_size);
		if(mst == (int **)0)
				exit(EINVAL);
		printf("\n\n\n");
		
		printf("minimum spanning tree:\n");
		show_graph(mst, graph_size, 1);

}
