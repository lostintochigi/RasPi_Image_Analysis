import sys
import cv2
import time
import datetime
import subprocess
import paramiko
import os

def send_server(DIR, fname):
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
            confdict = ssh_config.lookup('chinoumac') # 指定したHostNameの設定をdictに格納
            client.load_system_host_keys()
            client.connect(hostname=confdict['hostname'],username=confdict['user'], key_filename=confdict['identityfile'])
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            with client.open_sftp() as sftp:
                print('\r\033[92m' + '送信中...' + '\033[0m', end='')
                sftp.put(DIR+fname, os.path.join("RasPi/pic", fname))
                os.remove(DIR+fname)
                print('\r\033[92m' + '送信完了' + '\033[0m', end='\n')
    except Exception as e:
        print("ssh connection error:", e.args)
    return

def takepic(DIR, fname, sendflag):
    '''
    撮影用関数
    DIR: 保存したいディレクトリ
    fname: ファイル名
    sendflag: True=サーバに送信する False=サーバに送信しない
    '''

    MAX_RETRY = 3

    print("start photograping process...")
    cap = cv2.VideoCapture(0)

    # v4l2で設定を行う前にread()を1回実行しておく
    _, _ = cap.read() # 対策としてこの1行を追加

    '''
    # v4l2の設定をsubprocessを用いて実行
    cmd1 = "v4l2-ctl -d /dev/video0 -c white_balance_temperature_auto=0"    # WB設定 => Manual
    cmd2 = "v4l2-ctl -d /dev/video0 -c white_balance_temperature=4000"      # WB指定 => 4000
    cmd3 = "v4l2-ctl -d /dev/video0 -c exposure_auto=1"                     # 露出設定 => Manual
    cmd4 = "v4l2-ctl -d /dev/video0 -c exposure_absolute=8"               # 露出指定 => 8
    cmd5 = "v4l2-ctl -d /dev/video0 -c gain=25"                             # ゲイン指定(映像分野ではゲインは感度のこと??)
    '''

    # subprocess で実行するコマンドの辞書
    cmdict = dict(
    cmd1="v4l2-ctl -d /dev/video0 -c white_balance_temperature_auto=0",
    cmd2="v4l2-ctl -d /dev/video0 -c white_balance_temperature=4000",
    cmd3="v4l2-ctl -d /dev/video0 -c exposure_auto=1",
    cmd4="v4l2-ctl -d /dev/video0 -c exposure_absolute=1000",
    cmd5="v4l2-ctl -d /dev/video0 -c gain=30")

    # v4l2ctl設定関数
    def v4l2ctl():
        for i in range(1,6):
                s = 'cmd'+str(i)
                ret = subprocess.check_output(cmdict[s], shell=True)
                time.sleep(0.1)
        return subprocess.CalledProcessError

    # v4l2ctl エラー処理
    for i in range(MAX_RETRY + 1):
        try:
            res = v4l2ctl()
            break
        except subprocess.CalledProcessError as e:
            print(e)
            if (i == 3):
                print("再走失敗 設定終了...")
                break

    for i in range(10):
        result, frame = cap.read()
        time.sleep(0.01)

    cv2.imwrite(DIR+fname,frame)
    cap.release()
    print("success!\nfilename: %s" %fname)

    if (sendflag == True):
        send_server(DIR, fname) # サーバに送信

if __name__ == "__main__":
    try:
        print('webcam test mode')
        while True:
            takepic("Documents/","test.png", False)
            time.sleep(1)
    except KeyboardInterrupt:
        print("停止")
        sys.exit(0)