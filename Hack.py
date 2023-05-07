# region Import section
import pymem
from threading import Thread
from tkinter import *
from keyboard import wait as awaitKey
from tkinter import Label
from win32api import SetWindowLong
from win32con import WS_EX_COMPOSITED, WS_EX_LAYERED, WS_EX_NOACTIVATE, WS_EX_TOPMOST, WS_EX_TRANSPARENT, GWL_EXSTYLE
from pywintypes import HANDLE
from screeninfo import get_monitors
from time import sleep
from offsets import *
# endregion

# region CSGO process detection
# Get CSGO memory objects for reading and writing memory
try:
    CSGOObject = pymem.Pymem("csgo.exe")
    CSGOClient = pymem.pymem.process.module_from_name(CSGOObject.process_handle, "client.dll").lpBaseOfDll
except:
    print(u"\x1b[91;1m[-] \x1b[0mNo 'csgo.exe' process found! Please open csgo first, and start up a match!")
    exit(1)
# endregion

# region Global variables
# Initialize some variables
noFlash = noFlashThreadOn = noFlashThreadAlreadyStarted = False
triggerBot = triggerBotThreadOn = triggerBotThreadAlreadyStarted = False

chams = chamsThreadOn = chamsThreadAlreadyStarted = chamsPresetColorRunOnce = False
#             Enemy       Team
teamColors = [[0, 0, 0], [0, 0, 0]]

# Configure this stuff please
preSleepTime = 0.015            # Set to 0 for a super obvious triggerbot
postSleepTime = 0.150
noScopes = False
# endregion

# region TKinter window properties
mainWindow = Tk()

mainWindow.geometry("+" + str(get_monitors()[0].width-256) + "+12")

mainWindow.overrideredirect(True)
mainWindow.lift()
mainWindow.wm_attributes("-topmost", True)
mainWindow.wm_attributes("-disabled", True)
mainWindow.wm_attributes("-transparentcolor", "black")

hWindow = HANDLE(int(mainWindow.frame(), 16))
SetWindowLong(hWindow, GWL_EXSTYLE, (WS_EX_COMPOSITED | WS_EX_LAYERED | WS_EX_NOACTIVATE | WS_EX_TOPMOST | WS_EX_TRANSPARENT))

# endregion

# region Label properties
triggerBotLabel = Label(mainWindow, text="[ALT+1] Triggerbot = False", font=("Segoe UI", "12"), fg="white", bg="black", padx=5, pady=0, bd=0, highlightthickness=0, highlightbackground="black", anchor="w", height=1)
chamsLabel = Label(mainWindow, text="[ALT+2] Chams = False", font=("Segoe UI", "12"), fg="white", bg="black", padx=5, pady=0, bd=0, highlightthickness=0, highlightbackground="black", anchor="w", height=1)
noFlashLabel = Label(mainWindow, text="[ALT+3] NoFlash = False", font=("Segoe UI", "12"), fg="white", bg="black", padx=5, pady=0, bd=0, highlightthickness=0, highlightbackground="black", anchor="w", height=1)
# endregion

# region Triggerbot
print(u"\x1b[94;1m[>]\x1b[0m preSleepTime => " + str(preSleepTime))
print(u"\x1b[94;1m[>]\x1b[0m postSleepTime => " + str(postSleepTime))
print(u"\x1b[94;1m[>]\x1b[0m triggerBotMode => " + str(noScopes))

