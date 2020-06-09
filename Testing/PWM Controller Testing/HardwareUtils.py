simpleMode = False
try:
    # Import I2C Communication Libraries
    from board import SCL, SDA
    import busio
    from adafruit_motor import servo

    # Import the PCA9685 module (16 Motor 12 bit PWM Servo Driver)
    from adafruit_pca9685 import PCA9685

    # Import the BNO055 module (Absolute Orientation IMU Fusion Breakout)
    from adafruit_bno055 import BNO055
except:
    simpleMode = True
    from noise import pnoise1
    from random import randint
    import time

settings = {
    # We need to add 50 to all of the pulse lengths, because the PCA9685 is always about 50 to slow
    "servo_settings": {
        "T100": {
            "min_pulse": 1100 + 50,
            "max_pulse": 1900 + 50
        }
    }
}

if not simpleMode:
    i2c = busio.I2C(SCL, SDA)

class ServoDriver():
    def __init__(self, servo_locs, frequency=50):
        if not simpleMode:
            self.pca = PCA9685(i2c)
            self.pca.frequency = frequency
            self.servos = [None]*16
            for loc, s_type in servo_locs:
                self.servos[loc] = (servo.ContinuousServo(self.pca.channels[loc],
                                                          min_pulse=settings["servo_settings"][s_type]["min_pulse"],
                                                          max_pulse=settings["servo_settings"][s_type]["max_pulse"]),
                                    s_type)

    def set_servo(self, loc, speed):
        if not simpleMode:
            if self.servos[loc]:
                self.servos[loc][0].throttle = speed
            else:
                raise Exception("There is no servo at {}".format(loc))

    def set_all_servos(self, speed, only_type=False):
        if not simpleMode:
            for s in self.servos:
                if s:
                    servo, s_type = s
                    if servo and (only_type == False or s_type == only_type):
                        servo.throttle = speed
    
    def shutdown(self):
        if not simpleMode:
            self.set_all_servos(0)
            self.pca.deinit()

