"""
Slot control module for handling roller accept/reject mechanisms
"""


def handle_slot_control_bigface(roller_queue_bigface, shared_data, command_queue):
    """Control slot mechanism based on second proximity sensor."""

    a = False
    while True:
        if shared_data["bigface"] and not a:
            a = True
            if not roller_queue_bigface.empty():
                defect_detected = roller_queue_bigface.get()
                status = "Defective" if defect_detected else "Good"
                print(f"Slot control received roller status for Bigface: {status}")
                print("accept_bigface" if not defect_detected else "reject_bigface")
                command_queue.put(("accept_bigface" if not defect_detected else "reject_bigface", None))
        elif not shared_data["bigface"]:
            a = False


def handle_slot_control_od(roller_queue_od, shared_data, command_queue):
    """Control slot mechanism based on second proximity sensor."""
    processing = False
    while True:
        if shared_data["od"] and not processing and not roller_queue_od.empty():
            processing = True
            if not roller_queue_od.empty():
                defect_detected = roller_queue_od.get()
                status = "❌ Defective" if defect_detected else "✅ Good"
                print(f"Slot control received roller status for od: {status}")
                command_queue.put(("reject_od" if defect_detected else "accept_od" , None))

            queue_size = roller_queue_od.qsize()
            print(f"📌 Queue size: {queue_size}, Contents: {'Empty' if queue_size == 0 else 'Not Empty'}")

        elif not shared_data["od"]:
            processing = False
