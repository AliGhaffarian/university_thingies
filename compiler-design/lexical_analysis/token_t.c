#include "token_t.h"
token_t TOKEN_T_UNINIT = {
	.type = ERR,
	.attribute_value = -1
};

#ifdef TOKEN_T_DEBUG 
#include <stdio.h>
    #define debug_printf printf 
#else
    #define debug_printf(...)
#endif


char *token_type2str(enum token_type t){
	switch (t) {
		case INT : return "INT";
		case ID : return "ID";
		case OP : return "OP";
		case ERR : return "ERR";
	}

	debug_printf("invalid token type %d\n", t);
	return (char *)0;
}
