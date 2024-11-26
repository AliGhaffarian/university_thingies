#include <string.h>
#include <stdio.h>
#include "defined_options.h"
#include "mwis.h"
#include "graph_ops.h"
int mw[MAX_CHAIN_SIZE];

void mwis_init(){
		memset(mw, NODE_UNK, MAX_GRAPH_SIZE * sizeof(int)) ;
}
int mwis_chain(int* chain, int current_index){
		if(current_index == 0) {
				mw[0] = chain[0];
				return chain[0];
		}

		if(current_index <= -1)return 0;

		if(mw[current_index] != NODE_UNK) {
				return mw[current_index];
		}


		int m1 = mwis_chain(chain, current_index - 1);
		int m2 = mwis_chain(chain, current_index - 2) + chain[current_index];
		printf("m1: %d, m2: %d\n", m1, m2);

		mw[current_index] = m1 > m2 ? m1 : m2;

		return mw[current_index];
}
