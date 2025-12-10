import subprocess
import os
import argparse
import sys
import time
import json

# Baseline: CRC result for the given data buffer when compiled correctly
BASELINE_CRC = "c1d46223"
#"c08170c8" 
PERFORMANCE_THRESHOLD = 1.05 # Allowable performance degradation (5%)

def run_command(command, cwd=None, suppress_output=False):
    """Executes a shell command."""
    print(f"\n$ {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, cwd=cwd, text=True, capture_output=suppress_output)
        return result.stdout if suppress_output else ""
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Command not found. Is {command[0]} installed and in your PATH?")
        sys.exit(1)

def get_code_size(build_dir, target_name="integrity_checker"):
    """Runs 'size' utility to get code size metrics."""
    # Note: 'size' utility output varies significantly by OS (macOS vs. Linux)
    # This function aims for basic parsing of the 'text' section size.
    size_output = run_command(["size", target_name], cwd=build_dir, suppress_output=True)
    try:
        # Simple assumption: size output has a parsable line with code size
        # This is fragile but demonstrates the concept for a project.
        if size_output:
            metrics = size_output.split('\n')[1].split()
            return int(metrics[0]) # Return 'text' size (code size)
    except Exception:
        return 0
    return 0

def configure_and_build(generator, optimization_flag, feature_flag_value):
    """Configures, builds, and runs the test for a specific configuration."""
    config_name = f"{generator}_{optimization_flag}"
    build_dir = f"build_{config_name}"

    # 1. Setup Build Directory
    if os.path.exists(build_dir):
        run_command(["rm", "-rf", build_dir])
    os.makedirs(build_dir)

    # 2. Configure with CMake
    print(f"\n--- Configuring {config_name.upper()} ---")

    cmake_command = ["cmake", 
                     "-DENABLE_CRC=" + feature_flag_value,
                     "-DCMAKE_CXX_FLAGS=" + optimization_flag, 
                     ".."]

    if generator.lower() == "ninja":
        cmake_command.insert(1, "-G")
        cmake_command.insert(2, "Ninja")
    else: # Use Unix Makefiles for 'make'
        cmake_command.insert(1, "-G")
        cmake_command.insert(2, "Unix Makefiles")

    run_command(cmake_command, cwd=build_dir)

    # 3. Build the Project
    print(f"\n--- Building {config_name.upper()} ---")
    build_command = ["ninja"] if generator.lower() == "ninja" else ["make"]

    start_build_time = time.time()
    run_command(build_command, cwd=build_dir)
    build_time = time.time() - start_build_time

    # 4. Run the Test
    executable_path = os.path.join(build_dir, "integrity_checker")
    print(f"\n--- Running Test for {config_name.upper()} ---")

    # Execute and capture output for parsing
    test_output = run_command([executable_path], suppress_output=True)

    # 5. Parse Results
    results = {
        'build_time_s': round(build_time, 3),
        'code_size_b': get_code_size(build_dir),
        'crc_result': "N/A",
        'run_time_ms': 0
    }

    for line in test_output.split('\n'):
        if line.startswith("RESULT_CRC="):
            results['crc_result'] = line.split('=')[1].strip()
        elif line.startswith("RESULT_TIME_MS="):
            results['run_time_ms'] = int(line.split('=')[1].strip())

    return config_name, results

def generate_report(results_o0, results_o3):
    """Compares O0 and O3 results and checks for regressions."""
    report = {
        'Validation': {},
        'Regression_Check': {},
        'O0_Results': results_o0,
        'O3_Results': results_o3
    }

    # Correctness Check: CRC must be identical and match baseline
    crc_match = (results_o0['crc_result'] == results_o3['crc_result']) and (results_o0['crc_result'].lower() == BASELINE_CRC.lower())
    report['Validation']['CRC_Correctness'] = "PASS" if crc_match else "FAIL"

    # Performance Regression Check (O3 should be faster than O0)
    report['Regression_Check']['O3_Vs_O0_Time_Ratio'] = "N/A"
    if results_o3['run_time_ms'] > 0 and results_o0['run_time_ms'] > 0:
        perf_ratio = results_o0['run_time_ms'] / results_o3['run_time_ms']
        report['Regression_Check']['O3_Vs_O0_Time_Ratio'] = round(perf_ratio, 2)

        # Check for poor optimization (O3 should be significantly faster than O0)
        if perf_ratio < 1.05: # O3 is less than 5% faster than O0
            report['Regression_Check']['Optimization_Check'] = "FAIL (Poor Optimization Ratio)"
        else:
             report['Regression_Check']['Optimization_Check'] = "PASS"

    # Code Size Delta (O3 may be slightly larger due to unrolling, but we track change)
    report['Regression_Check']['Code_Size_O3_Bytes'] = results_o3['code_size_b']

    return report

def main():
    parser = argparse.ArgumentParser(description="Toolchain Validation Harness for Embedded Components.")
    parser.add_argument("--generator", choices=['make', 'ninja'], default='make',
                        help="Specify the build system generator (make or ninja).")
    parser.add_argument("--clean", action='store_true', help="Remove all build directories.")

    args = parser.parse_args()

    if args.clean:
        print("Cleaning up all build directories...")
        run_command(["rm", "-rf", "build_make_*", "build_ninja_*", "validation_report.json"])
        print("Cleanup complete.")
        return

    # --- Run Validation: O0 Build (Baseline) ---
    _, results_o0 = configure_and_build(args.generator, "-O0", "ON")

    # --- Run Validation: O3 Build (Optimized) ---
    _, results_o3 = configure_and_build(args.generator, "-O3", "ON")

    # --- Generate Report ---
    final_report = generate_report(results_o0, results_o3)

    # Save report for CI script to read
    with open("validation_report.json", 'w') as f:
        json.dump(final_report, f, indent=4)

    print("\n\n" + "="*50)
    print("           TOOLCHAIN VALIDATION REPORT")
    print("="*50)
    print(json.dumps(final_report, indent=4))

    # Check for overall success for CI pipeline
    if final_report['Validation']['CRC_Correctness'] == "FAIL" or        final_report['Regression_Check'].get('Optimization_Check') == "FAIL (Poor Optimization Ratio)":
        print("\n❌ VALIDATION FAILED: Correctness or Optimization Regression Detected.")
        sys.exit(1)
    else:
        print("\n✅ VALIDATION PASSED. Regression check clear.")
        sys.exit(0)

if __name__ == "__main__":
    main()
