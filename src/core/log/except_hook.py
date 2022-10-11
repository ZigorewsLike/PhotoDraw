import traceback
import tracemalloc

from .print_lib import print_e


def except_hook(exc_type, exc_value, exc_tb):
    tracemalloc.stop()
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print_e(tb)
