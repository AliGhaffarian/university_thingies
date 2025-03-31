#ifndef LEXICAL_ANALYSIS
#define LEXICAL_ANALYSIS
#include "token_t.h"

enum lexical_analyzer_states{
	START,
	IS_INT,
	IS_ID,
	IS_ERR,
};
extern int stopped_line;
extern int stopped_char;


short is_int(char ch);
short is_alpha(char ch);
short is_op(char ch);


token_t *lexical_analyzer (char*, int*);
void make_new_token(enum token_type, token_t*);
token_t* append_token_to_list(token_t*, token_t*, int*, int*);

#endif
