#include <stdlib.h>
#include "lexical_analysis.h"
#include "token_t.h"

#define SHARP ';'

#ifdef LEXICAL_ANALYSIS_DEBUG 
#include <stdio.h>
    #define debug_printf printf 
#else
    #define debug_printf(...)
#endif



short is_int(char ch){
	return ch >= '0' && ch <= '9';
}
short is_alpha(char ch){
	return ch >= 'a' && ch <= 'z' ||
		ch >= 'A' && ch <= 'Z';
}
short is_op(char ch){
	return ch == '+' || ch == '-' || ch == '*' || ch == '/';
}

int stopped_line = -1;
int stopped_char = -1;
short token_list_allocation_increase = 5;

int symbol_table_size = 0;
void make_new_token(enum token_type t, token_t *result){
	result->type = t;
	result->attribute_value = symbol_table_size++;
	debug_printf("[%s] made new token %s attribute_value:%d\n", 
			__func__, token_type2str(result->type), result->attribute_value);
}

token_t* append_token_to_list(token_t *list, token_t *token, int *size, int *real_size){
	if ((*size * sizeof(token_t)) == *real_size){
		debug_printf("reallocating token list with size %d and real_size %d\n", *size, *real_size);
		*real_size += token_list_allocation_increase * sizeof(token_t);
		list = realloc(list, *real_size);
		if (list == (token_t *)NULL)
			debug_printf("realloc failed\n");
	}
	list[(*size)++] = *token;
	debug_printf("[%s] append new token %s attribute_value: %d\n", 
			__func__, token_type2str(list[(*size)-1].type), list[(*size)-1].attribute_value);
	debug_printf("[%s] new result size is %d\n", __func__, *size);
	return list;
}

token_t* lexical_analyzer(char *str, int *result_size){
	enum lexical_analyzer_states current_state = START;

	int result_real_size = token_list_allocation_increase * sizeof(token_t);
	token_t *result = malloc(result_real_size);
	*result_size = 0;

	stopped_char = 0;
	stopped_line = 0;

	token_t discovered_token = TOKEN_T_UNINIT;

	int i = 0;
	while(1){
		switch (current_state) {
			case START: {
					    if (is_int(str[i]))
						    current_state = IS_INT;
					    else if (is_alpha(str[i]))
						    current_state = IS_ID;
					    else if (is_op(str[i])){
						    current_state = START;

						    make_new_token(OP, &discovered_token); 
						    result = append_token_to_list(result, &discovered_token, result_size, &result_real_size);
					    }
					    else {
						    current_state = IS_ERR;
					    }
					    break;
				    }
			case IS_INT: {
					     if (is_int(str[i]))
						     current_state = IS_INT;
					     else if (str[i] == SHARP){
						     make_new_token(INT, &discovered_token);
						     result = append_token_to_list(result, &discovered_token, result_size, &result_real_size);
						     return result;
					     }
					     else if (is_op(str[i])){
						     make_new_token(INT, &discovered_token);
						     result = append_token_to_list(result, &discovered_token, result_size, &result_real_size);

						     make_new_token(OP, &discovered_token);
						     result = append_token_to_list(result, &discovered_token, result_size, &result_real_size);
						     current_state = START;
					     }
					     else {
						     current_state = IS_ERR;
					     }
					     break;
				     }
			case IS_ID: {
					    if (is_int(str[i]) || is_alpha(str[i]))
						    current_state = IS_ID;
					    else if (str[i] == SHARP){
						    make_new_token(ID, &discovered_token);
						    result = append_token_to_list(result, &discovered_token, result_size, &result_real_size);
						    return result;
					    }
					    else if (is_op(str[i])){
						    make_new_token(ID, &discovered_token);
						    result = append_token_to_list(result, &discovered_token, result_size, &result_real_size);

						    make_new_token(OP, &discovered_token);
						    result = append_token_to_list(result, &discovered_token, result_size, &result_real_size);
						    current_state = START;
					    }
					    else{
						    current_state = IS_ERR;
					    }
					    break;
				    }
			case IS_ERR:{
					    if (str[i] == SHARP){
						    make_new_token(ERR, &discovered_token);
						    append_token_to_list(result, &discovered_token, result_size, &result_real_size);
						    return result;
					    }
					    else if (is_op(str[i])){
						    //if encountered an operator, append the err that was being processed, then append the discovered operator
						    make_new_token(ERR, &discovered_token);
						    append_token_to_list(result, &discovered_token, result_size, &result_real_size);

						    make_new_token(OP, &discovered_token);
						    append_token_to_list(result, &discovered_token, result_size, &result_real_size);

						    current_state = START;
					    }
					    else {
						    current_state = IS_ERR; 
					    }

				    }
		}

		i++;
		if (str[i] == '\n'){
			stopped_line++;
			stopped_char = 0;
			i++; // to exclude new line from processing
		}
		if (str[i] == SHARP){
			return result; // in case of SHARP immediately after an operator or newline
		}
		else stopped_char++;
	}
}
