import os

target_dir = '/Users/ashutoshyadav/Pep/campus-bites'

for root, dirs, files in os.walk(target_dir):
    if '.git' in root or '__pycache__' in root:
        continue
    for file in files:
        if not (file.endswith('.py') or file.endswith('.html') or file.endswith('.md') or file == 'Procfile' or file == 'manage.py'):
            continue
            
        filepath = os.path.join(root, file)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Skipping {filepath}: {e}")
            continue
            
        if file.endswith('.py') or file == 'Procfile' or file == 'manage.py':
            new_content = content.replace("campus_bites", "campus_bites").replace("Campus Bites", "Campus Bites")
        elif file.endswith('.html') or file.endswith('.md'):
            # Specific sequence to handle paths/python imports first
            new_content = content.replace("campus_bites/", "campus_bites/") \
                                 .replace("campus_bites.", "campus_bites.") \
                                 .replace("campus_bites", "campus-bites") \
                                 .replace("Campus Bites", "Campus Bites")
        else:
            new_content = content
                                 
        if new_content != content:
            print(f"Updating content in: {filepath}")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

# Rename the folder campus_bites to campus_bites
old_folder = os.path.join(target_dir, 'campus_bites')
new_folder = os.path.join(target_dir, 'campus_bites')
if os.path.exists(old_folder):
    print(f"Renaming directory {old_folder} to {new_folder}")
    os.rename(old_folder, new_folder)
