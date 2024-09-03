CFLAGS = -ansi -Wall -pedantic -g -I$(LIBRE_INC) -Iinclude -std=gnu99
LDFLAGS = -lm

  
all:
		@echo "** Compiling code **"
		rm -f *.so
		gcc -c *.c -I/sw/include
		gcc *o -o run -L/sw/lib -lm 
		
		@echo "\n"
		@echo "** Running compiled code **"
		./run $(CFLAGS) $(LDFLAGS)
		@echo "\n"

leaks:
		@echo "** Checking code for data leaks **"
		gcc -c *.c -I/sw/include
		gcc *o -o run -L/sw/lib -lm 
		valgrind --leak-check=yes ./run $(CFLAGS) $(LDFLAGS)
		@echo "\n"

compile:
		@echo "** Compiling code **"
		gcc -c *.c -I/sw/include
		gcc *o -o run -L/sw/lib -lm 

run:
		@echo "** Running compiled code **"
		./run $(CFLAGS) $(LDFLAGS)

clean: 
		@echo "** Cleaning object files **"
		rm -f *.o
		rm -f *.so
		rm -f run

build: 
		@echo "** Building .so library **"
		rm -f *.o
		rm -f *.so
		rm -f run

		cc -fPIC -shared -o clib.so *.c
