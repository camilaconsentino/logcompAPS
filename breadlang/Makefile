CC=gcc
CFLAGS=-O2 -Wall -Wextra

all: bread

lexer.c: lexer.l parser.tab.h
	flex -o lexer.c lexer.l

parser.tab.c parser.tab.h: parser.y
	bison -d -v parser.y

bread: parser.tab.c lexer.c main.c
	$(CC) $(CFLAGS) -o bread parser.tab.c lexer.c main.c

clean:
	rm -f bread lexer.c parser.tab.c parser.tab.h parser.output
