cmake_minimum_required(VERSION 3.10)
project(DynamicToolValidator CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Apply common flags to all CXX files in the project
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")

# 1. Define the CRC Utility Library
add_library(CRC_Utils STATIC
    src/CRC_Utils.cpp
)

# 2. Define the main executable
add_executable(dynamic_checker
    src/main.cpp
)

# 3. Link the executable to the static library
target_link_libraries(dynamic_checker
    CRC_Utils
)

# 4. Set the output directory for binaries (Crucial for automation script parsing)
if (CMAKE_GENERATOR MATCHES "Xcode")
    # Do not set for Xcode default
else()
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR})
endif()
