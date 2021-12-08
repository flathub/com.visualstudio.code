#define _GNU_SOURCE
#include <stdlib.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <dlfcn.h>
#include <limits.h>

#define ORIGIN_EXE  "/app/extra/vscode/code"
#define REPLACE_EXE "/app/extra/vscode/code_wrapper"

static void die_with(char *fmt, ...) {
  va_list args;
  va_start(args, fmt);
  vfprintf(stderr, fmt, args);
  va_end(args);
  fprintf(stderr, "\n");
  fflush(stderr);
  exit(-1);
}

typedef ssize_t (*ori_readlink_t) (const char * path, char * buf, size_t bufsiz);
static ori_readlink_t ori_readlink;

ssize_t readlink(const char * path, char * buf, size_t bufsiz) {
	//fprintf(stderr ,"%s, %d\n", path, bufsiz);
	ssize_t result = ori_readlink(path, buf, bufsiz);
	
	do {
		//if(bufsiz != 2*PATH_MAX-1) break;
		if(strcmp(path, "/proc/self/exe") != 0) break;
		if(strncmp(buf, ORIGIN_EXE, strlen(ORIGIN_EXE)) != 0) break;

		size_t len = strlen(REPLACE_EXE);
		if(len > bufsiz) break;

		memcpy(buf, REPLACE_EXE, len);
		return len;
	} while(0);
	return result;
}

__attribute__((constructor)) void lib_init() {
	char *dlerr;
	char *env_ld_preload;

	ori_readlink = (ori_readlink_t) dlsym(RTLD_NEXT, "readlink");

	if ((dlerr=dlerror()) != NULL)
		die_with("Failed to patch readlink() library call: %s", dlerr);

	env_ld_preload = getenv("LD_PRELOAD");
	if (env_ld_preload != NULL) {
		char path[PATH_MAX];
		int len;

		memset(path, PATH_MAX, '\0');
		len = ori_readlink("/proc/self/exe", path, PATH_MAX);
		if(len > 0 && strcmp(path, ORIGIN_EXE) == 0) {
			//fprintf(stdout, "unset LD_PRELOAD=%s\n", env_ld_preload);
			unsetenv("LD_PRELOAD");
		}
	}
}
