#ifndef PRIM 
#define PRIM

#define PRIM_DEBUG_PREFIX "[PRIM_DEBUG]: "
#include "graph_ops.h"

int connects_selected_to_notselected(int*, int, int);
struct edge lightest_edge_from_selected_v_to_remaining_v(int *, int **, int);
int **prim_minimum_spanning_tree(int **, int);
struct edge lightest_edge_from_selected_v_to_remaining_v(int *, int **, int);

#endif
