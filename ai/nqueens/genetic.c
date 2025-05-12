#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>
#define POP_SIZE 100
#define N 8
#define POP_MEM_SIZE (N * POP_SIZE * sizeof(int))
#define MAX_COST (((N - 1 + 1) / 2) * (N - 1))

#define debug_delim "--------------"
int cost(int *solution){
	int result = 0;
	for(int i = 0; i < N; i++)
		for(int j = i + 1; j < N; j++){
			if ( abs(i - j) == abs(solution[i] - solution[j]) ||
					solution[i] == solution[j]
					) result++;
		}
	return result;
}
int *solution_among_population(int *population){
	int *solution = 0;
	for(int i = 0; i < N; i++){
		if(cost(population + (i * N)) != 0) continue;
		solution = (int *)malloc(N * sizeof(int));
		memcpy(solution, population + (i * N), N * sizeof(int));
		break;
	}
	return solution;
}
int random_y(){
	return random() % N;
}
int *random_solution(){
	int *result = (int *)malloc(N * sizeof(int));
	for (int i = 0; i < N; i++)
		result[i] = random_y();
	return result;
}
int *init_ga(){
	int *initial_population = (int *)malloc(POP_MEM_SIZE);
	memset(initial_population, 0, POP_MEM_SIZE);
	for (int i = 0; i < POP_SIZE; i++){
		int *tmp_random_solution = random_solution();
		memcpy((initial_population + (i * N)), tmp_random_solution, N * sizeof(int));
		free(tmp_random_solution);
	}
	return initial_population;
}

int *make_parent_index_pool_based_on_fitness(int *population, int *size_of_pool){
	*size_of_pool = 0;
	// 				 			number of solutions 	* MAX_COST to make room for max fitnes
	int *parent_index_pool_based_on_fitness= (int *)malloc(POP_SIZE  		* MAX_COST * sizeof(int));
	int current_pool_index = 0;
	for (int i = 0; i < N; i++){
		int fitness_of_i = (MAX_COST) - cost(population + (i * N));
		for (int j = current_pool_index; j < current_pool_index + fitness_of_i; j++){
			parent_index_pool_based_on_fitness[j] = i;
		}
		current_pool_index += fitness_of_i;
	}
	(*size_of_pool) = current_pool_index;
	return parent_index_pool_based_on_fitness;
}
int *select_parents(int *population){
	//int parent_indexes[N][2]
	int *parent_indexes = (int *)malloc(2 * sizeof(int)); //two parent for each entry

	int size_of_parent_pool;
	int *parent_index_pool_based_on_fitness = make_parent_index_pool_based_on_fitness(population, &size_of_parent_pool);
	for (int i = 0; i < 2; i++){
		int random_index_for_map = random() % size_of_parent_pool;
		parent_indexes[i] = parent_index_pool_based_on_fitness[random_index_for_map];
	}
	free(parent_index_pool_based_on_fitness);
	return parent_indexes;
}
int *crossover_and_mutate(int *first_parent, int *second_parent){
	int crossover_line = (random() % (N - 2)) + 1;
	int *offsprings = malloc(N * 2 * sizeof(int));

	for (int i = 0; i < N; i++){
		offsprings[i] = ( i < crossover_line ) ? first_parent[i] : second_parent[i];
		offsprings[i + N] = ( i >= crossover_line ) ? first_parent[i] : second_parent[i];
	}

	bool do_mutate = random() % 2;
	if (do_mutate){
		offsprings[random_y()] = random_y();
	}

	do_mutate = random() % 2;
	if (do_mutate){
		offsprings[random_y() + N] = random_y();
	}
	return offsprings;
}
int *iter_ga(int *population){
	int *result_population = (int *)malloc(POP_MEM_SIZE);

	int size_of_parent_pool;
	for(int i = 0; i < POP_SIZE; i += 2){
		int *parent_indexes = select_parents(population);
		int *children = crossover_and_mutate(
				population + (parent_indexes[0] * N), 
				population + (parent_indexes[1] * N));

		memcpy(result_population + (i/2 * N), children, N * sizeof(int));
		memcpy(result_population + (((i/2) + 1) * N), children + N, N * sizeof(int));

		free(children);
		free(parent_indexes);
	}
	return result_population;
}
int *solve_ga(){
	int *population = init_ga();
	int *solution;
	int i = 0;
	while ((solution = solution_among_population(population)) == 0) {
		free(solution);
		int *next_gen = iter_ga(population);
		free(population);
		population = next_gen;
		i++;
	}
	printf("solved in %d gens\n", i);
	return solution;
}
int main(){
	srand(time(0));
	int *solution = solve_ga();
	for(int i = 0; i < N; i++){
		printf("%d, ", solution[i]);
	}
	puts("\n");
}
