import traceback
import tracemalloc


def except_hook(exc_type, exc_value, exc_tb):
    tracemalloc.stop()
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("[CRITICAL ERROR]:", tb)
