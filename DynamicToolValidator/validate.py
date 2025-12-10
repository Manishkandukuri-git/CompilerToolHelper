import subprocess
import os
import argparse
import sys
import re

# We will use this list to store results for comparison
TEST_RUNS = []

def run_command(command, cwd=None, suppress_output=False):
    """Executes a shell command."""
    print(f"\n$ {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, cwd=cwd, text=True, capture_output=suppress_output)
        return result.stdout if suppress_output else ""
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error executing command: {e}")
        print("Check if dependencies (cmake, make/ninja) are installed and accessible.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\n❌ Error: Command not found. Is {command[0]} installed and in your PATH?")
        sys.exit(1)

def configure_and_build(generator, build_dir, optimization_flag):
    """Configures and builds the project."""
    
    # 1. Setup Build Directory
    if os.path.exists(build_dir):
        run_command(["rm", "-rf", build_dir])
    os.makedirs(build_dir)
    
    # 2. Configure with CMake
    print(f"--- Configuring {build_dir} with {optimization_flag} ---")
    
    cmake_command = ["cmake", 
                     f"-DCMAKE_CXX_FLAGS={optimization_flag}", 
                     ".."]
    
    if generator.lower() == "ninja":
        cmake_command.insert(1, "-G")
        cmake_command.insert(2, "Ninja")
    else:
        cmake_command.insert(1, "-G")
        cmake_command.insert(2, "Unix Makefiles")
        
    run_command(cmake_command, cwd=build_dir)

    # 3. Build the Project
    print(f"--- Building in {build_dir} ---")
    build_command = ["ninja"] if generator.lower() == "ninja" else ["make"]
    
    run_command(build_command, cwd=build_dir)
    
    return os.path.join(build_dir, "dynamic_checker")

def run_validation(generator, optimization_flag, input_string, baseline_crc=None):
    """Builds the project and runs the test against the input string."""
    
    build_dir = f"build_{generator}_{optimization_flag.replace('-', '')}"
    
    executable_path = configure_and_build(generator, build_dir, optimization_flag)

    # 4. Run the Test
    print(f"--- Running Test for {optimization_flag} ---")
    
    # Execute and capture output for parsing
    command = [executable_path, input_string]
    test_output = run_command(command, suppress_output=True)
    
    # 5. Parse Results
    # Uses regex to pull the result out of the C++ output
    crc_match = re.search(r'CRC_RESULT=([0-9a-f]+)', test_output)
    if not crc_match:
        print(f"❌ Could not parse CRC result from executable output.")
        sys.exit(1)
        
    crc_result = crc_match.group(1)
    
    # 6. Store and Report
    is_correct = "N/A"
    if baseline_crc:
        # Check if the current run matches the established baseline
        is_correct = "PASS" if crc_result.lower() == baseline_crc.lower() else "FAIL"

    TEST_RUNS.append({
        'opt_level': optimization_flag,
        'crc_result': crc_result,
        'correctness': is_correct
    })
    
    print(f"✅ Result ({optimization_flag}): {crc_result} | Correctness: {is_correct}")
    return crc_result

def finalize_validation():
    """Checks for consistency between multiple runs (e.g., O0 vs. O3)."""
    if len(TEST_RUNS) < 2:
        return True, "Single run completed."
        
    # Check consistency between runs
    first_crc = TEST_RUNS[0]['crc_result']
    for run in TEST_RUNS[1:]:
        if run['crc_result'] != first_crc:
            print("\n❌ CRITICAL FAILURE: Optimization caused a correctness regression!")
            print(f"   -> {TEST_RUNS[0]['opt_level']} produced {first_crc}")
            print(f"   -> {run['opt_level']} produced {run['crc_result']}")
            return False, "Optimization Regression Detected"
            
    return True, "Correctness maintained across optimization levels."

def main():
    parser = argparse.ArgumentParser(description="Dynamic Toolchain Validator (CRC-32 Check).")
    parser.add_argument("--generator", choices=['make', 'ninja'], default='ninja',
                        help="Specify the build system generator.")
    parser.add_argument("--clean", action='store_true', help="Remove all build directories.")
    
    # 🛑 FIX: Input is no longer required by default
    parser.add_argument("--input", type=str, required=False,
                        help="The input string data to use for the CRC calculation.")
    
    args = parser.parse_args()

    # --- Step 1: Handle Clean Command (Before requiring input) ---
    if args.clean:
        print("Cleaning up all build directories...")
        run_command(["rm", "-rf", "build_*"])
        print("Cleanup complete.")
        return

    # --- Step 2: Enforce Input Requirement for Validation ---
    if not args.input:
        print("\n❌ Error: The --input argument is required for validation runs.")
        print("Usage: python3 validate.py --input 'YourTestString'")
        sys.exit(1)
        
    # Validation logic starts here, as input is now guaranteed to be present
    input_data = args.input
    
    print(f"\n========================================================")
    print(f"| VALIDATING TOOLCHAIN FOR INPUT: '{input_data}'")
    print(f"========================================================\n")
    
    # --- Step 1: Establish the Correctness Baseline (-O0) ---
    # We use -O0 as the most conservative baseline.
    baseline_crc = run_validation(args.generator, "-O0", input_data)
    
    # --- Step 2: Validate against Optimized Build (-O3) ---
    # If O3 produces a different CRC, it's a compiler correctness bug.
    run_validation(args.generator, "-O3", input_data, baseline_crc=baseline_crc)
    
    # --- Step 3: Final Analysis ---
    success, message = finalize_validation()
    
    print("\n================== FINAL REPORT ==================")
    print(f"Input Data: '{input_data}' ({len(input_data)} bytes)")
    print(f"Consistency Check: {message}")
    print("==================================================")
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
