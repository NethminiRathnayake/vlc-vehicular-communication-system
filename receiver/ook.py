from machine import ADC, Pin, I2C, UART
from ssd1306 import SSD1306_I2C
import time

# ============ UART (TO ESP32) ============
uart = UART(0, baudrate=9600, tx=Pin(0))

# ============ OLED SETUP ============
try:
    i2c = I2C(0, scl=Pin(17, Pin.PULL_UP), sda=Pin(16, Pin.PULL_UP), freq=400000)
    time.sleep(1)
    oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)
except Exception as e:
    print("I2C Initialization Error:", e)

def oled_message(lines):
    oled.fill(0)
    y = 0
    for line in lines:
        oled.text(line, 0, y)
        y += 10
    oled.show()

# ============ ADC CONFIG ============
adc = ADC(26)
voltage_threshold = 0.6
bit_delay = 0.01
message_bit_length = 35
message_timeout = 15
SYNC_DELAY = 3  # 3 seconds

# ============ VLC RECEIVE ============
def receive_message_adc():
    print("Waiting for Red light...")
    #oled_message([
                #"Waiting for",
                #"Red light!"
        #])
    start_time = time.time()

    # ---- Wait for Red light ----
    while time.time() - start_time < message_timeout:
        raw = adc.read_u16()
        voltage = (raw / 65535) * 3.3
        if voltage >= voltage_threshold:
            print("Red light detected!")
            break
        time.sleep(0.0001)
    else:
        print("No red light detected, timeout")
        return None

    # ===== SYNC = 3 seconds wait =====
    print("SYNC 3 seconds")
    time.sleep(SYNC_DELAY)

    # ===== Additional stabilization wait 5 seconds =====
    #print("Stabilization wait: 5 seconds...")
    time.sleep(5)

    # ===== RECEIVE BITS =====
    received_bits = ""
    for _ in range(message_bit_length):
        raw = adc.read_u16()
        voltage = (raw / 65535) * 3.3
        bit = '1' if voltage >= voltage_threshold else '0'
        received_bits += bit
        print("Voltage:", round(voltage, 2), "Bit:", bit)
        time.sleep(bit_delay)

    return received_bits

# ============ MAIN LOOP ============
def main():
    while True:
        bits = receive_message_adc()
        if bits:
            print("\nReceived bits:", bits)
            #uart.write("Received bits: " + bits + "\n")
            #oled_message([
                #"Message:",
                #"Bits:",
                #bits
            #])
        else:
            print("No message received")
           # oled_message([
                #"No message",
                #"received"
        #])

        time.sleep(2)

# ============ RUN ============
main()
