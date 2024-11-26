#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "graph_ops.h"
#include "defined_options.h"
void print_delim_ver(int times){
		int j = 0;
		printf("\n");
		while( j++ < times) printf("%s", SHOW_GRAPH_DELIM_VER);
		printf("\n");
}
void show_graph(int ** graph, int size, int weighted){
		int i, j;
		int to_print;

		printf(" %s", SHOW_GRAPH_DELIM_HOR);
		for(i = 0; i < size; i++)
				printf("%d%s", i, SHOW_GRAPH_DELIM_HOR);
		print_delim_ver(size);

		for(i = 0; i < size; i++){
				printf("%d%s", i, SHOW_GRAPH_DELIM_HOR);
				for(j = 0; j < size; j++){
						if(weighted) to_print = graph[i][j];
						else to_print = graph[i][j] != 0;
						printf("%d%s", to_print, SHOW_GRAPH_DELIM_HOR);
				}
				print_delim_ver(size);

		}	
}

int** generate_random_graph(int *size){
		srand(time(0));
		*size = (rand() % MAX_GRAPH_SIZE);
		if (*size < MIN_GRAPH_SIZE) *size = MIN_GRAPH_SIZE;

		/*could do malloc(*size * *size) instead of 'malloc'ing in a loop, 
		 * but sometimes the OS doesnt give us that much of continuous memory*/
		int **result = malloc(*size * sizeof(int*));

		for (int i = 0; i < *size; i++){ 
				result[i] = malloc(*size * sizeof(int));
		}

		for (int i = 0; i < *size; i++){ 
				for (int j = i; j < *size; j++){
						int rand_weight = (rand() % MAX_EDGE_WEIGHT);
						if (rand_weight % 2 == 0) rand_weight = 0;

						result[i][j] = rand_weight;
						result[j][i] = rand_weight;
				}
		}
		return result;
}

struct edge make_default_edge(){
		return (struct edge){
				.src = NODE_UNK,
				.dst = NODE_UNK,
				.weight = WEIGHT_UNK
		};
}

void set_bidirectional_edge(int ** graph, struct edge e){
#ifdef GR_OPS_DEBUG
		printf("%sconnecting %d to %d with weight %d\n", GR_OPS_DEBUG_PREFIX, e.src, e.dst, e.weight);
#endif

		graph[e.src][e.dst] = e.weight == WEIGHT_UNK ? 1 : e.weight;
		graph[e.dst][e.src] = e.weight == WEIGHT_UNK ? 1 : e.weight;	
}


void show_chain_weighted_nodes(int *chain, int size, int weighted){
		for (int i = 0 ; i < size ; i++)
				printf("%d%s", chain[i], SHOW_GRAPH_DELIM_HOR);
		printf("\n%s\n", SHOW_GRAPH_DELIM_VER);
}

int *generate_random_chain_weighted_nodes(int* size){
		srand(time(0));

		*size = rand() % MAX_CHAIN_SIZE;
		int *chain = malloc( *size * sizeof(int));
		for (int i = 0 ; i < *size ; i++)
				chain[i] = rand() % MAX_NODE_WEIGHT;
		return chain;
}
