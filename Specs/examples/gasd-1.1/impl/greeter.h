#ifndef GREETER_H
#define GREETER_H

/**
 * COMPONENT Greeter
 * TRACE: SRS-000 (Hello World)
 */
typedef struct {
    // Greeter component structure
} Greeter;

/**
 * FLOW say_hello():
 *     1. RETURN "Hello, World!"
 */
const char* greeter_say_hello(Greeter* self);

#endif // GREETER_H
