package parser

import (
	stack "LR_parser/internal/stack"
	"errors"
	"fmt"
	"strconv"
)
type TABLE_ENTRY int
const (
	N_STATES = 8
	N_RULES = 4
	ACCEPT = -1
)
var ALPHAS string = "ab$"
var VARIABLES string = "ABS"

type rule struct{
	variable byte
	result string 
}

var rules []rule
var alpha_or_var_to_index map[byte]int;
var parse_table []map[byte]int;
func init(){
	init_rules()
	init_parse_table()
}
func init_rules(){
	rules = append(rules, rule{variable: 'S', result: "aA"})
	rules = append(rules, rule{variable: 'A', result: "bB"})
	rules = append(rules, rule{variable: 'B', result: "aS"})
	rules = append(rules, rule{variable: 'B', result: "b"})
}
func init_parse_table(){
	//0
	parse_table = append(parse_table, map[byte]int{'a':  2 + 1})
	parse_table[0]['S'] = 1 + 1

	//1
	parse_table = append(parse_table, map[byte]int{'$': ACCEPT})

	//2
	parse_table = append(parse_table, map[byte]int{'b': 4 + 1})
	parse_table[2]['A'] = 3 + 1

	//3
	parse_table = append(parse_table, map[byte]int{'$': N_STATES + 1})

	//4
	parse_table = append(parse_table, map[byte]int{'a': 6 + 1})
	parse_table[4]['b'] = 7 + 1
	parse_table[4]['B'] = 5 + 1

	//5
	parse_table = append(parse_table, map[byte]int{'$': N_STATES + 2})

	//6
	parse_table = append(parse_table, map[byte]int{'a': 2 + 1})
	parse_table[6]['S'] = 8+1

	//7
	parse_table = append(parse_table, map[byte]int{'$': N_STATES + 4})

	//8
	parse_table = append(parse_table, map[byte]int{'$': N_STATES + 3})
}
func Parse(input string)bool {
	current_state := 0
	s := stack.Stack[string] {"0"}
	i := 0
	for i < len(input) {
		fmt.Println(s)
		
		current_state_str, err := s.Top()

		//stack is empty
		if(err != nil){
			
			return false
		}

		current_state, err = strconv.Atoi(current_state_str)	
		//expected state, no integer found
		if(err != nil){
			
			return false
		}
		

		todo := parse_table[current_state][byte(input[i])]
		
		if todo == 0 {
			//empty entry
			return false
		} else if todo == ACCEPT {
			//ACCEPT
			return true
		} else if todo > N_STATES {
			//reduce
			reduce := (todo - 1) - N_STATES
			
			err := pop_slice(&s, rules[reduce].result)
			if err != nil {
				//expected slice wan't present in stack
				return false
			}


			//parsed variable
			push_variable := rules[reduce].variable

			stack_top, err:= s.Top()
			//empty stack
			if err != nil{
				return false
			}
			stack_top_int, err := strconv.Atoi(stack_top)
			//top of stack is not an state
			if err != nil {
				return false
			}

			next_state := parse_table[stack_top_int][push_variable] - 1
			current_state = next_state
			if (next_state == -1){
				return false //empty entry for pushed variable
			}

			s.Push(string(push_variable))
			//goto state
			s.Push(strconv.Itoa(next_state))
			
			
		} else {
			//shift

			s.Push(string(input[i]))
			s.Push(strconv.Itoa(todo - 1))
			
			i++
		}

	}
	return false
}

func pop_slice(s *stack.Stack[string], str string)error {
	i := len(str) - 1

	for i >= 0{
		stack_top, err := s.Pop()
		if err != nil {
			return errors.New("tried to pop empty stack")
		}
		_, err = strconv.Atoi(stack_top)

		//is state, not alpha
		if err == nil {
			continue
		} 

		if stack_top != string(str[i]){
			
			return errors.New(fmt.Sprintf("%s != %s at i=%d", stack_top, string(str[i]), i))
		}
		i--
	}
	return nil 
}
