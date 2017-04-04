# standard constants
DVBT2 = 0
DVBT = 1
DVBC = 2

# bw constants
BW6 = 0
BW7 = 1
BW8 = 2

# timeouts
TIME_RESPONSE_OK           = 1.5
TIME_RESPONSE_MSG          = 2
TIME_GET_DEVINFO           = 10
TIME_GET_MEAS              = 1
TIME_GET_PARAMS            = 10

# tags and commands
UART_TAG_START             = 0xAA
UART_TAG_START_INV         = 0x55
UART_TAG_STOP              = 0xFE

UART_CMD_LEN_DEVINFO       = 2
UART_RSP_LEN_DEVINFO       = 11
UART_TAG_DEVINFO           = 0x10

UART_CMD_LEN_TUNER_SET     = 11
UART_RSP_LEN_TUNER_SET     = 11
UART_TAG_TUNER_SET         = 0x20

UART_CMD_LEN_MEAS          = 2
UART_RSP_LEN_MEAS          = 18
UART_TAG_MEAS              = 0x30

UART_CMD_LEN_PARAMS        = 2
UART_RSP_LEN_PARAMS        = 41
UART_TAG_PARAMS            = 0x40

UART_CMD_LEN_PLP_LIST      = 2
# UART_RSP_LEN_PLP_LIST    var
UART_TAG_PLP_LIST          = 0x50

UART_CMD_LEN_PLP_SET       = 2
UART_RSP_LEN_PLP_SET       = 3
UART_TAG_PLP_SET           = 0x60

UART_RSP_LEN_OK            = 2
UART_TAG_OK                = 0xEE

