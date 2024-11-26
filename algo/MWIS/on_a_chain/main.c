#include <stdio.h>

#include <stdlib.h>
#include "defined_options.h"
#include "mwis.h"
#include "graph_ops.h"
int main(){
		int chain_size;

		int* chain =generate_random_chain_weighted_nodes(&chain_size);	

		printf("random chain:\n");
		show_chain_weighted_nodes(chain, chain_size, 1);

		mwis_init();
		printf("result of recursive: %d\n", mwis_chain_recursive(chain, chain_size - 1));

		mwis_init();
		printf("result of iterative: %d\n", mwis_chain_iterative(chain, chain_size));

}
