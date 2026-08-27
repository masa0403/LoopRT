import serial
import time


def send_commands(port, commands, baudrate=115200):
    ser = serial.Serial(port, baudrate, timeout=1)

    try:

        # =====================================================
        # LoopRT Readyを待つ
        # =====================================================

        print("[INFO] Waiting for LoopRT Ready...")

        while True:
            line = ser.readline().decode(errors="replace").strip()

            if not line:
                continue

            print(f"[LOOPRT] {line}")

            if line == "LoopRT Ready":
                break

        # =====================================================
        # Command Sequence
        # =====================================================

        print("[INFO] Send Command Sequence")

        for command in commands:

            start_time = time.perf_counter()

            ser.write(command.encode())

            print(
                f"[INFO] Send Command: {repr(command)}"
            )

            # -------------------------------------------------
            # LoopRTからCommand完了通知を待つ
            # -------------------------------------------------

            while True:

                line = (
                    ser.readline()
                    .decode(errors="replace")
                    .strip()
                )

                if not line:
                    continue

                print(f"[LOOPRT] {line}")

                if line == "[DONE]":

                    elapsed_time = (
                        time.perf_counter()
                        - start_time
                    )

                    print(
                        f"[INFO] Command Duration: "
                        f"{elapsed_time:.3f} s"
                    )

                    break

        # =====================================================
        # Experiment End
        # =====================================================

        print("[INFO] Waiting for Experiment End...")

        while True:

            line = (
                ser.readline()
                .decode(errors="replace")
                .strip()
            )

            if not line:
                continue

            print(f"[LOOPRT] {line}")

            if line == "Experiment End":
                return line

    finally:
        ser.close()