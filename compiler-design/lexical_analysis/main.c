#include <stdio.h>
#include "lexical_analysis.h"
#include "token_t.h"


void exercise_output(token_t *token_list, int list_size){
	int ID_counter = 0;
	int INT_counter = 0;
	int OP_counter = 0;
	int ERR_counter = 0;

	int i = 0;

	if (token_list == (token_t *)0 && list_size == -1){
		printf("invalid test case near line %d char %d\n", stopped_line, stopped_char);
		return;
	}

	for (i; i < list_size; i++){
		int *counter_to_use;
		switch (token_list[i].type) {
			case ID:{
					counter_to_use = &ID_counter;
					break;
				}
			case INT:{
					 counter_to_use = &INT_counter;
					 break;
				 }
			case OP:{
					counter_to_use = &OP_counter;
					break;
				}
			case ERR:{
					 counter_to_use = &ERR_counter;
					 break;
				 }
		}
		printf("%s%d ", token_type2str(token_list[i].type), *counter_to_use);
		(*counter_to_use)++;
	}
	printf("\n");
}

int main(){
	char test_case[] = "x11+play-32++32;";
	int result_size = 0;
	token_t *result;
	result = lexical_analyzer(test_case, &result_size);

	printf("%s\n", test_case);
	exercise_output(result, result_size);

	char test_case2[] = "x32+32+1x+fioj++;";
	printf("%s\n", test_case2);
	result = lexical_analyzer(test_case2, &result_size);
	exercise_output(result, result_size);


	char test_case3[] = "x32+32+x+fioj++\nhaha++234--!;";
	printf("%s\n", test_case3);
	result = lexical_analyzer(test_case3, &result_size);
	exercise_output(result, result_size);


	char test_case4[] = "x32+3x2+1x+1fioj++;";
	printf("%s\n", test_case4);
	result = lexical_analyzer(test_case4, &result_size);
	exercise_output(result, result_size);

}
