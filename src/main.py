import os
import shutil
import sys
from gen_content import generate_pages_recursive


def copy_files(source_dir, target_dir):
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    source_files = os.listdir(source_dir)
    for source_file in source_files:
        source_path = os.path.join(source_dir, source_file)
        target_path = os.path.join(target_dir, source_file)

        if os.path.isfile(source_path):
            print(f"Copying file {source_file} from {source_path} to {target_path}...")
            shutil.copy(source_path, target_path)
        else:
            copy_files(source_path, target_path)


def main():
    static_dir = "./static"
    public_dir = "./docs"
    content_dir = "./content"
    template = "./template.html"

    if sys.argv[1] == "":
        basepath = "/"
    else:
        basepath = sys.argv[1]

    if os.path.exists(public_dir):
        print("Deleting public directory...")
        shutil.rmtree(public_dir)

    print("Copying static files to public directory...")
    copy_files(static_dir, public_dir)

    print("Generating website...")
    generate_pages_recursive(content_dir, template, public_dir, basepath)


if __name__ == "__main__":
    main()
