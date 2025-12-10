#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include "CRC_Utils.h"

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Error: Input string argument required." << std::endl;
        std::cerr << "Usage: " << argv[0] << " <input_string>" << std::endl;
        return 1;
    }

    std::string input_string = argv[1];
    
    // Convert input string to a byte vector
    std::vector<uint8_t> data(input_string.begin(), input_string.end());

    // Calculate CRC (single run is sufficient for correctness check)
    uint32_t final_crc = calculate_crc32(data);
    
    // Output designed for Python parsing
    std::cout << "CRC_RESULT=" << std::hex << final_crc << std::dec << std::endl;
    std::cout << "INPUT_SIZE=" << data.size() << std::endl;

    return 0;
}