class IMUFusion():
    def __init__(self):
        if not simpleMode:
            self.imu = BNO055(i2c)
            self.calibration = {
                "gyro-offset": {
                    "x": 0,
                    "y": 0,
                    "z": 0
                },
                "last": {
                    "gyro": {
                        "x": 0,
                        "y": 0,
                        "z": 0
                    },
                    "vel": {
                        "x": 0,
                        "y": 0,
                        "z": 0
                    },
                    "temp": 0
                }
            }
        else:
            self.offsets = {
                "imu": {
                    "calibration": {
                        "sys": randint(0, 1000),
                        "gyro": randint(0, 1000),
                        "accel": randint(0, 1000),
                        "mag": randint(0, 1000)
                    },
                    "gyro": {
                        "x": randint(0, 1000),
                        "y": randint(0, 1000),
                        "z": randint(0, 1000),
                    },
                    "vel": {
                        "x": randint(0, 1000),
                        "y": randint(0, 1000),
                        "z": randint(0, 1000),
                    }
                },
                "temp": randint(0, 1000)
            }
            self.start = time.time()
            self.octaves = 2
    
    def set_offset(self, offset=False):
        if not simpleMode:
            if offset:
                self.calibration["gyro-offset"]["x"] += offset["x"]
                self.calibration["gyro-offset"]["y"] += offset["y"]
                self.calibration["gyro-offset"]["z"] += offset["z"]
            else:
                self.calibration["gyro-offset"]["x"] += self.calibration["last"]["gyro"]["x"]
                self.calibration["gyro-offset"]["y"] += self.calibration["last"]["gyro"]["y"]
                self.calibration["gyro-offset"]["z"] += self.calibration["last"]["gyro"]["z"]
    
    def get_full_state(self):
        state = {
            "imu": {
                "calibration": {
                    "sys": 0,
                    "gyro": 0,
                    "accel": 0,
                    "mag": 0
                },
                "gyro": {
                    "x": 0,
                    "y": 0,
                    "z": 0,
                },
                "vel": {
                    "x": 0,
                    "y": 0,
                    "z": 0,
                }
            },
            "temp": 0
        }

        if not simpleMode:
            gyro = self.imu.euler
            lin_accel = self.imu.linear_acceleration
            temp = self.imu.temperature
            calib = self.imu.calibration_status

            state["imu"]["calibration"]["sys"] = calib[0]
            state["imu"]["calibration"]["gyro"] = calib[1]
            state["imu"]["calibration"]["accel"] = calib[2]
            state["imu"]["calibration"]["mag"] = calib[3]

            if gyro[0] is not None:
                state["imu"]["gyro"]["x"] = gyro[2] - self.calibration["gyro-offset"]["x"]
                state["imu"]["gyro"]["y"] = gyro[1] - self.calibration["gyro-offset"]["y"]
                state["imu"]["gyro"]["z"] = gyro[0] - self.calibration["gyro-offset"]["z"]
                self.calibration["last"]["gyro"]["x"] = state["imu"]["gyro"]["x"]
                self.calibration["last"]["gyro"]["y"] = state["imu"]["gyro"]["y"]
                self.calibration["last"]["gyro"]["z"] = state["imu"]["gyro"]["z"]
            else:
                state["imu"]["gyro"]["x"] = self.calibration["last"]["gyro"]["x"]
                state["imu"]["gyro"]["y"] = self.calibration["last"]["gyro"]["y"]
                state["imu"]["gyro"]["z"] = self.calibration["last"]["gyro"]["z"]
            
            if lin_accel[0] is not None:
                state["imu"]["vel"]["x"] += lin_accel[0]
                state["imu"]["vel"]["y"] += lin_accel[1]
                state["imu"]["vel"]["z"] += lin_accel[2]
                self.calibration["last"]["vel"]["x"] = state["imu"]["vel"]["x"]
                self.calibration["last"]["vel"]["y"] = state["imu"]["vel"]["y"]
                self.calibration["last"]["vel"]["z"] = state["imu"]["vel"]["z"]
            else:
                state["imu"]["vel"]["x"] = self.calibration["last"]["vel"]["x"]
                state["imu"]["vel"]["y"] = self.calibration["last"]["vel"]["y"]
                state["imu"]["vel"]["z"] = self.calibration["last"]["vel"]["z"]
            
            if temp > 0:
                state["temp"] = temp
                self.calibration["last"]["temp"] = state["temp"]
            else:
                state["temp"] = self.calibration["last"]["temp"]

        else:
            x = float(-(time.time()-self.start))/150.0

            state["imu"]["calibration"]["sys"] = (pnoise1(x+self.offsets["imu"]["calibration"]["sys"], self.octaves))*2+2
            state["imu"]["calibration"]["gyro"] = (pnoise1(x+self.offsets["imu"]["calibration"]["gyro"], self.octaves))*2+2
            state["imu"]["calibration"]["accel"] = (pnoise1(x+self.offsets["imu"]["calibration"]["accel"], self.octaves))*2+2
            state["imu"]["calibration"]["mag"] = (pnoise1(x+self.offsets["imu"]["calibration"]["mag"], self.octaves))*2+2
            
            state["imu"]["gyro"]["x"] = pnoise1(x+self.offsets["imu"]["gyro"]["x"], self.octaves)*180
            state["imu"]["gyro"]["y"] = pnoise1(x+self.offsets["imu"]["gyro"]["y"], self.octaves)*180
            state["imu"]["gyro"]["z"] = pnoise1(x+self.offsets["imu"]["gyro"]["z"], self.octaves)*180

            state["imu"]["vel"]["x"] = pnoise1(x+self.offsets["imu"]["vel"]["x"], self.octaves)*60
            state["imu"]["vel"]["y"] = pnoise1(x+self.offsets["imu"]["vel"]["y"], self.octaves)*60
            state["imu"]["vel"]["z"] = pnoise1(x+self.offsets["imu"]["vel"]["z"], self.octaves)*60
            
            state["temp"] = pnoise1(x+self.offsets["temp"], self.octaves)*5+21
        
        return state
    
