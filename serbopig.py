import pigpio
import time
import sys

class Servo:
    '''
    サーボモータ制御用クラス
    '''

    Hz = 50

    def __init__(self, N, d=0):
        self.IS_SETUP = True
        self.GPIO_No = N
        self.direction = d
        print('セットアップします')
        self.pi = pigpio.pi()    #pigpioライブラリにアクセスするためのインスタンスを作成
        self.pi.set_mode(self.GPIO_No, pigpio.OUTPUT)    #GPIO 12を出力用に設定
        print('セットアップしました!')

    def setDirection(self, deg, t=1):
        '''
        角度指定でサーボモータを駆動
        degは-90~90
        '''
        self.direction = deg
        dc = 25000 + (120000-25000)/180*(deg+90)
        self.pi.hardware_PWM(self.GPIO_No, Servo.Hz, int(dc))
        time.sleep(t)

    def slowSetDirection(self, s_deg, e_deg, t=0.01):
        '''
        サーボモータをゆっくり駆動
        '''
        if (s_deg < e_deg):
            step = 1
            ie_deg = e_deg+1
        else:
            step = -1
            ie_deg = e_deg-1
        print('回転中:' + str(s_deg) + '度 ~ ' + str(e_deg) + '度')
        for i in range(s_deg, ie_deg, step):
            self.setDirection(i, t)

    def getDirection(self):
        '''
        現在のサーボモータの角度を取得
        '''
        return self.direction

    def cleanup(self):
        '''
        PWM出力停止
        '''
        print('リセットします。')
        time.sleep(0.5)
        #self.pi.set_mode(self.GPIO_No, pigpio.INPUT)
        #print('set INPUT')
        time.sleep(0.5)
        print('stop')
        self.pi.stop()
        self.IS_SETUP = False
        print('リセットしました。')

    def getIsSetup(self):
        '''
        セットアップ状態判定
        '''
        return self.IS_SETUP

    def __del__(self):
        print('殺された!')
        self.cleanup()

ROTATE = 23	#回転する角度(22)
def sw_ON(d=None):
    if (d is None):
        s = Servo(12)
        s.slowSetDirection(s.getDirection(), ROTATE)
    else:
        s = Servo(12, d)
        s.slowSetDirection(d, ROTATE)
    return s.getDirection()

def sw_OFF(d=None):
    if (d is None):
        s = Servo(12)
        s.slowSetDirection(s.getDirection(), -ROTATE-5)	#-ROTATE-5
    else:
        s = Servo(12, d)
        s.slowSetDirection(d, -ROTATE-5)
    time.sleep(0.12)
    s.slowSetDirection(s.getDirection(), -ROTATE)
    return s.getDirection()

if __name__ == "__main__":
    try:
        cnt = 0
        d2 = None
        while True:
            if (cnt == 0):
                d1 = sw_ON()
            else:
                d1 = sw_ON(d2)
            time.sleep(5)		#10
            d2 = sw_OFF(d1)
            time.sleep(5)		#10
            cnt += 1

    except KeyboardInterrupt:
        pi = pigpio.pi()
        pi.set_mode(12, pigpio.INPUT)
        sys.exit(0)
