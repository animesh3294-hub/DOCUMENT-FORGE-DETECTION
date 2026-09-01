import os
import zipfile

def create_project_zip(zip_name):
    # Folders to ignore so the zip file stays lightweight
    ignore_dirs = {'node_modules', '__pycache__', 'venv', 'env', '.git', 'dist'}
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if not file.endswith('.zip') and file != 'zip_project.py':
                    file_path = os.path.join(root, file)
                    archive_path = os.path.relpath(file_path, '.')
                    zipf.write(file_path, archive_path)
                    print(f"Added: {archive_path}")

if __name__ == "__main__":
    output_filename = "omni-guard-forensics.zip"
    create_project_zip(output_filename)
    print(f"\n✅ Successfully created {output_filename}!")