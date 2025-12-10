#include <iostream>
#include <vector>
#include <chrono>
#include <algorithm>
#include "CRC_Utils.h"

constexpr size_t BUFFER_SIZE = 4 * 1024 * 1024;

int main(int argc, char* argv[]) {
    std::vector<uint8_t> data(BUFFER_SIZE);
    std::generate(data.begin(), data.end(), []() {
        static uint8_t counter = 0;
        return counter++; 
    });

    auto start_time = std::chrono::high_resolution_clock::now();

    constexpr int RUNS = 10; 
    uint32_t final_crc = 0;
    for (int i = 0; i < RUNS; ++i) {
        final_crc = calculate_crc32(data);
    }

    auto end_time = std::chrono::high_resolution_clock::now();

    long long duration_ms = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count();

    // Output must be easily parsable by Python script
    std::cout << "RESULT_CRC=" << std::hex << final_crc << std::dec << std::endl;
    std::cout << "RESULT_TIME_MS=" << duration_ms << std::endl;

    return 0;
}
