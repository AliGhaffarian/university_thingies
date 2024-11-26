#ifndef GR_OPS 
#define GR_OPS

#define GR_OPS_DEBUG_PREFIX "[GR_OPS_DEBUG_PREFIX]: "

#define MAX_GRAPH_SIZE 10
#define MIN_GRAPH_SIZE 4
#define MAX_EDGE_WEIGHT 50
int **generate_random_graph(int *);

#define SHOW_GRAPH_DELIM_HOR "\t|\t"
#define SHOW_GRAPH_DELIM_VER "------------------"
void show_graph(int **, int, int);

#define NODE_UNK -1
#define WEIGHT_UNK -1
struct edge{
		int src;
		int dst;
		int weight;
};
struct edge make_default_edge();
void set_bidirectional_edge(int **, struct edge);

#define MAX_CHAIN_SIZE 10
#define MAX_NODE_WEIGHT MAX_EDGE_WEIGHT
int *generate_random_chain_weighted_nodes(int *);
void show_chain_weighted_nodes(int *, int, int);
#endif
