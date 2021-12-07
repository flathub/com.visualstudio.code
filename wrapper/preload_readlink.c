#define _GNU_SOURCE
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <dlfcn.h>
#include <limits.h>

typedef ssize_t (*ori_readlink) (const char * path, char * buf, size_t bufsiz);

ssize_t readlink(const char * path, char * buf, size_t bufsiz) {
	// fprintf(stderr, "readlink: %s\n", path);
	
	do {
		//if(bufsiz != 2*PATH_MAX-1) break;
		if(strcmp(path, "/proc/self/exe") != 0) break;

		const char* replace = "/app/extra/vscode/code_wrapper";
		size_t len = strlen(replace);
		if(len > bufsiz) break;

		memcpy(buf, replace, len);
		return len;
	} while(0);

	ori_readlink ori_readlink_op;
	ori_readlink_op = (ori_readlink) dlsym(RTLD_NEXT, "readlink");
	return ori_readlink_op(path, buf, bufsiz);
}
