#include "mysockets.h"

/* this is in netinet/in.h; included here for reference only.
struct sockaddr_in {
    short   sin_family;
    u_short sin_port;
    struct  in_addr sin_addr;
    char    sin_zero[8];
};
*/

void die(char *s) {
    perror(s);
    exit(2);
}

char *getTime(void) {
    struct timeval myTime;
    struct tm *myTimP;

    gettimeofday(&myTime,(struct timezone *)NULL);
    myTimP = localtime((time_t *)&myTime.tv_sec);
    return asctime(myTimP);
}

/*
 * translate strings in "dotted quad-port" notation ("W.X.Y.Z-P") to
 * struct sockaddr_in
 * NOTE: ranges not checked on integers.  Result is correct only
 * if the quad is actually valid, i.e. 0 <= W,X,Y,Z < 256
 */
int StringToSockaddr(char *name, struct sockaddr_in *address) {
    int a,b,c,d,p;
    char string[BUFSIZE];
    register char *cp;

    assert(name!=NULL);
    assert(address!=NULL);

/* Copy the name string into a private buffer so we don't crash trying
 * to write into a constant string.
 */
    if (strlen(name) > BUFSIZE-1)
        return -1;
    else
        strcpy(string,name);

    cp = string;

    address->sin_family = AF_INET;

    /* throw away leading blanks, since they make gethostbyname() choke.  */
    while (cp[0]==' ' || cp[0]=='\t') cp++;

    /* is the first character a digit?
     * If so, we assume "w.x.y.z-port"
     * If not, we assume "hostname-port" */
    if (isdigit(cp[0])) {
        if (sscanf(cp,"%d.%d.%d.%d-%d",&a,&b,&c,&d,&p) != 5)
            return -2;

        address->sin_addr.s_addr = htonl(a<<24 | b<<16 | c<<8 | d);
        address->sin_port = htons(p);
    } else {        /* we dont have a digit first */
        char *port;

        /* find the '-' in string: format must be hostname-port*/
        if ((port=strchr(cp,'-')) == NULL)
            return -3;

        /* split string in two... hostname\0port\0 and increment port past \0 */
        *port++ = '\0';

        /* look-up hostentry for the hostname */
        {
            struct hostent *destHostEntry;

            /* find the hostEntry for string */
            if ((destHostEntry=gethostbyname(cp))== NULL)
                return -4;

            /* copy the address from the hostEntry into our address */
            bcopy(destHostEntry->h_addr_list[0],
                &address->sin_addr.s_addr, destHostEntry->h_length);

        } /* look-up the hostentry for hostname */

        address->sin_port = htons(atoi(port));

    } /* else (we have hostname-port) */

    return 0;
}


/*
 * Convert a struct sockaddr_in into dotted.quad-port string notation.
 * String must point to a buffer of at least 22 characters.
 */
int SockaddrToString (char *string, struct sockaddr_in *ss) {
    int ip = ss->sin_addr.s_addr;
    ip = ntohl(ip);
    if (string==0x0)
        return -1;
    sprintf(string ,"%d.%d.%d.%d-%d", (int)(ip>>24)&0xff,
        (int)(ip>>16)&0xff,
        (int)(ip>>8)&0xff,
        (int)ip&0xff, ntohs(ss->sin_port));
    return 1;
}

static int mySocket, isVerbose;
static struct sockaddr_in destAddr, myAddr;
static int sizeofmyAddr, sizeofdestAddr;
static char inbuf[BUFSIZE], msgbuf[BUFSIZE], addrbuf[BUFSIZE], saddrbuf[BUFSIZE];

void end_connection(){
    close(mySocket);
}

