cmake_minimum_required(VERSION 3.10)
project(CompilerToolHelper CXX)

# Set the C++ standard required
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# 1. Define the MathFunctions Static Library
add_library(MathFunctions STATIC
    src/MathFunctions.cpp
)

# 2. Define the main executable
add_executable(tool_helper
    src/main.cpp
)

# 3. Link the executable to the static library
target_link_libraries(tool_helper
    MathFunctions
)

# 4. Set the output directory for binaries and libraries
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib)

# 5. Define an install target
install(TARGETS tool_helper MathFunctions
    DESTINATION bin
)
