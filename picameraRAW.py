import sys
import time
import datetime
import picamera
import numpy as np
import cv2
import paramiko
import os

def send_server(DIR, fname, start_date):
    '''
    sftpでファイル送信関数
    DIR: ラズパイの保存ディレクトリ
    fname: ファイル名
    '''
    try:
        with paramiko.SSHClient() as client:
            print('\r\033[92m' + 'サーバ接続中...' + '\033[0m', end='')
            config_file = ('/home/nishihara/.ssh/config') # sshのconfigfileを読む
            ssh_config = paramiko.SSHConfig()
            ssh_config.parse(open(config_file, 'r'))
            confdict = ssh_config.lookup('chinousaba') # 指定したHostNameの設定をdictに格納
            client.load_system_host_keys()
            client.connect(hostname=confdict['hostname'],username=confdict['user'], key_filename=confdict['identityfile'])
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            with client.open_sftp() as sftp:
                dirlist = sftp.listdir("RasPi/pic/r02d/")
                if not (start_date in dirlist):
                    sftp.mkdir("RasPi/pic/r02d/" + start_date)

                print('\r\033[92m' + '送信中...' + '\033[0m', end='')
                sftp.put(DIR+fname, os.path.join("RasPi/pic/r02d", start_date, fname))
                os.remove(DIR+fname)
                print('\r\033[92m' + '送信完了' + '\033[0m', end='\n')
    except Exception as e:
        print("ssh connection error:", e.args)
    return

def takeRawPic(DIR, fname, sendflag, start_date):
    '''
    撮影用関数
    DIR: 保存したいディレクトリ
    fname: ファイル名
    sendflag: True=サーバに送信する False=サーバに送信しない
    '''

    print("start photograping process...(RGB)")

    with picamera.PiCamera() as camera:
        camera.ISO = 50
        camera.exposure_mode = 'off'
        camera.awb_mode = 'fluorescent'
        camera.shutter_speed = 3500
        camera.resolution = (736, 480)

        print('ISO' + str(camera._get_ISO()))
        print('exposure_mode' + str(camera._get_exposure_mode()))
        print('exposure_compensation' + str(camera._get_exposure_compensation()))
        print('awb_mode' + str(camera._get_awb_mode()))
        print('exposure_speed' + str(camera._get_shutter_speed()))
        print('analoggain' + str(camera._get_analog_gain()))
        print('digitalgain' + str(camera._get_digital_gain()))
        print('reslution' + str(camera._get_resolution()))

        image = np.empty((480 * 736 * 3,), dtype=np.uint8)
        camera.capture(image, 'bgr')
        #camera.capture(DIR + fname + '.png')
        image = image.reshape((480, 736, 3))
        np.save(DIR + fname, image)

    print("success!\nfilename: %s" %fname)

    if (sendflag == True):
        send_server(DIR, fname + '.npy', start_date) # サーバに送信

def select_mode():
    s = input("choose testmode r:roopmode m:manualmode: ")
    if (s == "r" or s == "m"):
        return s
    elif(s == "exit"):
        return
    else:
        print("pless r or m")
        select_mode()

if __name__ == "__main__":
    # テスト用
    s = select_mode()
    try:
        if (s == "r"):
            print('webcam test roopmode')
            while True:
                takeRawPic("/home/nishihara/Documents/","test", False, "test")
                time.sleep(3)
        elif (s == "m"):
            print('webcam test manualmode')
            fs = input("file name?: ")
            fname = fs
            for i in range(1):
                takeRawPic("/home/nishihara/Documents/",fname, True, "test")
                time.sleep(3)
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("停止")
        sys.exit(0)