def triggerBotLoop():
    # Use globals from start of file
    global postSleepTime
    global preSleepTime
    global noScopes

    # Check wether thread should be disabled or not
    while True:
        if not triggerBotThreadOn:
            pass
        else:
            # Get current player offset
            playerOffset = CSGOObject.read_uint(CSGOClient + signatures.dwLocalPlayer)

            # If we're alive basically
            if playerOffset:

                # Get some values for our crosshair position, our team, and the entity list infront of us, aswell as weapon ID and scope status
                playerCrosshairPosition = CSGOObject.read_uint(playerOffset + netvars.m_iCrosshairId)
                playerTeam = CSGOObject.read_uint(playerOffset + netvars.m_iTeamNum)
                crosshairEntity = CSGOObject.read_uint(CSGOClient + signatures.dwEntityList + (playerCrosshairPosition - 1) * 0x10)

                # If someone is infront of us, get their team
                if crosshairEntity:
                    entityTeam = CSGOObject.read_uint(crosshairEntity + netvars.m_iTeamNum)
                
                    # If their not on our team, shoot them, and wait 150ms
                    if playerTeam != entityTeam:
                        
                        # Weapon analysis for noscope featuer
                        currentWeaponAddress = CSGOObject.read_uint(playerOffset + netvars.m_hActiveWeapon) & 0xFFF
                        weaponDefinitionsOffsetStart = CSGOObject.read_uint(CSGOClient + signatures.dwEntityList + (currentWeaponAddress - 1) * 0x10)

                        # Whenever the player buys a new weapon, this will throw an exception, we're just gonna reset the loop and ignore it
                        try:
                            weaponID = CSGOObject.read_uint(weaponDefinitionsOffsetStart + netvars.m_iItemDefinitionIndex)
                        except:
                            continue
                        scopeStatus = CSGOObject.read_uint(playerOffset + netvars.m_bIsScoped)
                        
                        # Dont use triggerbot if holding bombs
                        if weaponID in (43, 44, 45, 46, 47, 48):
                            continue

                        # Disallow no-scopes if option not set
                        if scopeStatus == 0:
                            if weaponID in (9, 11, 38, 40):
                                if not noScopes:
                                    continue
                        
                        if playerCrosshairPosition >=1 and playerCrosshairPosition <= 15:
                            sleep(preSleepTime)
                            CSGOObject.write_int(CSGOClient + signatures.dwForceAttack, 6)

                            # Desert eagle has alot of kickback, we're gonna add a bit more delay to it
                            if weaponID == 1:
                                sleep(postSleepTime + 0.200)
                            else:
                                sleep(postSleepTime)

def triggerBotOnClickHandler():
    # Use globals from start of file
    global triggerBot
    global triggerBotThreadOn
    global triggerBotThreadAlreadyStarted

    # Toggle trigger bot on button click
    if triggerBot:
        triggerBotLabel.config(text="[ALT+1] Triggerbot = False")
        triggerBot = False
    else:
        triggerBotLabel.config(text="[ALT+1] Triggerbot = True")
        triggerBot = True
    
    # Start thread if not started already
    if triggerBotThreadOn and not triggerBot:
        triggerBotThreadOn = False

    # Check wether thread is already started, if not then we will start it, if so we will simply allow the while True loop to play out
    elif not triggerBotThreadOn and triggerBot:
        if not triggerBotThreadAlreadyStarted:
            Thread(target=triggerBotLoop).start()
            triggerBotThreadAlreadyStarted = True
        triggerBotThreadOn = True

# Detect F1 key being used. This is alot less laggy than using the pynput keyboard listener. This has to be in its own thread due to tkinter :(
def triggerBotOnClickHandlerThread():
    while True:
        awaitKey("alt+1")
        triggerBotOnClickHandler()
        
Thread(target=triggerBotOnClickHandlerThread).start()

# endregion

# region Chams
def getChamsPresetColors():
    global teamColors

    # Get current player offset
    playerOffset = CSGOObject.read_uint(CSGOClient + signatures.dwLocalPlayer)

    # Iterate through all players in team
    for i in range (0, 33):
        renderedEntity = CSGOObject.read_uint(CSGOClient + signatures.dwEntityList + i * 0x10)

        # Check wether the rendered entity is actually in the game
        if renderedEntity:

            # Setup references for their team, and our team
            renderedEntityTeam = CSGOObject.read_uint(renderedEntity + netvars.m_iTeamNum)
            ourTeam = CSGOObject.read_uint(playerOffset + netvars.m_iTeamNum)

            # Set their default colors depending on what team they are
            if renderedEntityTeam != ourTeam:
                teamColors[0][0] = CSGOObject.read_int(renderedEntity + 0x70)
                teamColors[0][1] = CSGOObject.read_int(renderedEntity + 0x71)
                teamColors[0][2] = CSGOObject.read_int(renderedEntity + 0x72)
            else:
                teamColors[1][0] = CSGOObject.read_int(renderedEntity + 0x70)
                teamColors[1][1] = CSGOObject.read_int(renderedEntity + 0x71)
                teamColors[1][2] = CSGOObject.read_int(renderedEntity + 0x72)



