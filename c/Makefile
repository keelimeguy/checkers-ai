all:
	gcc -c -fpic main_test.c main.c checkers32.c checkers32_calc.c
	ld -r checkers32.o checkers32_calc.o -o test.o
	gcc -shared test.o -o libtest.so
	gcc -ggdb3 main_test.c checkers32_calc.c -o test_checkers32.exe
	gcc -ggdb3 main.c checkers32_calc.c checkers32.c -o checkers32.exe

clean:
	rm test.o main.o main_test.o checkers32.o checkers32_calc.o libtest.so checkers32.exe test_checkers32.exe
