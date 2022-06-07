import os
from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilenames


def main():
    # folder_select()
    items = file_select()
    print(os.path.join("/".join(items[0])))
    # [print(item) for item in items]

def folder_select():
    path = askdirectory(title='Select Folder') # shows dialog box and return the path
    print(path) 


def file_select():
    root = Tk()
    myFiles = []
    startLoc = "D:\python\StandardDetails\Issued"
    filez = askopenfilenames(
        parent=root,
        title='Choose PDF Files',
        initialdir=startLoc,filetypes=[ 
            ("Video Files", "*.mp4")
            ])
    myList = root.tk.splitlist(filez)
    for item in myList:
        loc, item = os.path.split(item)
        baseloc, folder = os.path.split(loc)
        myFiles.append([baseloc, folder, item])
    return(myFiles)


if __name__ == "__main__":
    main()