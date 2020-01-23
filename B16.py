#CPU module
import time

def arrSet(len):
    arr = []
    i = 0
    while i < len:
        arr.append(0)
        i += 1
    return arr

rom  = arrSet(512)
regs = arrSet(16)

execute = 1
jumped = 0

milli, lmilli = 0, 0

raw = open("rom.bin", "rb")
i, byte = 0, raw.read(1)
while byte:
    rom[i] = int.from_bytes(byte, "little")
    i += 1
    byte = raw.read(1)

while execute:
    lmilli = milli
    milli = int(round(time.time() * 1000))
    if milli - lmilli > 0: regs[6] += milli - lmilli
    
    regs[5] = 1
    
    if(regs[0] + 1 < len(rom)):
        lByte = rom[regs[0]]
        rByte = rom[regs[0] + 1]
    
    mode = lByte >> 6
    opcode = (lByte >> 1) & 0b11111
    arg1 = rByte >> 4
    arg2 = rByte & 0b00001111
    imm = ((lByte & 1) << 8) | rByte
    
    if opcode == 0x01:   #clr
        regs[arg1] = 0
    elif opcode == 0x02: #rst
        regs[0] = 0
    elif opcode == 0x03: #hlt
        execute = 0
    #0x04: mem not implemented
    elif opcode == 0x05: #mov - movm not implemented
        regs[arg2] = regs[arg1]
    elif opcode == 0x06: #ldm
        regs[arg2] = rom[regs[arg1]]
    #0x04: stm not implemented
    elif opcode == 0x08: #dat
        regs[0] += 2
        regs[arg1] = (rom[regs[0]] << 8) | rom[regs[0] + 1]
        jumped = 1
    elif opcode == 0x09: #add/i
        if mode & 1:
            regs[arg1] += regs[arg2]
        else:
            regs[1] = (regs[arg1] + regs[arg2]) if not mode >> 1 else (regs[2] + imm)
    elif opcode == 0x0A: #sub/d
        if mode & 1:
            regs[arg1] -= regs[arg2]
        else:
            regs[1] = (regs[arg1] - regs[arg2]) if not mode >> 1 else (regs[2] - imm)
        if regs[arg2] > regs[arg1]: regs[3] |= 6
    elif opcode == 0x0B: #mul/i
        if mode & 1:
            regs[arg1] *= regs[arg2]
        else:
            regs[1] = (regs[arg1] * regs[arg2]) if not mode >> 1 else (regs[2] * imm)
    elif opcode == 0x0C: #div/d
        if mode & 1:
            regs[arg1] = int(regs[arg1] / regs[arg2])
        else:
            regs[1] = int((regs[arg1] / regs[arg2]) if not mode >> 1 else (regs[2] / imm))
    elif opcode == 0x0D: #shl
        regs[1] = (regs[arg1] << regs[arg2]) if not mode >> 1 else (regs[2] << imm)
        regs[3] |= 4
    elif opcode == 0x0E: #shr
        regs[1] = (regs[arg1] >> regs[arg2]) if not mode >> 1 else (regs[2] >> imm)
        regs[3] |= 5
    elif opcode == 0x0F: #and
        regs[1] = (regs[arg1] & regs[arg2]) if not mode >> 1 else (regs[2] & imm)
    elif opcode == 0x10: #or
        regs[1] = (regs[arg1] | regs[arg2]) if not mode >> 1 else (regs[2] | imm)
    elif opcode == 0x11: #not
        regs[1] = ~regs[arg1]
    elif opcode == 0x12: #xor
        regs[1] = (regs[arg1] ^ regs[arg2]) if not mode >> 1 else (regs[2] ^ imm)
    elif opcode == 0x13: #cmp
        if (regs[arg1] >  regs[arg2]) if not mode >> 1 else (regs[2] >  imm): regs[3] |= 1
        if (regs[arg1] == regs[arg2]) if not mode >> 1 else (regs[2] == imm): regs[3] |= 2
        if (regs[arg1] == 0)          if not mode >> 1 else (regs[2] == 0):   regs[3] |= 4
    elif opcode == 0x14: #jmp
        regs[0] = (regs[arg1]) if not mode >> 1 else imm
        jumped = 1
    elif opcode == 0x15: #jal/nal
        if (regs[3] & 1) if not mode & 1 else (not regs[3] & 1):
            regs[0] = (regs[arg1]) if not mode >> 1 else imm
            jumped = 1
    elif opcode == 0x16: #jeq/neq
        if (regs[3] & 1) if not mode & 2 else (not regs[3] & 2):
            regs[0] = (regs[arg1]) if not mode >> 1 else imm
            jumped = 1
    elif opcode == 0x17: #jze/nze
        if (regs[3] & 4) if not mode & 1 else (not regs[3] & 4):
            regs[0] = (regs[arg1]) if not mode >> 1 else imm
            jumped = 1
    elif opcode == 0x18: #jof/nof
        if (regs[3] & 8) if not mode & 1 else (not regs[3] & 8):
            regs[0] = (regs[arg1]) if not mode >> 1 else imm
            jumped = 1
    elif opcode == 0x19: #juf/nuf
        if (regs[3] & 16) if not mode & 1 else (not regs[3] & 16):
            regs[0] = (regs[arg1]) if not mode >> 1 else imm
            jumped = 1
    elif opcode == 0x1A: #jng/nng
        if (regs[3] & 32) if not mode & 1 else (not regs[3] & 32):
            regs[0] = (regs[arg1]) if not mode >> 1 else imm
            jumped = 1
    elif opcode == 0x1B: #jin/nin
        if (regs[3] & 64) if not mode & 1 else (not regs[3] & 64):
            regs[0] = (regs[arg1]) if not mode >> 1 else imm
            jumped = 1
    #0x1C: sdr not implemented
    #0x1D: gdr not implemented
    elif opcode == 0x1E: #deb
        print(regs[arg1])
    #0x1F: ram dump not implemented
    
    if not jumped:
        if regs[0] < len(rom) - 1:
            regs[0] += 2
        else: regs[0] = 0
    else: jumped = 0
    
    for i in range(16):
        if(regs[i] > 65535): regs[i] = 0
        if(regs[i] < 0): regs[i] = 65535
