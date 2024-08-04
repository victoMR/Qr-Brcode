# import numpy as np

import os
import platform
import subprocess
import tempfile
import time
from collections import deque
from multiprocessing.pool import ThreadPool

import customtkinter as ctk
import cv2 as cv
import pyperclip
import qrcode
from PIL import Image, ImageTk
# import dbr
from dbr import *

# Initialize the barcode reader
BarcodeReader.init_license(
    "DLS2eyJoYW5kc2hha2VDb2RlIjoiMjAwMDAxLTE2NDk4Mjk3OTI2MzUiLCJvcmdhbml6YXRpb25JRCI6IjIwMDAwMSIsInNlc3Npb25QYXNzd29yZCI6IndTcGR6Vm05WDJrcEQ5YUoifQ==")
reader = BarcodeReader()


# Process frame function
def process_frame(frame):
    results = None
    try:
        results = reader.decode_buffer(frame)
    except BarcodeReaderError as bre:
        print(bre)
    return results


# Function to update frame in the GUI
def update_frame():
    ret, frame = cap.read()
    if ret:
        if len(barcodeTasks) > 0 and barcodeTasks[0].ready():
            results = barcodeTasks.popleft().get()
            if results is not None:
                for result in results:
                    points = result.localization_result.localization_points
                    cv.line(frame, points[0], points[1], (0, 255, 0), 2)
                    cv.line(frame, points[1], points[2], (0, 255, 0), 2)
                    cv.line(frame, points[2], points[3], (0, 255, 0), 2)
                    cv.line(frame, points[3], points[0], (0, 255, 0), 2)
                    cv.putText(frame, result.barcode_text, tuple(points[0]), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
                    result_text.set(result.barcode_text)

        if len(barcodeTasks) < threadn:
            task = pool.apply_async(process_frame, (frame.copy(),))
            barcodeTasks.append(task)

        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_img.imgtk = imgtk
        lbl_img.configure(image=imgtk, text="")

    root.after(10, update_frame)


# Copy result to clipboard
def copy_result():
    result = result_text.get()
    pyperclip.copy(result)


# Take snapshot
def take_snapshot():
    ret, frame = cap.read()
    if ret:
        cv.imwrite(f'pictures/snapshot_{int(time.time())}.png', frame)


# Open QR Code generator window
def open_qr_generator():
    def generate_qr():
        qr_input = qr_input_text.get()
        if qr_input:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_input)
            qr.make(fit=True)
            qr_img = qr.make_image(fill='black', back_color='white')
            qr_img = qr_img.resize((200, 200), Image.LANCZOS)
            qr_imgtk = ImageTk.PhotoImage(qr_img)
            lbl_qr.imgtk = qr_imgtk
            lbl_qr.configure(image=qr_imgtk, text="")
            lbl_qr.qr_image = qr_img

    def copy_qr():
        qr_img = lbl_qr.qr_image
        if qr_img:
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            qr_img.save(temp_file.name)
            temp_file.close()

            if platform.system() == 'Darwin':  # macOS
                subprocess.run(
                    ["osascript", "-e", f'set the clipboard to (read (POSIX file "{temp_file.name}") as JPEG picture)'])
            elif platform.system() == 'Windows':
                from io import BytesIO
                import win32clipboard

                image = Image.open(temp_file.name)
                output = BytesIO()
                image.convert("RGB").save(output, "BMP")
                data = output.getvalue()[14:]
                output.close()

                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
            else:
                raise NotImplementedError("Clipboard copy not implemented for this OS")

            os.remove(temp_file.name)

    def save_qr():
        qr_img = lbl_qr.qr_image
        if qr_img:
            qr_img.save(f'qr_{int(time.time())}.png')

    qr_gen_window = ctk.CTkToplevel(root)
    qr_gen_window.title("QR Code Generator")
    qr_gen_window.geometry("400x400")

    ctk.CTkLabel(qr_gen_window, text="Enter text or URL for QR Code:").pack(pady=10)
    qr_input_text = ctk.CTkEntry(qr_gen_window, width=300)
    qr_input_text.pack(pady=10)

    ctk.CTkButton(qr_gen_window, text="Generate QR Code", command=generate_qr).pack(pady=10)
    lbl_qr = ctk.CTkLabel(qr_gen_window)
    lbl_qr.pack(pady=10)

    ctk.CTkButton(qr_gen_window, text="Copy QR Code", command=copy_qr).pack(pady=10)
    ctk.CTkButton(qr_gen_window, text="Save QR Code", command=save_qr).pack(pady=10)
    ctk.CTkButton(qr_gen_window, text="Exit", command=qr_gen_window.destroy).pack(pady=10)

    qr_gen_window.mainloop()


# GUI setup
root = ctk.CTk()
root.title("Barcode & QR Code Scanner")
root.geometry("350x700")

# Create widgets
lbl_img = ctk.CTkLabel(root)
lbl_img.pack(pady=10)

result_text = ctk.StringVar()
lbl_result = ctk.CTkLabel(root, textvariable=result_text, font=('Helvetica', 16))
lbl_result.pack(pady=10)

btn_copy = ctk.CTkButton(root, text="Copy Result", command=copy_result)
btn_copy.pack(pady=5)

btn_snapshot = ctk.CTkButton(root, text="Snapshot", command=take_snapshot)
btn_snapshot.pack(pady=5)

btn_generate_qr = ctk.CTkButton(root, text="Generate QR Code", command=open_qr_generator)
btn_generate_qr.pack(pady=5)

btn_exit = ctk.CTkButton(root, text="Exit", command=root.destroy)
btn_exit.pack(pady=5)

# Initialize camera and other variables
cap = cv.VideoCapture(0)
threadn = 1  # Number of threads
pool = ThreadPool(processes=threadn)
barcodeTasks = deque()

# Start updating the frames
update_frame()

# Start the main loop
root.mainloop()

cap.release()
cv.destroyAllWindows()