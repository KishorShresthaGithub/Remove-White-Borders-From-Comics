import cv2
import numpy as np
import os
import shutil
from os import walk
import math
import zipfile
from shutil import make_archive


def crop(x, dirpath):
    if x.endswith(".png") or x.endswith(".jpg"):
        # shpfiles.append(os.path.join(dirpath, x))
        # #img = cv2.imread("test.png")

        img = cv2.imread(os.path.join(dirpath, x))
        blurred = cv2.blur(img, (3, 3))
        canny = cv2.Canny(blurred, 50, 200)

        # find the non-zero min-max coords of canny
        pts = np.argwhere(canny > 0)
        x1, y1, x2, y2 = [0, 0, 0, 0]
        try:
            y1, x1 = pts.min(axis=0)
            y2, x2 = pts.max(axis=0)
        except ValueError:
            pass

        # crop the region
        cropped = img[y1:y2, x1:x2]
        # adding small borders to end result
        cropped = cv2.copyMakeBorder(
            cropped, 5, 5, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        cv2.imwrite(os.path.join(dirpath, x), cropped)


def main():
    for dirpath, subdirs, files in os.walk("."):
        for file in files:
            if(file.endswith(".cbz")):
                # path of file
                file_path = os.path.abspath(os.path.join(dirpath, file))
                # extracting the zip file
                folder_path, file_name, file_extension = extract_zip(file_path)
                # process zip
                process_zip(folder_path)
                # wrap up zip
                wrap_zip(folder_path, file_name, file_extension)
                # finish
                print(file_name+" completed")


def extract_zip(zip):
    # gettin filename of zip and extension
    file_name, file_extension = os.path.splitext(zip)
    # temp folder name
    temp_folder_name = str(file_name).strip() + "_temp"
    # absolute temp folder path
    temp_folder_path = os.path.abspath(os.path.join(".", temp_folder_name))

    # extracting zip file to temp folder path
    with zipfile.ZipFile(zip, "r") as zip_ref:
        zip_ref.extractall(temp_folder_path)

    return temp_folder_path, file_name, file_extension


def process_zip(temp_folder):
    # get all files in folder
    for dirpath, subdirs, files in os.walk(temp_folder):
        for file in files:
            # move images to topmost folder
            if file.endswith(".jpg") or file.endswith(".png"):
                image_file = os.path.join(dirpath, file)
                # crop image
                crop(image_file, dirpath)
                # move to topmost folder
                if not os.path.exists(os.path.join(temp_folder, image_file)):
                    shutil.move(image_file, temp_folder)


def removeEmptyFolders(path, removeRoot=True):
    if not os.path.isdir(path):
        return

    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                removeEmptyFolders(fullpath)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0 and removeRoot:
        print("Removing empty folder:", path)
        os.rmdir(path)


def wrap_zip(folder, file, extension):
    if(os.path.exists(folder)):
        # removing empty folders
        removeEmptyFolders(folder)
        # creating archive
        shutil.make_archive(os.path.join(
            folder, file+"_cropped"), "zip", folder)
        # removing temp directory
        shutil.rmtree(folder)
        # rename archive
        os.rename(os.path.join(
            folder, file+"_cropped.zip"), os.path.join(
            folder, file+"_cropped.cbz"))


main()

print("Task Finished. Press any key to continue...")
quit()
