import requests
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import threading
import datetime
import os
from tkinter import messagebox
from tkinter import *
from tkinter.ttk import Progressbar
import glob

myApp = Tk()

myApp.geometry("500x500")

myApp.resizable(0, 0)

myApp.configure(bg="orange")

myApp.title("Jupyter Downloader")

# event

def download_chunk(start, end, url, chunk_number):
    headers = {'Range': f'bytes={start}-{end}'}
    response = requests.get(url, headers=headers, stream=True)

    with open(f'chunk_{chunk_number}', 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)

# Step 2: Combine the Files
def combine_files(chunk_prefix, output_file):
    with open(output_file, 'wb') as output_f:
        chunk_number = 0
        while True:
            try:
                with open(f'{chunk_prefix}_{chunk_number}', 'rb') as chunk_f:
                    chunk = chunk_f.read(1024)  # Read in 1KB chunks
                    while chunk:
                        output_f.write(chunk)
                        chunk = chunk_f.read(1024)
                chunk_number += 1
            except FileNotFoundError:
                break

# Step 3: Clean Up Split Files
def clean_up_chunks(chunk_prefix):
    for file_name in glob.glob(f'{chunk_prefix}_*'):
        os.remove(file_name)


def download():
    url_input = url_input_var.get()
    url = url_input.split('?')[0] if url_input.count('?') > 1 else url_input
    num_threads = 15

    increase_count = 0

    response = requests.head(url)
    file_size = int(response.headers['content-length'])

    chunk_size = file_size // num_threads

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Create a list of futures for each thread and wait for them to finish before continuing.
        task = []
        for i in range(num_threads):
            start = i * chunk_size
            end = start + chunk_size
            task.append(executor.submit(download_chunk, start , end, url , i))
            progressBar['value'] += increase_count
            if (increase_count <= 7):
                increase_count += 0.5

        for future in as_completed(task):
            # Do something with the result of the
            progressBar['value'] += increase_count
            if increase_count <= 15:
                increase_count += 0.5

        messagebox.showinfo("Download Complete", "Download Complete ,Check your file in directory same as you downloaded it")

    increase_count = 0
    filename_ = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    chunk_prefix = 'chunk'  # Prefix used while splitting
    output_file = f'file_{filename_}_.zip'  # Specify the desired output file name

    combine_files(chunk_prefix, output_file)

    clean_up_chunks(chunk_prefix)  # Clean up files with prefix 'chunk'

    progressBar['value'] = 0

# widget

url_input_var = StringVar()

myLabel = Label(myApp, text="Jupyter Downloader", font=("Arial", 25), bg="orange" ,fg="white")

myLabel.pack(expand=True)

myEntry = Entry(myApp ,textvariable=url_input_var, font=("Arial", 20), bg="white")

myEntry.pack(expand=True ,padx=10 ,pady=10 ,fill=BOTH)

myButton = Button(myApp, text="Download", font=("Arial", 20), bg="white", command=threading.Thread(target=download).start)

myButton.pack(expand=True ,padx=10 ,pady=20 ,fill=BOTH)

progressBar = Progressbar(myApp, orient=HORIZONTAL, length=15, mode='determinate')

progressBar.pack(expand=True ,padx=10 ,pady=10 ,fill=BOTH)

myApp.mainloop()