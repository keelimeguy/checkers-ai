all:
	# Compile C code:
	gcc -c -fpic checkers32.c checkers32_calc.c mysockets.c -std=c99
	#
	# Compile checkers32 shared library:
	ld -r checkers32.o checkers32_calc.o -o libcheckers32.o
	gcc -shared libcheckers32.o -o libcheckers32.so -std=c99
	#
	# Compile mysockets shared library:
	ld -r mysockets.o -o libmysockets.o
	gcc -shared libmysockets.o -o libmysockets.so -std=c99

clean:
	# Remove all files created during C code and library compiling:
	rm libmysockets.o libcheckers32.o mysockets.o checkers32.o checkers32_calc.o libmysockets.so libcheckers32.so
