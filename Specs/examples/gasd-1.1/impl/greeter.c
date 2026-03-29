#include "greeter.h"
#include <stdio.h>

const char *greeter_say_hello(Greeter *self) { return "Hello, World!"; }

int main() {
  Greeter greeter;
  printf("%s\n", greeter_say_hello(&greeter));
  return 0;
}
