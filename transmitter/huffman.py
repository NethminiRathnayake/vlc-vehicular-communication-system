from machine import Pin, time_pulse_us
import time
import heapq


# Huffman Tree Classes

class Node:
    def __init__(self, char, prob):
        self.char = char
        self.prob = prob
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.prob < other.prob

def build_huffman_tree(frequencies):
    heap = [Node(char, freq) for char, freq in frequencies.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        merged = Node(None, node1.prob + node2.prob)
        merged.left = node1
        merged.right = node2
        heapq.heappush(heap, merged)

    return heap[0]

def generate_codes(node, current_code="", codes=None):
    if codes is None:
        codes = {}
    if node is None:
        return

    if node.char is not None:
        codes[node.char] = current_code
        return

    generate_codes(node.left, current_code + "0", codes)
    generate_codes(node.right, current_code + "1", codes)
    return codes

def huffman_encode(text, codes):
    encoded = ""
    for char in text:
        encoded += codes[char]
    return encoded

# ---------------------------
# Hardware Setup
# ---------------------------

# LED Pin
led = Pin(15, Pin.OUT)

# Ultrasonic Sensor Pins
trig = Pin(2, Pin.OUT)
echo = Pin(3, Pin.IN)

bit_delay = 0.1


SYNC_DELAY = 3  # Duration of each bit

# ---------------------------
# Ultrasonic Distance Function
# ---------------------------
def get_distance():
    trig.value(0)
    time.sleep_us(5)

    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    duration = time_pulse_us(echo, 1, 30000)  # timeout 30ms

    if duration <= 0:
        return None

    distance_cm = (duration * 0.0343) / 2
    return distance_cm

# ---------------------------
# LED Transmission
# ---------------------------
def send_sync():
    print("[TX] SYNC")
    led.value(1)
    time.sleep(SYNC_DELAY)
    led.value(0)
    time.sleep(0.0001)
    
def transmit_bit(bit):
    led.value(1 if bit == "1" else 0)
    time.sleep(bit_delay)
    led.value(0)

def transmit_message(bitstring):
    send_sync()
    time.sleep(5)
    print("Transmitting:", bitstring)
    for bit in bitstring:
        transmit_bit(bit)
    print("Transmission complete.\n")

# ---------------------------
# Main Program
# ---------------------------
def main():
    original_text = "BACDABAABACDABBACD"
    print("Original Text:", original_text)

    # Frequencies
    characters = {
        'A': 7,
        'B': 5,
        'C': 3,
        'D': 3
    }

    # Huffman Setup
    tree = build_huffman_tree(characters)
    codes = generate_codes(tree)
    encoded_bitstring = huffman_encode(original_text, codes)

    # Print codes
    print("\nCharacter : Codeword")
    for char, code in codes.items():
        print(f"'{char}' : {code}")

    print("\nEncoded Bitstring:", encoded_bitstring)
    print("\nSystem Ready! Waiting for object...\n")

    threshold = 200   # cm

    while True:
        distance = get_distance()
        if distance is not None:
            print("Distance:", round(distance, 2), "cm")

            if distance < threshold:
                print("Object detected! Starting communication...\n")
                transmit_message(encoded_bitstring)
                print("Waiting 5 seconds before next detection...\n")
                time.sleep(5)
            else:
                print("No object close enough.\n")
        else:
            print("Sensor Error\n")

        time.sleep(1)

if __name__ == "__main__":
    main()
