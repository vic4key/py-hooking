#include <stdio.h>

#if defined(_MSC_VER)
#define EXPORT __declspec(dllexport)
#elif defined(__GNUC__)
#define EXPORT __attribute__((visibility("default")))
#endif

#pragma optimize("", off)

extern "C" EXPORT void change_ptr_var(int* pvar)
{
  if (pvar != nullptr)
  {
    *pvar = 123;
  }
}

extern "C" EXPORT void change_ref_var(int& var)
{
  var = 456;
}

extern "C" EXPORT void print_message(const char* message)
{
  printf("%s\n", message);
}

extern "C" EXPORT void c_invoke_print_message()
{
  print_message("This is a string from C code");
}

#pragma optimize("", on)