int setup(int isB, int opponent, int verbose) {
    isVerbose = verbose;
    if ((mySocket = socket(AF_INET,SOCK_STREAM,0)) < 0)
        die("couldn't allocate socket");

    sprintf(addrbuf, "%s-%d", SVR_ADDR, SVR_PORT);
    StringToSockaddr (addrbuf, &destAddr);
    if (connect(mySocket,(struct sockaddr *) &destAddr,sizeof(destAddr)) < 0)
        die("failed to connect to server");

    printf("connected to server at %s\n",getTime());

    sizeofmyAddr = sizeof(myAddr);
    if (getsockname(mySocket, (struct sockaddr *) &myAddr,&sizeofmyAddr)<0) {
        printf("getsockname failed on mySocket!\n");
        addrbuf[0] = (char) 0;
    } else {
        /* set up addrbuf */
        SockaddrToString (addrbuf, &myAddr);
    }

    sizeofdestAddr = sizeof(destAddr);
    if (getpeername(mySocket,(struct sockaddr *) &destAddr,&sizeofdestAddr)<0) {
        printf("getpeername failed on mySocket!\n");
        saddrbuf[0] = (char) 0;
    } else {
        SockaddrToString (saddrbuf, &destAddr);
    }

    // Get the reply
    memset(inbuf, 0, BUFSIZE);
    recv(mySocket, inbuf, BUFSIZE, 0);
    if (isVerbose) printf("<< %s\n", inbuf);

    // Username prompt
    memset(inbuf, 0, BUFSIZE);
    recv(mySocket, inbuf, BUFSIZE, 0);
    if (isVerbose) printf("<< %s\n", inbuf);

    // Write the client username to the socket
    if (isB) sprintf(msgbuf,"%d\r\n", USERNUM_B);
    else sprintf(msgbuf,"%d\r\n", USERNUM_A);
    send(mySocket, msgbuf, strlen(msgbuf), 0);
    if (isVerbose) printf(">> %s\n", msgbuf);

    // Password prompt
    memset(inbuf, 0, BUFSIZE);
    recv(mySocket, inbuf, BUFSIZE, 0);
    if (isVerbose) printf("<< %s\n", inbuf);

    // Write the client password to the socket
    if (isB) sprintf(msgbuf,"%d\r\n", PASSWORD_B);
    else sprintf(msgbuf,"%d\r\n", PASSWORD_A);
    send(mySocket, msgbuf, strlen(msgbuf), 0);
    if (isVerbose) printf(">> %s\n", msgbuf);

    // Opponent prompt
    memset(inbuf, 0, BUFSIZE);
    recv(mySocket, inbuf, BUFSIZE, 0);
    if (isVerbose) printf("<< %s\n", inbuf);

    // Write the opponent to the socket
    sprintf(msgbuf,"%d\r\n", opponent);
    send(mySocket, msgbuf, strlen(msgbuf), 0);
    if (isVerbose) printf(">> %s\n", msgbuf);

    // Game number
    memset(inbuf, 0, BUFSIZE);
    recv(mySocket, inbuf, BUFSIZE, 0);
    if (isVerbose) printf("<< %s\n", inbuf);

    // Color prompt
    memset(inbuf, 0, BUFSIZE);
    recv(mySocket, inbuf, BUFSIZE, 0);
    if (isVerbose) printf("<< %s\n", inbuf);

    // Return 1 if we are white, else 0
    return inbuf[6]=='W';
}

char* send_move(char* move) {
    if(strlen(move)!=0) {
        // Don't send move until asked for move
        if (!strstr(inbuf, "?Move")) {
            // Move prompt
            memset(inbuf, 0, BUFSIZE);
            recv(mySocket, inbuf, BUFSIZE, 0);
            if (isVerbose) printf("<< %s\n", inbuf);
            if(strstr(inbuf, "Error:")) return (char*)0;
            if(strstr(inbuf, "Result:")) return (char*)0;
        }

        // Write the move to the socket
        sprintf(msgbuf,"%s\r\n", move);
        send(mySocket, msgbuf, strlen(msgbuf), 0);
        if (isVerbose) printf(">> %s\n", msgbuf);

        // Note: Sometimes server sends echo and response at same time?

        // Get move echo
        memset(inbuf, 0, BUFSIZE);
        recv(mySocket, inbuf, BUFSIZE, 0);
        if (isVerbose) printf("<< %s\n", inbuf);
        if(strstr(inbuf, "Error:")) return (char*)0;
        if(strstr(inbuf, "Result:")) return (char*)0;
        if (!strstr(inbuf+1, "Move:")) {
            // Get opponent move
            memset(inbuf, 0, BUFSIZE);
            recv(mySocket, inbuf, BUFSIZE, 0);
            if (isVerbose) printf("<< %s\n", inbuf);
            if(strstr(inbuf, "Error:")) return (char*)0;
            if(strstr(inbuf, "Result:")) return (char*)0;
        }
    } else {
        if (!strstr(inbuf, "Move:")) {
            // Move result
            memset(inbuf, 0, BUFSIZE);
            recv(mySocket, inbuf, BUFSIZE, 0);
            if (isVerbose) printf("<< %s\n", inbuf);
            if(strstr(inbuf, "Error:")) return (char*)0;
            if(strstr(inbuf, "Result:")) return (char*)0;
        }
    }

    char* instr_sub = strstr(inbuf, "(");
    char* substr = malloc(strlen(instr_sub) * sizeof(char) + 1);
    strncpy(substr, strstr(inbuf, "("), strlen(instr_sub) + 1);
    if(!substr) return (char*)0;
    int len = strstr(substr, "\n") - substr;
    substr[len] = (char)0;
    char* response = malloc((len+1)*sizeof(char));
    sprintf(response, "%s", substr);
    return response;
}