def chamsLoop():
    while True:

        # Get current player offset
        playerOffset = CSGOObject.read_uint(CSGOClient + signatures.dwLocalPlayer)

        # Iterate through all players in team
        for i in range (0, 33):
            renderedEntity = CSGOObject.read_uint(CSGOClient + signatures.dwEntityList + i * 0x10)

            # Check wether the rendered entity is actually in the game` `
            if renderedEntity:

                # Setup references for their team, and our team
                renderedEntityTeam = CSGOObject.read_uint(renderedEntity + netvars.m_iTeamNum)
                ourTeam = CSGOObject.read_uint(playerOffset + netvars.m_iTeamNum)

                # Set their color to red if they are an enemy, and green if they are not
                if renderedEntityTeam != ourTeam:
                    if not chamsThreadOn:
                        CSGOObject.write_int(renderedEntity + 0x70, teamColors[0][0])
                        CSGOObject.write_int(renderedEntity + 0x71, teamColors[0][1])
                        CSGOObject.write_int(renderedEntity + 0x72, teamColors[0][2])
                    else:
                        CSGOObject.write_int(renderedEntity + 0x70, (255))
                        CSGOObject.write_int(renderedEntity + 0x71, (0))
                        CSGOObject.write_int(renderedEntity + 0x72, (0))
                else:
                    if not chamsThreadOn:
                        CSGOObject.write_int(renderedEntity + 0x70, teamColors[1][0])
                        CSGOObject.write_int(renderedEntity + 0x71, teamColors[1][1])
                        CSGOObject.write_int(renderedEntity + 0x72, teamColors[1][2])
                    else:
                        CSGOObject.write_int(renderedEntity + 0x70, (0))
                        CSGOObject.write_int(renderedEntity + 0x71, (255))
                        CSGOObject.write_int(renderedEntity + 0x72, (0))





def chamsOnClickHandler():
    # Use globals from start of file
    global chams
    global chamsThreadOn
    global chamsThreadAlreadyStarted

    # Toggle chams on button click
    if chams:
        chamsLabel.config(text="[ALT+2] Chams = False")
        chams = False
    else:
        chamsLabel.config(text="[ALT+2] Chams = True")
        chams = True
    
    # Start thread if not started already
    if chamsThreadOn and not chams:
        chamsThreadOn = False

    # Check wether thread is already started, if not then we will start it, if so we will simply allow the while True loop to play out
    elif not chamsThreadOn and chams:
        if not chamsThreadAlreadyStarted:
            Thread(target=chamsLoop).start()
            chamsThreadAlreadyStarted = True
        chamsThreadOn = True

# Get the default colors for the ability to disable
getChamsPresetColors()

# Detect F2 key being used. This is alot less laggy than using the pynput keyboard listener. This has to be in its own thread due to tkinter :(
def chamsOnClickHandlerThread():
    while True:
        awaitKey("alt+2")
        chamsOnClickHandler()

Thread(target=chamsOnClickHandlerThread).start()

# endregion

# region NoFlash
def noFlashLoop():
    # Use globals from start of file
    global noFlashThreadOn
    
    # Check wether thread should be disabled or not
    while True:
        if not noFlashThreadOn:
            pass
        else:
            # Get current player offset
            playerOffset = CSGOObject.read_uint(CSGOClient + signatures.dwLocalPlayer)

            if playerOffset:
                if CSGOObject.read_uint(playerOffset +  netvars.m_flFlashMaxAlpha) > 0.0:
                    CSGOObject.write_float(playerOffset +  netvars.m_flFlashMaxAlpha, float(0))

            sleep(.001)

def noFlashOnClickHandler():
    # Use globals from start of file
    global noFlash
    global noFlashThreadOn
    global noFlashThreadAlreadyStarted

    # Toggle trigger bot on button click
    if noFlash:
        noFlashLabel.config(text="[ALT+3] No Flash = False")
        noFlash = False
    else:
        noFlashLabel.config(text="[ALT+3] No Flash = True")
        noFlash = True
    
    # Start thread if not started already
    if noFlashThreadOn and not noFlash:
        noFlashThreadOn = False

    # Check wether thread is already started, if not then we will start it, if so we will simply allow the while True loop to play out
    elif not noFlashThreadOn and noFlash:
        if not noFlashThreadAlreadyStarted:
            Thread(target=noFlashLoop).start()
            noFlashThreadAlreadyStarted = True
        noFlashThreadOn = True

# Detect F3 key being used. This is alot less laggy than using the pynput keyboard listener. This has to be in its own thread due to tkinter :(
def noFlashOnClickHandlerThread():
    while True:
        awaitKey("alt+3")
        noFlashOnClickHandler()

Thread(target=noFlashOnClickHandlerThread).start()

# endregion

# region Final TKinter setup and rendering
triggerBotLabel.pack(side="top", fill="x")
chamsLabel.pack(side="top", fill="x")
noFlashLabel.pack(side="top", fill="x")

mainWindow.mainloop()
# endregion