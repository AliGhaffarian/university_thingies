#ifndef TOKEN_T
#define TOKEN_T

enum token_type {
	INT,
	ID,
	OP,
	ERR
};

typedef struct _token_t {
	enum token_type type;
	int attribute_value;
}token_t ;

char *token_type2str(enum token_type);

extern token_t TOKEN_T_UNINIT;

#endif
