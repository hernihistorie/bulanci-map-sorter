import subprocess
import sys

def run_script(script_name):
    try:
        subprocess.run([sys.executable, script_name])
    except FileNotFoundError:
        print(f"Error: {script_name} not found.")

def main():
    while True:
        print("\n=== MAIN MENU ===")
        print("1. Run Hasher")
        print("2. Run Name Getter")
        print("3. Run Screenshoter")
        print("4. Make new HTML overview")
        print("5. Delete place")
        print("6. Run Places Visualization")
        print("7. Exit")

        choice = input("Select option (1-7): ")

        if choice == "1":
            run_script("hasher.py")
        elif choice == "2":
            run_script("name_getter.py")
        elif choice == "3":
            run_script("screenshoter.py")
        elif choice == "4":
            run_script("maps_overview.py")
        elif choice == "5":
            run_script("delete_place.py")
        elif choice == "6":
            run_script("places_visualization.py")    
        elif choice == "7":
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()