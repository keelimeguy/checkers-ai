#ifndef MYSOCKETS_H
#define MYSOCKETS_H

#include <stdio.h>   /* for NULL */
#include <string.h>  /* for strtok() */
#include <ctype.h>   /* for isdigit() */
#include <stdlib.h>  /* for atoi() */
#include <strings.h> /* for bcopy() */
#include <errno.h>   /* for perror() */
#include <assert.h>  /* for assert() */
#include <unistd.h>  /* for close() */

#include <netdb.h>  /* for gethostbyname() and struct hostent */
#include <sys/types.h>  /* for pid_t, socket.h */
#include <sys/param.h>  /* for MAXHOSTNAMELEN */
#include <sys/socket.h> /* for AF_INET, etc. */
#include <netinet/in.h> /* for struct sockaddr_in */

#include <time.h>
#include <sys/time.h>   /* for struct timeval */

#define NMSIZE      26
#define BUFSIZE     1024

#define USERNUM     5
#define PASSWORD    291701
// #define USERNUM     6
// #define PASSWORD    615566

#define SVR_ADDR    "icarus.engr.uconn.edu" /* server name */
#define SVR_PORT    3499 /* Port # of checkers server */

int SockaddrToString (char *string, struct sockaddr_in *ss);
int StringToSockaddr(char *name, struct sockaddr_in *address);
char *getTime(void);
void die(char *s);

int setup();
void end_connection();
char* send_move(char* move);

#endif
