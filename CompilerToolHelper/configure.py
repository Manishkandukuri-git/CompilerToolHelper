import subprocess
import os
import argparse
import sys

def run_command(command, cwd=None):
    """Executes a shell command and prints the output."""
    print(f"\n$ {' '.join(command)}")
    try:
        # Use check=True to raise an error if the command fails
        subprocess.run(command, check=True, cwd=cwd, text=True, capture_output=False)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        sys.exit(1)

def configure_and_build(generator="make"):
    """Configures and builds the project using CMake and the specified generator."""
    build_dir = f"build_{generator.lower()}"

    # 1. Setup Build Directory
    if os.path.exists(build_dir):
        run_command(["rm", "-rf", build_dir])
    os.makedirs(build_dir)
    print(f"Created build directory: {build_dir}")

    # 2. Configure with CMake
    print(f"\n--- Configuring Project using CMake and {generator.upper()} ---")
    if generator.lower() == "ninja":
        cmake_command = ["cmake", "-G", "Ninja", ".."]
    else:
        # Explicitly use the Unix Makefiles generator for reliable output path on Mac/Linux
        cmake_command = ["cmake", "-G", "Unix Makefiles", ".."]

    run_command(cmake_command, cwd=build_dir)

    # 3. Build the Project
    print(f"\n--- Building Project using {generator.upper()} ---")
    if generator.lower() == "ninja":
        build_command = ["ninja"]
    else:
        build_command = ["make"]

    run_command(build_command, cwd=build_dir)

    return build_dir

def run_test(build_dir):
    """Runs the compiled executable."""
    # Corrected path: assuming the executable is placed directly in the build directory
    executable_path = os.path.join(build_dir, "tool_helper") 
    # ... rest of function
    print("\n--- Running Compiled Executable Test ---")
    if os.path.exists(executable_path):
        run_command([executable_path])
    else:
        print(f"Error: Executable not found at {executable_path}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Python automation script for CompilerToolHelper project.")
    parser.add_argument("--generator", choices=['make', 'ninja'], default='make',
                        help="Specify the build system generator (make or ninja).")
    parser.add_argument("--clean", action='store_true', help="Remove all build directories.")

    args = parser.parse_args()

    if args.clean:
        print("Cleaning up all build directories...")
        run_command(["rm", "-rf", "build_make", "build_ninja"])
        print("Cleanup complete.")
        return

    # Full end-to-end workflow
    build_directory = configure_and_build(args.generator)
    run_test(build_directory)
    print(f"\n✅ Build and test successful using {args.generator.upper()}.")

if __name__ == "__main__":
    main()
