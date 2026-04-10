from machine import Pin, time_pulse_us
import time

# ---------------------------
# Hardware Setup
# ---------------------------

led = Pin(15, Pin.OUT)
trig = Pin(2, Pin.OUT)
echo = Pin(3, Pin.IN)

bit_delay = 0.01
SYNC_DELAY = 3# seconds per bit (kept same)

# ---------------------------
# Ultrasonic Distance Function
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

    distance_cm = (duration * 0.0343) / 2
    return distance_cm

# ---------------------------
# OOK Transmission Functions
# ---------------------------
def send_sync():
    print("[TX] SYNC")
    led.value(1)
    time.sleep(SYNC_DELAY)
    led.value(0)
    time.sleep(0.0001)
    
def transmit_bit(bit):
    # Only one delay per bit
    led.value(1 if bit == "1" else 0)
    time.sleep(bit_delay)
    led.value(0)  # Turn OFF for next bit immediately

def transmit_message(bitstring):
    send_sync()
    time.sleep(5) 
    print("Transmitting (OOK):", bitstring)
    for bit in bitstring:
        transmit_bit(bit)
    print("Transmission complete.\n")
    time.sleep(2)
    
    

# ---------------------------
# Main Program
# ---------------------------

def main():
    message = "10011011101000100110111010100110111"  # Example OOK message
    print("OOK Message:", message)

    threshold = 200  # cm
    print("\nSystem Ready! Waiting for object...\n")

    while True:
        distance = get_distance()

        if distance is not None:
            print("Distance:", round(distance, 2), "cm")

            if distance < threshold:
                print("Object detected! Sending message...\n")
                transmit_message(message)
                print("Waiting 5 seconds...\n")
                time.sleep(5)
            else:
                print("No object close enough.\n")
        else:
            print("Sensor Error\n")

        time.sleep(1)

if __name__ == "__main__":
    main()
