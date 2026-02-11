"""Constants for HiDOM integration."""
DOMAIN = "hidom"

# Configuration
CONF_HOST = "host"

# Data indices in data[] array
DATA_ONOFF = 28
DATA_MODE = 29
DATA_FAN = 30
DATA_SET_TEMP = 31
DATA_ERROR_CODE = 35
DATA_PIPE_TEMP = 38
DATA_ROOM_TEMP = 39

# Operation mode codes
MODE_COOL = 2
MODE_DRY = 4
MODE_FAN_ONLY = 8
MODE_HEAT = 16
MODE_AUTO_DRY = 32
MODE_REFRESH = 256
MODE_SLEEP = 512
MODE_HEAT_SUP = 1024

# Fan speed codes
FAN_AUTO = 1
FAN_HIGH = 2
FAN_MID = 4
FAN_LOW = 8

# Mode mapping
MODE_MAP = {
    MODE_COOL: "cool",
    MODE_DRY: "dry",
    MODE_FAN_ONLY: "fan_only",
    MODE_HEAT: "heat",
    MODE_AUTO_DRY: "dry",
    MODE_REFRESH: "cool",
    MODE_SLEEP: "cool",
    MODE_HEAT_SUP: "heat"
}

MODE_REVERSE_MAP = {
    "cool": MODE_COOL,
    "dry": MODE_DRY,
    "fan_only": MODE_FAN_ONLY,
    "heat": MODE_HEAT
}

# Fan mapping
FAN_MAP = {
    FAN_AUTO: "auto",
    FAN_HIGH: "high",
    FAN_MID: "medium",
    FAN_LOW: "low"
}

FAN_REVERSE_MAP = {v: k for k, v in FAN_MAP.items()}