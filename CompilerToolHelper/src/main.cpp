#include <iostream>
#include "MathFunctions.h" // Includes the function we want to test

int main() {
    int x = 10;
    int y = 5;

    std::cout << "--- CompilerToolHelper Executable ---" << std::endl;

    // Use the function from the static library
    int result = add(x, y);

    std::cout << "Result of add(" << x << ", " << y << "): " << result << std::endl;
    std::cout << "-----------------------------------" << std::endl;

    return 0;
}
