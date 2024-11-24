#include "graph_ops.h"
#include "prim.h"
#include <stdio.h>
int main(){
		int graph_size = 0;
		int **graph = generate_random_graph(&graph_size);
		
		show_graph(graph, graph_size, 1);

		int **mst = prim_minimum_spanning_tree(graph, graph_size);
		printf("\n\n\n");
		
		show_graph(mst, graph_size, 1);

}
