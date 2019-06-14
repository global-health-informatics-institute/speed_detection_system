import time


def main():
    print("Started speed detection application")
    initialize_variables()
    while True:
        detect_speed()
    print("Concluded speed detection application")


def initialize_variables():
    print("Initializing variables")


def detect_speed():
    print("Detecting speed")
    display_on_segment_display()


def display_on_segment_display():
    print("displaying values on seven segment display")
    time.sleep(2)


# This defines which function will be executed first
if __name__ == "__main__":
    main()
