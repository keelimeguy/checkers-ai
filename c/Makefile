all:
	gcc -c -fpic main.c test_keelin.c
	ld -r main.o test_keelin.o -o test.o
	gcc -shared test.o -o libtest.so
	gcc -ggdb3 main.c test_keelin.c -o main.o

clean:
	rm test.o main.o test_keelin.o libtest.so

# all: main.o test_keelin.o
# 	gcc -shared test_keelin.o -o libtest.dll -Wl,--out-implib,libtest.a
# 	gcc main.o -Wl,-rpath=. -L. -ltest -o main

# clean:
# 	rm main.o test_keelin.o libtest.dll libtest.a
