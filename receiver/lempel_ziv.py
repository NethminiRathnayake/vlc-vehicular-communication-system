from machine import ADC, Pin, I2C, UART
from ssd1306 import SSD1306_I2C
import time

# ============ UART (Optional Debug) ============
uart = UART(0, baudrate=9600, tx=Pin(0))  # GP0 TX → ESP32 RX

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
adc = ADC(26)                 # GP26 (ADC0)
voltage_threshold = 0.5       # Light detection threshold (V)
bit_delay = 0.01 # MUST match transmitter bit_delay
SYNC_DELAY = 3               # MUST match transmitter SYNC_DELAY

# ============ LZW PARAMETERS ============
CODE_BITS = 9       
NUM_CODES = 12               #variyng according to text
message_bit_length = CODE_BITS * NUM_CODES
message_timeout = 15          # Max wait time for SYNC light (s)

# ============ VLC RECEIVE ============
def receive_message_adc():
    print("Waiting to detect Red light (SYNC)...")
    #oled_message(["Waiting for", "Red light"])

    start_time = time.time()

    # ---- SYNC DETECTION ----
    while time.time() - start_time < message_timeout:
        raw = adc.read_u16()
        voltage = (raw / 65535) * 3.3
        if voltage >= voltage_threshold:
            print("SYNC detected!")
            #oled_message(["SYNC", "detected"])
            break
        time.sleep(0.0001)
    else:
        return None

    # ---- IGNORE SYNC PERIOD ----
    #print("Waiting for SYNC period to finish...")
    time.sleep(SYNC_DELAY)

    # Small guard time
    time.sleep(3)

    print("Starting DATA reception...\n")
    #oled_message(["Receiving", "data..."])

    # ---- RECEIVE BITSTREAM ----
    received_bits = ""
    for _ in range(message_bit_length):
        raw = adc.read_u16()
        voltage = (raw / 65535) * 3.3
        bit = '1' if voltage >= voltage_threshold else '0'
        received_bits += bit
        print("Voltage:", round(voltage, 2), "Bit:", bit)
        time.sleep(bit_delay)

    return received_bits

# ============ BITSTREAM → LZW CODES ============
def bitstream_to_codes(bitstream):
    codes = []
    for i in range(0, len(bitstream), CODE_BITS):
        code = int(bitstream[i:i + CODE_BITS], 2)
        codes.append(code)
    return codes

# ============ SAFE LZW DECODER ============
def lzw_decode_safe(codes):
    dictionary = {i: chr(i) for i in range(256)}
    next_code = 256

    if codes[0] not in dictionary:
        return None

    p = dictionary[codes[0]]
    decoded_text = p

    for code in codes[1:]:
        if code in dictionary:
            entry = dictionary[code]
        elif code == next_code:
            entry = p + p[0]
        else:
            return None

        decoded_text += entry
        dictionary[next_code] = p + entry[0]
        next_code += 1
        p = entry

    return decoded_text

# ============ BITSTREAM VALIDATION ============
def is_bitstream_valid(bitstream):
    return len(bitstream) == message_bit_length

# ============ MAIN LOOP ============
def main():
    while True:
        bitstream = receive_message_adc()

        if bitstream is None:
            print("\nNo message received")
            #oled_message(["No message", "received"])
            time.sleep(2)
            continue

        print("\nReceived Bitstream:")
        print(bitstream)

        if not is_bitstream_valid(bitstream):
            print("ERROR: Bitstream length mismatch")
            #oled_message(["ERROR!", "Bit length", "mismatch"])
            time.sleep(2)
            continue

        codes = bitstream_to_codes(bitstream)
        print("Received LZW Codes:", codes)

        decoded = lzw_decode_safe(codes)

        if decoded is None:
            print("ERROR: Wrong bits received")
            #oled_message(["ERROR!", "Wrong bits"])
        else:
            print("Decoded Message:", decoded)
            #oled_message(["Message RX", decoded])

        time.sleep(5)

# ============ RUN ============
main()
