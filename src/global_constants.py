import os
from enums.ConfigurationMode import ConfigurationMode

# region Auto detect configuration from env vars
_conf = os.environ.get("CONFIGURATION", None)
if _conf is not None:
    CONFIGURATION = ConfigurationMode.DEBUG
else:
    CONFIGURATION = ConfigurationMode.RELEASE
# endregion

DEBUG = CONFIGURATION is ConfigurationMode.DEBUG
LOG_SHOW_INSPECT = CONFIGURATION is ConfigurationMode.DEBUG

LOG_IN_FILE = False
LOG_IN_SIGNAL = False

USAGE_TIMER_TICK_INTERVAL = 500

APP_NAME = "PhotoDraw"

