cmake_minimum_required(VERSION 3.10)
project(ToolchainTestHarness CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Apply common flags to all CXX files in the project
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")

option(ENABLE_CRC "Enable CRC-32 validation feature" ON)

# 1. Define the CRC Utility Library
if (ENABLE_CRC)
    add_library(CRC_Utils STATIC
        src/CRC_Utils.cpp
    )
    set(EXEC_SRCS src/main.cpp)
else()
    message(STATUS "CRC-32 feature is DISABLED.")
    set(EXEC_SRCS src/main.cpp)
endif()

# 2. Define the main executable
add_executable(integrity_checker
    ${EXEC_SRCS}
)

# 3. Link the executable to the static library
if (ENABLE_CRC)
    target_link_libraries(integrity_checker
        CRC_Utils
    )
endif()

# 4. Set the output directory for binaries (Crucial for QA script parsing)
if (CMAKE_GENERATOR MATCHES "Xcode")
    # Do not set for Xcode default
else()
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR})
endif()

# 5. Define an install target (CI/CD release simulation)
install(TARGETS integrity_checker CRC_Utils
    DESTINATION bin
)
