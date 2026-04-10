from machine import Pin, time_pulse_us
import time

# ---------------------------
# Hardware Pins
# ---------------------------
LED_PIN = 15
TRIG_PIN = 2
ECHO_PIN = 3

led = Pin(LED_PIN, Pin.OUT)
trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# ---------------------------
# Timing Parameter
# ---------------------------
BIT_DELAY = 0.01
CODE_BITS = 9
DIST_THRESHOLD = 200
SYNC_DELAY = 3  # cm

# ---------------------------
# Ultrasonic Distance
# ---------------------------
def get_distance():
    trig.value(0)
    time.sleep_us(5)

    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    duration = time_pulse_us(echo, 1, 30000)

    if duration <= 0:
        return None

    return (duration * 0.0343) / 2

# ---------------------------
# LZW Encoder
# ---------------------------
def lzw_encode(text):
    if not text:
        return []

    dictionary = {chr(i): i for i in range(256)}
    next_code = 256

    p = text[0]
    codes = []

    for c in text[1:]:
        if p + c in dictionary:
            p = p + c
        else:
            codes.append(dictionary[p])
            dictionary[p + c] = next_code
            next_code += 1
            p = c

    codes.append(dictionary[p])
    return codes

# ---------------------------
# Codes → Bitstream (FIXED)
# ---------------------------
def codes_to_bitstream(codes):
    bitstream = ""

    for code in codes:
        b = bin(code)[2:]              # binary without 0b
        padding = CODE_BITS - len(b)   # manual zero padding

        if padding > 0:
            b = ("0" * padding) + b

        bitstream += b

    return bitstream

# ---------------------------
# VLC Transmission (OOK)
# ---------------------------
def send_sync():
    print("[TX] SYNC")
    led.value(1)
    time.sleep(SYNC_DELAY)
    led.value(0)
    time.sleep(0.0001)
    
def transmit_bit(bit):
    print(bit, end="")
    led.value(1 if bit == "1" else 0)
    time.sleep(BIT_DELAY / 2)
    led.value(0)
    time.sleep(BIT_DELAY / 2)

def transmit(bitstream):
    send_sync()
    time.sleep(3)   # ← FIXED INDENTATION
    print("[TX] Sending bits...")
    for b in bitstream:
        transmit_bit(b)
    print("[TX] Done\n")

# ---------------------------
# Main
# ---------------------------
def main():
    original_text = "BACDABAABACDABBACD"
    print("Original Text:", original_text)

    codes = lzw_encode(original_text)
    bitstring = codes_to_bitstream(codes)

    print("LZW Codes:", codes)
    print("Bitstream:")
    print(bitstring)
    print("Total bits:", len(bitstring))
    print("\nWaiting for object...")

    while True:
        distance = get_distance()

        if distance is not None and distance < DIST_THRESHOLD:
            print("\nObject detected at {:.2f} cm".format(distance))
            transmit(bitstring)
            time.sleep(5)

        time.sleep(1)

# Run
main()
