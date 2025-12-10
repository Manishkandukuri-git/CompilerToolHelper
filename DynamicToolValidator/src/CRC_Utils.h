#ifndef CRC_UTILS_H
#define CRC_UTILS_H

#include <cstdint>
#include <vector>

// Function to calculate CRC32 of a data buffer
uint32_t calculate_crc32(const std::vector<uint8_t>& data);

#endif // CRC_UTILS_H
