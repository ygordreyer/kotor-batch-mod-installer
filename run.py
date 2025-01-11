import argparse
import os
import subprocess
import sys

def run_installer():
    """Run the KOTOR Mod Installer"""
    print("Launching KOTOR Mod Installer...")
    subprocess.run([sys.executable, 'kotor_mod_installer.py'])

def run_tests():
    """Run all test scripts"""
    print("Running tests...\n")
    
    test_scripts = [
        ('Environment Test', 'test_environment.py'),
        ('File Structure Test', 'test_file_structure.py'),
        ('Combine Mods Test', 'test_combine_mods.py'),
        ('Full Installer Test', 'test_installer.py')
    ]
    
    all_passed = True
    for test_name, script in test_scripts:
        print(f"\nRunning {test_name}...")
        print("=" * 40)
        result = subprocess.run([sys.executable, script])
        if result.returncode != 0:
            print(f"❌ {test_name} failed!")
            all_passed = False
        else:
            print(f"✓ {test_name} passed!")
        print("=" * 40)
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

def cleanup():
    """Clean up temporary files"""
    print("\nCleaning up...")
    subprocess.run([sys.executable, 'cleanup.py'])

def main():
    parser = argparse.ArgumentParser(description='KOTOR Mod Installer Runner')
    parser.add_argument('--test', action='store_true', help='Run tests instead of the installer')
    parser.add_argument('--clean', action='store_true', help='Clean up temporary files after running')
    args = parser.parse_args()
    
    try:
        if args.test:
            result = run_tests()
        else:
            run_installer()
            result = 0
        
        if args.clean:
            cleanup()
        
        return result
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"\nError: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())