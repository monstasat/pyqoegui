# standard constants
DVBT2 = 0
DVBT = 1
DVBC = 2

# bw constants
BW6 = 0
BW7 = 1
BW8 = 2

# indexes of settings list
DEVICE = 0
T2_FREQ = 1
T2_BW = 2
T2_PLP_ID = 3
T_FREQ = 4
T_BW = 5
C_FREQ = 6


DEFAULT_VALUES = [[DVBT2],          # device
                  [586000000],      # t2 frequency
                  [BW8],            # t2 bandwidth
                  [0],              # t2 plp id
                  [586000000],      # t frequency
                  [BW8],            # t bandwidth
                  [586000000]]      # c frequency

