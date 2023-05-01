import pycam2
import time
import threading
import datetime
import RPi.GPIO as GPIO
import os
import subprocess
import sys
import serbopig

settime = 1800      # 撮影間隔(秒) 1800
DIR = "/home/nishihara/Pictures/"   # 保存ディレクトリ
sendflag = True     # サーバに送信するか否か
IS_servo = False     # サーボを動かすか
take_num = 49 # 総撮影回数49

#logger = logging.getLogger('LoggingTest')
#logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')
# logging.disable(logging.CRITICAL)

# schedule関数に直接渡すとエラーを吐くので(理由はわからない)分割



def tp(manuflag=False):
    '''
    撮影処理呼び出し関数
    '''

    # 次回撮影時刻取得
    next_time = datetime.datetime.now() + datetime.timedelta(seconds=settime)
    dtime = datetime.datetime.today()

    # 複数回撮影
    for i in range(3):
        if (manuflag == True):
            fname = dtime.strftime("%Y-%m-%d_%H-%M-%S_m_" + str(i) + ".png")
        else:
            fname = dtime.strftime("%Y-%m-%d_%H-%M-%S_" + str(i) + ".png")

        pycam2.takepic(DIR, fname, sendflag, start_date)
        time.sleep(3)

    if (manuflag == False):
        print('次回撮影予定時刻' + str(next_time))
    print('waiting...')

def schedule(interval_sec):
    d2 = None
    '''
    撮影定期実行関数
    '''
    current_num = 0
    print('自動撮影実行スレッド is running')

    # 基準時刻を作る
    '''
    base_timing = datetime.datetime.now()
    while current_num < take_num:
        if (IS_servo == True):
            time.sleep(2)
            time.sleep(10)
            tp()
            time.sleep(2)
        elif (IS_servo == False):
            tp()
    '''
    base_timing = datetime.datetime.now()
    while current_num < take_num:
        if (IS_servo == True):
            if (current_num == 0):
                d1 = serbopig.sw_OFF()
            d1 = serbopig.sw_OFF(d2)
            time.sleep(10)	#10		#サーボ実行から撮影までの間隔
            tp()
            d2 = serbopig.sw_ON(d1)
        elif (IS_servo == False):
            tp()
        # 基準時刻と現在時刻の剰余を元に、次の実行までの時間を計算する
        current_timing = datetime.datetime.now()
        elapsed_sec = (current_timing - base_timing).total_seconds()
        sleep_sec = interval_sec - (elapsed_sec % interval_sec)
        current_num += 1

        time.sleep(max(sleep_sec, 0)) # 指定時間待機

def switch():
    '''
    マニュアル実行用関数
    '''
    print('マニュアル実行スレッド is runnning')
    GPIO_Nbr = 12
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_Nbr, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # GPIO設定 内部プルダウン抵抗ON

    while True:
        if GPIO.wait_for_edge(GPIO_Nbr, GPIO.RISING):
            print("Switch ON")
            tp(True)
    GPIO.cleanup()

if __name__ == "__main__":
    print("===定点撮影プログラム===")
    dt_now = datetime.datetime.now()
    date = (dt_now.strftime('%Y-%m-%d'))
    times = (dt_now.strftime('%H:%M'))
    start_date = date
    start_time = times
    IS_servo = True
    start_times = start_date + ' ' + start_time
    print("===設定===\n撮影間隔: %.2f 秒\n撮影回数: %d\n保存先: %s" %(settime, take_num, DIR))
    print("======================\n")

    # 自動撮影と手動撮影の待ちをマルチスレッドで走らせる
    thread_1 = threading.Thread(target=schedule, args=([settime]))
    #thread_2 = threading.Thread(target=switch) # SW入力待ちスレッド 現在未使用
    #thread_1.setDaemon(True)
    #thread_2.setDaemon(True)

    wait_time = (datetime.datetime.strptime(start_times, '%Y-%m-%d %H:%M') - datetime.datetime.now()).total_seconds() # 撮影開始予定時刻になるまで待機させる時間
    try:
        print("開始時刻: %s, 待機秒数: %lf" %(str(datetime.datetime.strptime(start_times, '%Y-%m-%d %H:%M')),wait_time))
        time.sleep(max(wait_time, 0))
        thread_1.start()
        thread_1.join()
        print("停止")
        #sys.exit(0)
    except KeyboardInterrupt:
        print("停止")
        sys.exit(0)
