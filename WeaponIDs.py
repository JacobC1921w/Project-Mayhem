import pymem
from offsets import *

# Get CSGO memory objects for reading and writing memory
try:
    CSGOObject = pymem.Pymem("csgo.exe")
    CSGOClient = pymem.pymem.process.module_from_name(CSGOObject.process_handle, "client.dll").lpBaseOfDll
except:
    print(u"\x1b[91;1m[-] \x1b[0mNo 'csgo.exe' process found! Please open csgo first, and start up a match!")
    exit(1)

lastWeaponID = 0

while True:
    # Get current player offset
    playerOffset = CSGOObject.read_uint(CSGOClient + signatures.dwLocalPlayer)

    if playerOffset:
        currentWeaponAddress = CSGOObject.read_uint(playerOffset + netvars.m_hActiveWeapon) & 0xFFF
        m_iBase = CSGOObject.read_uint(CSGOClient + signatures.dwEntityList + (currentWeaponAddress - 1) * 0x10)
        weaponID = CSGOObject.read_uint(m_iBase + netvars.m_iItemDefinitionIndex)
        if weaponID != lastWeaponID:
            lastWeaponID = weaponID
            print(weaponID)

        

        """scopeStatus = CSGOObject.read_uint(playerOffset + netvars.m_bIsScoped)
        if scopeStatus == 0:
            scopeStatus = "Non-Scoped"
        elif scopeStatus == 1:
            scopeStatus = "Scoped"
        else:
            scopeStatus = str(scopeStatus)
        print(" (" + scopeStatus + ")")"""