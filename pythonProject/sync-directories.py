import os
import shutil


def sync_directories(source_dir, destination_dir):
    # Sync from source to destination
    sync_directory(source_dir, destination_dir)
    # Sync from destination to source
    sync_directory(destination_dir, source_dir)


def sync_directory(source_dir, destination_dir):
    for root, dirs, files in os.walk(source_dir):
        relative_path = os.path.relpath(root, source_dir)
        dest_path = os.path.join(destination_dir, relative_path)
        os.makedirs(dest_path, exist_ok=True)

        for file in files:
            source_file = os.path.join(root, file)
            dest_file = os.path.join(dest_path, file)
            if not os.path.exists(dest_file) or \
                    os.stat(source_file).st_mtime > os.stat(dest_file).st_mtime:
                shutil.copy2(source_file, dest_file)
            elif os.stat(source_file).st_mtime < os.stat(dest_file).st_mtime:
                shutil.copy2(dest_file, source_file)


if __name__ == "__main__":
    source_dir = r"\\pesto\cnsd\rsmith\-VAULT-\Notes"
    destination_dir = r"C:\Users\rsmith\Documents\Notes"
    sync_directories(source_dir, destination_dir)
    print("Sync completed.")
