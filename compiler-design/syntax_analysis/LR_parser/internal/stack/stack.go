package stack

import "errors"

type Stack[T any] []T

func (s *Stack[T]) Pop() (top T, err error) {
	if s.Empty() {
		var def T
		return def, errors.New("tried to pop empty stack")
	}
	top, _ = s.Top()
	(*s) = (*s)[:len(*s) -1]
	return top, nil
}

func (s Stack[T]) Empty()bool {
	return len(s) == 0
}

func (s Stack[T]) Top() (top T, err error) {
	if s.Empty(){
		err = errors.New("tried to top empty stack")
		return
	}
	top = (s)[len(s)-1]
	return top, nil
}

func (s *Stack[T]) Push(val T) {
	(*s) = append(*s, val)
}
