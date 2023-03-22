#!/usr/bin/env python3
import sys
import os
import time
import shutil
import flask
from flask_apscheduler import APScheduler

app = flask.Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)

local_dir = sys.argv[1]
media_drive = sys.argv[2]

timeout = 10

global current_status
global prev_update_time
current_status = ""
prev_update_time = time.time()

@app.route("/check_status", methods=["GET"])
def check_status():
    global current_status
    resp = flask.Response(current_status)
    resp.headers["Access-Control-Allow-Origin"]= "*"
    resp.headers["Access-Control-Allow-Methods"]= "GET, POST, PUT, DELETE, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"]= '*'
    resp.headers["Status"]= "200 OK"
    resp.headers["Vary"]= "Accept"
    resp.headers['Content-Type']= 'application/string'    
    return resp

@scheduler.task('interval', [local_dir, media_drive], id='copy_files', seconds=1) # every second
def copy_files(local_dir, media_drive):
    global current_status
    global prev_update_time

    current_time = time.time()
    if current_time - prev_update_time > timeout:
        current_status = ""

        # check usb names in media drive
        l_drives = os.listdir(media_drive)  
        if len(l_drives) == 0:
             current_status = "No USB drivers found!"
        for _usb_dir in l_drives:
            try:
                usb_dir = os.path.join(media_drive,_usb_dir)
                if not os.path.exists(usb_dir):
                    break
                # get list of files
                l_files = os.listdir(local_dir)
                l_files = [fpath for fpath in l_files if fpath.split('.')[-1] == 'bag']
                if len(l_files) > 0:
                    for fpath in l_files: 
                        # copy bag files
                        if not os.path.exists(os.path.join(usb_dir, fpath)):
                            shutil.copy(os.path.join(local_dir, fpath), os.path.join(usb_dir, fpath))  
                            # check that file was copied correctly 
                            file_size = get_file_size(os.path.join(usb_dir, fpath))
                            if file_size == 0:
                                os.remove(os.path.join(usb_dir, fpath), ignore_errors=True)                         
                        # delete file from local system after it was copied
                        else:
                            os.remove(os.path.join(local_dir, fpath))   
                    current_status = f"Bag files copied to {os.path.join(usb_dir, fpath)}!"
                    prev_update_time = current_time

            except Exception as e:
                print(e)
                current_status = "ERROR: bag file was not copied to USB drive!"
 


def get_file_size(filepath):           
    # open the file in read only           
    with open(filepath, "r") as file:           
        # move pointer to the end of the file           
        file.seek(0, 2)           
        # retrieve the current position of the pointer           
        # this will be the file's size in bytes           
        size = file.tell()           
        return size           
    # if the function reaches this statement it means an error occurred within the above context handler           
    return 0

if __name__ == '__main__':    
    port = 5001  
    scheduler.start()
    app.run(host='0.0.0.0', port=port, debug=True)
    