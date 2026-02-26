from pathlib import Path
import shutil

def confirm_deletions(*paths: str | Path) -> dict[str | Path, bool]:
    """
    Prompt the user to confirm deletion for an arbitrary number of paths.
    Returns a dictionary mapping each path to a boolean (True for delete, False to keep).
    """
    results = {}
    
    for path in paths:
        # Convert string to Path object for easier handling
        p = Path(path)
        
        prompt = f"Do you want to delete '{p}'? [y/N]: "
        
        while True:
            response = input(prompt).strip().lower()
            
            if response in ['y', 'yes']:
                try:
                    # Check if the path actually exists first
                    if p.exists():
                        # Check if it's a directory or a file
                        if p.is_dir():
                            shutil.rmtree(p) # rmtree accepts Path objects directly
                        else:
                            p.unlink() # Delete a single file
                        print(f"Successfully deleted '{p}'")
                        results[path] = True
                    else:
                        print(f"Path '{p}' does not exist. Skipping.")
                        results[path] = False
                except Exception as e:
                    print(f"Error deleting '{p}': {e}")
                    results[path] = False
                break
                
            elif response in ['n', 'no', '']:
                results[path] = False
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
                
    return results
