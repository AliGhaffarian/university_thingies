#define SHARP '\0'
enum token_type {
	INT,
	ID,
	OP,
	ERR
};


enum is_lex_states{
	START,
	IS_INT,
	IS_ID,
	IS_OP
};

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
enum token_type is_lex(char* str){
	enum is_lex_states current_state = START;
	int i = 0;
	while(1){
		switch (current_state) {
			case START: {
					    if (is_int(str[i]))
						    current_state = IS_INT;
					    else if (is_alpha(str[i]))
						    current_state = IS_ID;
					    else if (is_op(str[i]))
						    current_state = IS_OP;
					    else
						    return ERR;
					    break;
				    }
			case IS_INT: {
					     if (is_int(str[i]))
						     current_state = IS_INT;
					     else if (str[i] == SHARP)
						     return INT;
					     else
						     return ERR;	
					     break;
				     }
			case IS_ID: {
					    if (is_int(str[i]) || is_alpha(str[i]))
						    current_state = IS_ID;
					    else if (str[i] == SHARP)
						    return ID;
					    else
						    return ERR;
					    break;
				    }
			case IS_OP: {
					    if (str[i] == SHARP)
						    return OP;
					    else
						    return ERR;
					    break;
				    }
		}
		i++;
	}
}
