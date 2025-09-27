#coding: utf-8
import time, json, math

from lupa import LuaRuntime

from utils import Utils
from ByteArray import ByteArray
from Identifiers import Identifiers

import asyncio

class Lua:
    def __init__(this, room, server):
        # Others
        this.room = room
        this.server = server
        # NoneType
        this.owner = None
        this.runtime = None
        this.running = True
        # String
        this.name = ""
        this.script = ""
        this.lastmsg = ""
        this.roomFix = False
        # Dict
        this.RoomObjects = {}
        this.roomAreas = []
        this.imagesadd = []
        this.loops = {}
        #List
        this.HiddenCommands = []
        # Integer
        this.LastRoomObjectID = 2000
        this.lastloopid = 1

    def SetupRuntimeGlobals(this):
        if this.runtime is None:
            return
        this.globals = this.runtime.globals()

        this.globals['io'] = None
        this.globals['dofile'] = None
        this.globals['module'] = None
        this.globals['require'] = None
        this.globals['loadfile'] = None
        this.globals['table']['foreach'] = this.tableForeach
        
        this.globals['math']['atan2'] = math.atan2

        this.globals['os']['exit'] = None
        this.globals['os']['getenv'] = None
        this.globals['os']['remove'] = None
        this.globals['os']['rename'] = None
        this.globals['os']['execute'] = None
        this.globals['os']['setlocale'] = None
        this.globals['os']['time'] = lambda: int(time.time() * 1000)

        this.globals['print'] = this.sendLuaMessage

        this.globals['bit32'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        this.globals['bit32']['band'] = this.bandb
        
        this.globals['system'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        this.globals['system']['bindKeyBoard'] = this.room.bindKeyBoard
        this.globals['system']['bindKeyboard'] = this.room.bindKeyBoard
        this.globals['system']['disableChatCommandDisplay'] = this.disableChatCommandDisplay
        this.globals['system']['bindMouse'] = this.room.bindMouse
        this.globals['system']['exit'] = this.ModuleStop
        this.globals['system']['loadPlayerData'] = this.loadPlayerData
        this.globals['system']['savePlayerData'] = this.savePlayerData
        this.globals['system']['newTimer'] = this.newTimer
        this.globals['system']['removeTimer'] = this.removeTimer
        this.globals['system']['addBot'] = this.addBot
        this.globals['system']['loadFile'] = this.loadFile
        this.globals['system']['saveFile'] = this.saveFile
        this.globals['system']['players'] = this.getplayers

        this.globals['ui'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        this.globals['ui']['showColorPicker'] = this.room.showColorPicker
        this.globals['ui']['setMapName'] = this.setMapName
        this.globals['ui']['setShamanName'] = this.setShamanName
        
        this.globals['ui']['addTextArea'] = this.addTextArea
        this.globals['ui']['removeTextArea'] = this.removeTextArea
        this.globals['ui']['updateTextArea'] = this.updateTextArea
        this.globals['ui']['addPopup'] = this.addPopup
        this.globals['ui']['addLog'] = this.addLog
        
        this.globals['string']['rep'] = lambda t, x: str(t * int(x))

        this.globals['tfm'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        this.globals['tfm']['enum'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        this.globals['tfm']['enum']['shamanObject'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        this.globals['tfm']['enum']['emote'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        this.globals['tfm']['enum']['bonus'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        this.globals['tfm']['enum']['ground'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        this.globals['tfm']['enum']['particle'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        this.globals['tfm']['exec'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        this.globals['tfm']['get'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        this.globals['tfm']['get']['misc'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        this.globals['tfm']['get']['room'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        
        this.globals['tfm']['enum']['shamanObject']['arrow'] = 0
        this.globals['tfm']['enum']['shamanObject']['littleBox'] = 1
        this.globals['tfm']['enum']['shamanObject']['box'] = 2
        this.globals['tfm']['enum']['shamanObject']['littleBoard'] = 3
        this.globals['tfm']['enum']['shamanObject']['board'] = 4
        this.globals['tfm']['enum']['shamanObject']['ball'] = 6
        this.globals['tfm']['enum']['shamanObject']['trampoline'] = 7
        this.globals['tfm']['enum']['shamanObject']['anvil'] = 10
        this.globals['tfm']['enum']['shamanObject']['cannon'] = 19
        this.globals['tfm']['enum']['shamanObject']['bomb'] = 23
        this.globals['tfm']['enum']['shamanObject']['orangePortal'] = 26
        this.globals['tfm']['enum']['shamanObject']['blueBalloon'] = 28
        this.globals['tfm']['enum']['shamanObject']['redBalloon'] = 29
        this.globals['tfm']['enum']['shamanObject']['greenBalloon'] = 30
        this.globals['tfm']['enum']['shamanObject']['yellowBalloon'] = 31
        this.globals['tfm']['enum']['shamanObject']['rune'] = 32
        this.globals['tfm']['enum']['shamanObject']['chicken'] = 33
        this.globals['tfm']['enum']['shamanObject']['snowBall'] = 34
        this.globals['tfm']['enum']['shamanObject']['cupidonArrow'] = 35
        this.globals['tfm']['enum']['shamanObject']['apple'] = 39
        this.globals['tfm']['enum']['shamanObject']['sheep'] = 40
        this.globals['tfm']['enum']['shamanObject']['littleBoardIce'] = 45
        this.globals['tfm']['enum']['shamanObject']['littleBoardChocolate'] = 46
        this.globals['tfm']['enum']['shamanObject']['iceCube'] = 54
        this.globals['tfm']['enum']['shamanObject']['cloud'] = 57
        this.globals['tfm']['enum']['shamanObject']['bubble'] = 59
        this.globals['tfm']['enum']['shamanObject']['tinyBoard'] = 60
        this.globals['tfm']['enum']['shamanObject']['companionCube'] = 61
        this.globals['tfm']['enum']['shamanObject']['stableRune'] = 62
        this.globals['tfm']['enum']['shamanObject']['ballonFish'] = 65
        this.globals['tfm']['enum']['shamanObject']['longBoard'] = 67
        this.globals['tfm']['enum']['shamanObject']['triangle'] = 68
        this.globals['tfm']['enum']['shamanObject']['sBoard'] = 69
        this.globals['tfm']['enum']['shamanObject']['paperPlane'] = 80
        this.globals['tfm']['enum']['shamanObject']['rock'] = 85
        this.globals['tfm']['enum']['shamanObject']['pumpkinBall'] = 89
        this.globals['tfm']['enum']['shamanObject']['tombstone'] = 90
        this.globals['tfm']['enum']['shamanObject']['paperBall'] = 95
        
        this.globals['tfm']['enum']['emote']['dance'] = 0
        this.globals['tfm']['enum']['emote']['laugh'] = 1
        this.globals['tfm']['enum']['emote']['cry'] = 2
        this.globals['tfm']['enum']['emote']['kiss'] = 3
        this.globals['tfm']['enum']['emote']['angry'] = 4
        this.globals['tfm']['enum']['emote']['clap'] = 5
        this.globals['tfm']['enum']['emote']['sleep'] = 6
        this.globals['tfm']['enum']['emote']['facepaw'] = 7
        this.globals['tfm']['enum']['emote']['sit'] = 8
        this.globals['tfm']['enum']['emote']['confetti'] = 9
        this.globals['tfm']['enum']['emote']['flag'] = 10
        this.globals['tfm']['enum']['emote']['marshmallow'] = 11
        this.globals['tfm']['enum']['emote']['selfie'] = 12
        this.globals['tfm']['enum']['emote']['highfive'] = 13
        this.globals['tfm']['enum']['emote']['highfive_1'] = 14
        this.globals['tfm']['enum']['emote']['highfive_2'] = 15
        this.globals['tfm']['enum']['emote']['partyhorn'] = 16
        this.globals['tfm']['enum']['emote']['hug'] = 17
        this.globals['tfm']['enum']['emote']['hug_1'] = 18
        this.globals['tfm']['enum']['emote']['hug_2'] = 19
        this.globals['tfm']['enum']['emote']['jigglypuff'] = 20
        this.globals['tfm']['enum']['emote']['kissing'] = 21
        this.globals['tfm']['enum']['emote']['kissing_1'] = 22
        this.globals['tfm']['enum']['emote']['kissing_2'] = 23
        this.globals['tfm']['enum']['emote']['carnaval'] = 24
        this.globals['tfm']['enum']['emote']['rockpaperscissors'] = 25
        this.globals['tfm']['enum']['emote']['rockpaperscissors_1'] = 26
        this.globals['tfm']['enum']['emote']['rockpaperscissor_2'] = 27
        
        this.globals['tfm']['enum']['bonus']['point'] = 0
        this.globals['tfm']['enum']['bonus']['speed'] = 1
        this.globals['tfm']['enum']['bonus']['death'] = 2
        this.globals['tfm']['enum']['bonus']['spring'] = 3
        this.globals['tfm']['enum']['bonus']['booster'] = 5
        this.globals['tfm']['enum']['bonus']['electricArc'] = 6
        
        this.globals['tfm']['enum']['ground']['wood'] = 0
        this.globals['tfm']['enum']['ground']['ice'] = 1
        this.globals['tfm']['enum']['ground']['trampoline'] = 2
        this.globals['tfm']['enum']['ground']['lava'] = 3
        this.globals['tfm']['enum']['ground']['chocolate'] = 4
        this.globals['tfm']['enum']['ground']['earth'] = 5
        this.globals['tfm']['enum']['ground']['grass'] = 6
        this.globals['tfm']['enum']['ground']['sand'] = 7
        this.globals['tfm']['enum']['ground']['cloud'] = 8
        this.globals['tfm']['enum']['ground']['water'] = 9
        this.globals['tfm']['enum']['ground']['stone'] = 10
        this.globals['tfm']['enum']['ground']['snow'] = 11
        this.globals['tfm']['enum']['ground']['rectangle'] = 12
        this.globals['tfm']['enum']['ground']['circle'] = 13
        this.globals['tfm']['enum']['ground']['invisible'] = 14
        this.globals['tfm']['enum']['ground']['web'] = 15
        this.globals['tfm']['enum']['ground']['yellowGrass'] = 17
        this.globals['tfm']['enum']['ground']['pinkGrass'] = 18
        this.globals['tfm']['enum']['ground']['acid'] = 19
        
        this.globals['tfm']['enum']['particle']['whiteGlitter'] = 0
        this.globals['tfm']['enum']['particle']['blueGlitter'] = 1
        this.globals['tfm']['enum']['particle']['orangeGlitter'] = 2
        this.globals['tfm']['enum']['particle']['cloud'] = 3
        this.globals['tfm']['enum']['particle']['dullWhiteGlitter'] = 4
        this.globals['tfm']['enum']['particle']['heart'] = 5
        this.globals['tfm']['enum']['particle']['bubble'] = 6
        this.globals['tfm']['enum']['particle']['tealGlitter'] = 9
        this.globals['tfm']['enum']['particle']['spirit'] = 10
        this.globals['tfm']['enum']['particle']['yellowGlitter'] = 11
        this.globals['tfm']['enum']['particle']['ghostSpirit'] = 12
        this.globals['tfm']['enum']['particle']['redGlitter'] = 13
        this.globals['tfm']['enum']['particle']['waterBubble'] = 14
        this.globals['tfm']['enum']['particle']['plus1'] = 15
        this.globals['tfm']['enum']['particle']['plus10'] = 16
        this.globals['tfm']['enum']['particle']['plus12'] = 17
        this.globals['tfm']['enum']['particle']['plus14'] = 18
        this.globals['tfm']['enum']['particle']['plus16'] = 19
        this.globals['tfm']['enum']['particle']['meep'] = 20
        this.globals['tfm']['enum']['particle']['redConfetti'] = 21
        this.globals['tfm']['enum']['particle']['greenConfetti'] = 22
        this.globals['tfm']['enum']['particle']['blueConfetti'] = 23
        this.globals['tfm']['enum']['particle']['yellowConfetti'] = 24
        this.globals['tfm']['enum']['particle']['diagonalRain'] = 25
        this.globals['tfm']['enum']['particle']['curlyWind'] = 26
        this.globals['tfm']['enum']['particle']['wind'] = 27
        this.globals['tfm']['enum']['particle']['rain'] = 28
        this.globals['tfm']['enum']['particle']['star'] = 29
        this.globals['tfm']['enum']['particle']['littleRedHeart'] = 30
        this.globals['tfm']['enum']['particle']['littlePinkHeart'] = 31
        this.globals['tfm']['enum']['particle']['daisy'] = 32
        this.globals['tfm']['enum']['particle']['bell'] = 33
        this.globals['tfm']['enum']['particle']['egg'] = 34
        this.globals['tfm']['enum']['particle']['projection'] = 35
        this.globals['tfm']['enum']['particle']['mouseTeleportation'] = 36
        this.globals['tfm']['enum']['particle']['shamanTeleportation'] = 37
        this.globals['tfm']['enum']['particle']['lollipopConfetti'] = 38
        this.globals['tfm']['enum']['particle']['yellowCandyConfetti'] = 39
        this.globals['tfm']['enum']['particle']['pinkCandyConfetti'] = 40
        
        this.globals['tfm']['exec']['chatMessage'] = this.chatMessage
        this.globals['tfm']['exec']['playerVictory'] = this.playerVictory
        this.globals['tfm']['exec']['addConjuration'] = this.addConjuration
        this.globals['tfm']['exec']['respawnPlayer'] = this.respawnPlayer
        this.globals['tfm']['exec']['removeCheese'] = this.removeCheese
        this.globals['tfm']['exec']['giveCheese'] = this.giveCheese
        this.globals['tfm']['exec']['giveMeep'] = this.giveMeep
        this.globals['tfm']['exec']['addJoint'] = this.addJoint
        this.globals['tfm']['exec']['removeJoint'] = this.removeJoint
        this.globals['tfm']['exec']['killPlayer'] = this.killPlayer
        this.globals['tfm']['exec']['displayParticle'] = this.displayParticle
        this.globals['tfm']['exec']['setGameTime'] = this.setGameTime
        this.globals['tfm']['exec']['bindKeyBoard'] = this.room.bindKeyBoard
        this.globals['tfm']['exec']['bindKeyboard'] = this.room.bindKeyBoard
        this.globals['tfm']['exec']['setShaman'] = this.setShaman
        this.globals['tfm']['exec']['setTransformationPlayer'] = this.setTransformationPlayer
        this.globals['tfm']['exec']['addShamanObject'] = this.addShamanObject
        this.globals['tfm']['exec']['removeObject'] = this.room.removeObject
        this.globals['tfm']['exec']['moveObject'] = this.moveObject
        this.globals['tfm']['exec']['movePlayer'] = this.room.movePlayer
        this.globals['tfm']['exec']['bindMouse'] = this.room.bindMouse
        this.globals['tfm']['exec']['newGame'] = this.newGame
        this.globals['tfm']['exec']['setCatPlayer'] = this.setCatPlayer
        this.globals['tfm']['exec']['moveCheese'] = this.moveCheese
        this.globals['tfm']['exec']['addTextArea'] = this.addTextArea
        this.globals['tfm']['exec']['explosion'] = this.explosion
        this.globals['tfm']['exec']['removeTextArea'] = this.removeTextArea
        this.globals['tfm']['exec']['updateTextArea'] = this.updateTextArea
        this.globals['tfm']['exec']['addPopup'] = this.addPopup
        this.globals['tfm']['exec']['attachBalloon'] = this.attachBalloon
        this.globals['tfm']['exec']['lowerSyncDelay'] = this.lowerSyncDelay
        this.globals['tfm']['exec']['setUIMapName'] = this.setMapName
        this.globals['tfm']['exec']['setUIShamanName'] = this.setShamanName
        this.globals['tfm']['exec']['addImage'] = this.addImage
        this.globals['tfm']['exec']['removeImage'] = this.removeImage
        this.globals['tfm']['exec']['addBonus'] = this.addBonus
        this.globals['tfm']['exec']['getPlayerSync'] = this.room.getSyncCode
        this.globals['tfm']['exec']['removeBonus'] = this.removeBonus
        this.globals['tfm']['exec']['playEmote'] = this.playEmote
        this.globals['tfm']['exec']['freezePlayer'] = this.freezePlayer
        this.globals['tfm']['exec']['giveConsumables'] = this.giveConsumables
        this.globals['tfm']['exec']['setRoomMaxPlayers'] = this.setRoomMaxPlayers
        this.globals['tfm']['exec']['setNameColor'] = this.room.setNameColor
        this.globals['tfm']['exec']['setPlayerScore'] = this.setPlayerScore
        this.globals['tfm']['exec']['addPhysicObject'] = this.room.addPhysicObject
        this.globals['tfm']['exec']['removePhysicObject'] = this.room.removeObject
        this.globals['tfm']['exec']['changePlayerSize'] = this.changePlayerSize
        this.globals['tfm']['exec']['setRoomPassword'] = this.setRoomPassword

        this.globals['tfm']['exec']['disableAfkDeath'] = this.disableAfkDeath
        this.globals['tfm']['exec']['disableAllShamanSkills'] = this.disableAllShamanSkills
        this.globals['tfm']['exec']['disableAutoNewGame'] = this.disableAutoNewGame
        this.globals['tfm']['exec']['disableAutoScore'] = this.disableAutoScore
        this.globals['tfm']['exec']['disableAutoShaman'] = this.disableAutoShaman
        this.globals['tfm']['exec']['disableAutoTimeLeft'] = this.disableAutoTimeLeft
        this.globals['tfm']['exec']['disableDebugCommand'] = this.disableDebugCommand
        this.globals['tfm']['exec']['disableMinimalistMode'] = this.disableMinimalistMode
        this.globals['tfm']['exec']['disableMortCommand'] = this.disableMortCommand
        this.globals['tfm']['exec']['disablePrespawnPreview'] = this.disablePrespawnPreview
        this.globals['tfm']['exec']['disableWatchCommand'] = this.disableWatchCommand
        this.globals['tfm']['exec']['disablePhysicalConsumables'] = this.disablePhysicalConsumables
        this.globals['tfm']['exec']['snow'] = this.snow
        this.globals['tfm']['exec']['giveEventGift'] = this.giveEventGift
        this.globals['tfm']['exec']['setVampirePlayer'] = this.setVampirePlayer

        this.globals['tfm']['get']['misc']['apiVersion'] = "0.28"
        this.globals['tfm']['get']['misc']['transformiceVersion'] = this.server.Version

        this.globals['tfm']['get']['room']['objectList'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        this.globals['tfm']['get']['room']['xmlMapInfo'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        this.globals['tfm']['get']['room']['xmlMapInfo']['permCode'] = this.room.mapPerma
        this.globals['tfm']['get']['room']['xmlMapInfo']['author'] = this.room.mapName
        this.globals['tfm']['get']['room']['xmlMapInfo']['mapCode'] = this.room.mapCode
        this.globals['tfm']['get']['room']['xmlMapInfo']['xml'] = this.room.mapXML
        this.RefreshTFMGet()

    def UpdateObjectList(this, olist={}):
        this.RoomObjects = olist

    def RefreshTFMGet(this):
        this.globals['tfm']['get']['room']['name'] = this.room.name
        this.globals['tfm']['get']['room']['community'] = this.room.community
        this.globals['tfm']['get']['room']['language'] = this.room.community
        this.globals['tfm']['get']['room']['currentMap'] = this.room.mapCode
        this.globals['tfm']['get']['room']['maxPlayers'] = this.room.maxPlayers
        this.globals['tfm']['get']['room']['mirroredMap'] = this.room.mapInverted
        this.globals['tfm']['get']['room']['uniquePlayers'] = len(this.room.clients)
        this.globals['tfm']['get']['room']['passwordProtected'] = this.room.roomPassword != ""
        this.globals['tfm']['get']['room']['isTribeHouse'] = this.room.isTribeHouse

        this.globals['tfm']['get']['room']['objectList'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
        this.globals['tfm']['get']['room']['playerList'] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')

        for object in this.RoomObjects.values():
            this.globals['tfm']['get']['room']['objectList'][object['id']] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
            this.globals['tfm']['get']['room']['objectList'][object['id']]['id'] = object['id']
            this.globals['tfm']['get']['room']['objectList'][object['id']]['type'] = object['type']
            this.globals['tfm']['get']['room']['objectList'][object['id']]['angle'] = object['angle']
            this.globals['tfm']['get']['room']['objectList'][object['id']]['ghost'] = object['ghost']
            this.globals['tfm']['get']['room']['objectList'][object['id']]['vx'] = object['velX']
            this.globals['tfm']['get']['room']['objectList'][object['id']]['vy'] = object['velY']
            this.globals['tfm']['get']['room']['objectList'][object['id']]['x'] = object['posX']
            this.globals['tfm']['get']['room']['objectList'][object['id']]['y'] = object['posY']
            this.globals['tfm']['get']['room']['objectList'][object['id']]['rotationSpeed'] = object['rotationSpeed']
            this.globals['tfm']['get']['room']['objectList'][object['id']]['stationary'] = object['stationary']

        for player in this.room.clients.values():
            this.globals['tfm']['get']['room']['playerList'][player.playerName] = this.runtime.eval('setmetatable({}, {__len = function(self) local count = 0;for i in next, self do count = count+1 end;return count;end})')
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["community"] = player.langue.lower()
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["language"] = player.langue.lower()
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["hasCheese"] = player.hasCheese
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["id"] = player.playerID
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["cheeses"] = player.cheeseCount
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["gender"] = player.gender
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["shamanMode"] = player.shamanType
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["inHardMode"] = player.shamanType
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["isDead"] = player.isDead
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["isFacingRight"] = player.isMovingRight
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["isJumping"] = player.isJumping
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["isShaman"] = player.isShaman
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["isVampire"] = player.isVampire
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["look"] = player.playerLook
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["movingLeft"] = player.isMovingLeft
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["movingRight"] = player.isMovingRight
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["playerName"] = player.playerName
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["registrationDate"] = player.regDate
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["score"] = player.playerScore
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["title"] = player.titleNumber
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["tribeId"] = player.tribeCode
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["shamanMode"] = player.shamanType
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["tribeName"] = player.tribeName
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["vx"] = player.velX
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["vy"] = player.velY
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["x"] = player.posX
            this.globals['tfm']['get']['room']['playerList'][player.playerName]["y"] = player.posY

    def FixUnicodeError(this, text=u""):
        if isinstance(text, bytes):
            text = text.decode()
        return text

    def newTimer(this, callback, _time=0, loop=False, *args):
        _time = _time / 1000
        if loop:
            this.lastloopid+=1
            d = this.createLoop(this.lastloopid, _time, lambda: callback(*args))
            this.loops[this.lastloopid] = d
            return this.lastloopid
        else:
            this.lastloopid+=1
            d = this.server.loop.call_later(_time, lambda: callback(*args))
            this.loops[this.lastloopid] = d
            return this.lastloopid
    
    def removeTimer(this, _id):
        _id = int(_id)
        if _id in this.loops:
            this.loops[_id].cancel()
            while _id in this.loops:
                del this.loops[_id]

    def createLoop(this, _id, _time, callback):
        if not this.running: return
        this.server.loop.call_later(0, callback)
        d = this.server.loop.call_later(_time, lambda: this.createLoop(_id, _time, callback))
        if _id in this.loops:
            this.loops[_id] = d
        else:
            return d
    
    def freezePlayer(this, playerName, freeze=True):
        player = this.room.clients.get(playerName)
        if player:
            player.sendPacket([100, 66], ByteArray().writeBoolean(freeze).toByteArray())

    def setPlayerScore(this, playerName, score, add = False):
        if add is None:
            add = False
        player = this.room.clients.get(playerName)
        if player:
            if add:
                player.playerScore += score
            else:
                player.playerScore = score
            this.room.sendAll(Identifiers.send.Set_Player_Score, ByteArray().writeInt(player.playerCode).writeShort(player.playerScore).toByteArray())

    def disablePhysicalConsumables(this, yes=True):
        this.room.disablePhysicalConsumables = yes
    
    def htmlfix(this, text):
        if "<a" in text:
            if not "</a>" in text:
                text = text + "</a>"
        if "<p" in text:
            if not "</p>" in text:
                text = text + "</p>"
        if "<font" in text:
            if not "</font>" in text:
                text = text + "</font>"
        return text
    
    def addJoint(this, id=0, ground1=0, ground2=0, jointDefinition={}):
        this.room.sendAll(Identifiers.send.Add_Joint, [id, ground1, ground2, jointDefinition])
    
    def removeJoint(this, id=0):
        this.room.sendAll(Identifiers.send.Remove_Joint, [id])
        
    def disableWatchCommand(this, tor):
        if tor:
            pass
            
    def disablePrespawnPreview(this, tor):
        if tor:
            pass
            
    def disableMortCommand(this, tor=True):
        if tor:
            this.room.blacklistcmd.append("mort")
        else:
            if "mort" in this.room.blacklistcmd:
                this.room.blacklistcmd.remove("mort")
            
    def disableMinimalistMode(this, tor):
        if tor:
            pass
    
    def setRoomPassword(this, password):
        this.room.roomPassword = password
    
    def disableDebugCommand(this, tor=True):
        if tor:
            this.room.blacklistcmd.append("debug")
        else:
            if "debug" in this.room.blacklistcmd:
                this.room.blacklistcmd.remove("debug")

    def giveConsumables(this, playerName, consumableId, amount=1):
        player = this.room.clients.get(playerName)
        if player:
            player.sendGiveConsumables(consumableId, amount)

    def addLog(this, text, playerName):
        player = this.room.clients.get(playerName)
        if player != None:
            player.sendLogMessage(text)

    def chatMessage(this, message="", target=None):
        if this.lastmsg == message: return
        this.lastmsg = message
        if target == "" or target is None:
            for player in this.room.clients.values():
                player.sendMessage(this.FixUnicodeError(message))
        else:
            player = this.room.clients.get(target)

            if player != None:
                player.sendMessage(this.FixUnicodeError(message))

    def setRoomMaxPlayers(this, maxPlayers):
        this.room.maxPlayers = maxPlayers
        
    def snow(this, d=60, i=10):
        this.room.startSnow(int(d), int(i), True)
        
    def setVampirePlayer(this, playerName):
        client = this.room.clients.get(playerName)
        if client != None:
            client.sendVampireMode(False)
        
    def addConjuration(this, x, y, bl):
        this.room.sendAll(Identifiers.old.send.Add_Conjuration, [x, y, bl])
        this.server.loop.call_later(10, this.room.sendAll, Identifiers.old.send.Conjuration_Destroy, [int(x), int(y)])
    
    def explosion(this, xPosition=0, yPosition=0, power=0, distance=0, miceOnly=False):
        this.room.sendAll(Identifiers.send.Explosion, [int(xPosition), int(yPosition), int(power), int(distance), bool(miceOnly)])
    
    def moveObject(this, id=0, xy=0, vy=0, d=False, x=0, y=0, r=False, i=0, b=False):
        this.RoomObjects[id]['velX'] = x
        this.RoomObjects[id]['velY'] = y
        this.RoomObjects[id]['posX'] = xy
        this.RoomObjects[id]['posY'] = vy
        this.RoomObjects[id]['angle'] = i
        this.RefreshTFMGet()
        packet = ByteArray()
        packet.writeInt(id)
        packet.writeShort(xy)
        packet.writeShort(vy)
        packet.writeBoolean(d)
        packet.writeShort(x)
        packet.writeShort(y)
        packet.writeBoolean(r)
        packet.writeShort(i)
        packet.writeBoolean(b)
        this.room.sendAll(Identifiers.send.Move_Object, packet.toByteArray())
        
    def changePlayerSize(this, name, size=1):
        size = float(size)
        size = 5.0 if size > 5.0 else size
        size = int(size * 100)
        playerName = Utils.parsePlayerName(name)
        if playerName == "*":
            for player in this.room.clients.copy().values():
                this.room.sendAll(Identifiers.send.Mouse_Size, ByteArray().writeInt(player.playerCode).writeShort(size).writeBoolean(False).toByteArray())
        else:
            player = this.server.players.get(playerName)
            if player != None:
                this.room.sendAll(Identifiers.send.Mouse_Size, ByteArray().writeInt(player.playerCode).writeShort(size).writeBoolean(False).toByteArray())

    def getplayers(this):
        return len(this.room.clients)
    
    def loadFile(this, _id=0):
        data = ""
        try:
            with open(f"./include/lua/luaDatas/{_id}.dat", "r") as f:
                data = f.read()
                if data == None:
                    data = ""
        except:
            data = ""
        this.emit("FileLoaded", (_id, data))
        return data != None
    
    def attachBalloon(this, playerName="", isAttached=True, colorType=1, ghost=False, speed=1):
        colorType = 4 if colorType > 4 else 1 if colorType < 1 else colorType
        player = this.server.players.get(playerName)
        if player != None:
            p = this.room.objectID+1
            player.sendPlaceObject(p,28,player.posX,player.posY-25,0,0,0,not ghost,True,colorType)
            if isAttached:
                this.room.sendAll([144, 9], ByteArray().writeByte(-1).toByteArray())
                this.room.sendAll([144, 20], ByteArray().writeInt(player.playerCode).writeInt(p).writeInt(speed*1000).toByteArray())
            
    def saveFile(this, data="", _id=0):
        if len(data) > 64000:
            return
        with open(f"./include/lua/luaDatas/{_id}.dat", "w") as f:
            f.write(data)
        this.emit("FileSaved", (_id))
                
    def loadPlayerData(this, playerName):
        data = ""
        try:
            with open(f"./include/lua/playerDatas/{playerName}", "r") as f:
                data = f.read()
                if data == None:
                    data = ""
        except:
                data = ""
        this.emit("PlayerDataLoaded", (playerName, data))
        return data != None
        
    def lowerSyncDelay(this, playerName=""):
        pass
        
    def addBot(this, npcId, npcName, npcTitle, npcLook, npcPosX, npcPosY, starePlayer, shop="", x=""):
        client = this.room.clients.get(starePlayer)       
        if client != None:
            client.sendPacket(Identifiers.send.NPC, ByteArray().writeInt(npcId).writeUTF(npcName).writeShort(npcTitle).writeBoolean(starePlayer).writeUTF(npcLook).writeShort(npcPosX).writeShort(npcPosY).writeShort(1).writeByte(11).writeShort(0).toByteArray())

    def savePlayerData(this, playerName, data):
        if len(data) > 64000:
            return
        with open(f"./include/lua/playerDatas/{playerName}", "w") as f:
            f.write(data)
    
    def bandb(this, x, y):
        return 0
    
    def giveEventGift(this, targetPlayer="", done=""):
        if done == "titre_carnaval_lua":
            pass

    def addImage(this, imageName = "", target = "", xPosition = 50, yPosition = 50, targetPlayer = "", scaleX = 1, scaleY = 1,angle = 0,alpha = 1,AnchorX=0,AnchorY=0):
        if imageName is None:
            imageName = ""
        if target is None:
            target = ""
        if xPosition is None:
            xPosition == 50
        if yPosition is None:
            yPosition = 50
        if targetPlayer is None:
            targetPlayer = ""
        if scaleX is None:
            scaleX = 1
        if scaleY is None:
            scaleY = 1
        if angle is None:
            angle = 0
        if alpha is None:
            alpha = 1
        if AnchorX is None:
            AnchorX = 0
        if AnchorY is None:
            AnchorY = 0
        packet = ByteArray()
        this.room.lastImageID += 1
        packet.writeInt(this.room.lastImageID)
        this.imagesadd.append(this.room.lastImageID)
        packet.writeUTF(imageName)
        packet.writeByte(1 if target.startswith("#") else 2 if target.startswith("$") else 3 if target.startswith("%") else 4 if target.startswith("?") else 5 if target.startswith("_") else 6 if target.startswith("!") else 7 if target.startswith("&") else 8 if target.startswith(":") else 9 if target.startswith("+") else 0)
        target = target[1:]
        if '.0' in target: target = target.split('.')[0]
        packet.writeInt(int(target) if target.isdigit() else this.server.getPlayerCode(Utils.parsePlayerName(target)))
        packet.writeShort(xPosition)
        packet.writeShort(yPosition)
        packet.writeFloat(scaleX)
        packet.writeFloat(scaleY)
        packet.writeFloat(angle)
        packet.writeFloat(alpha)
        packet.writeFloat(AnchorX)
        packet.writeFloat(AnchorY)
        if targetPlayer == "":
            this.room.sendAll(Identifiers.send.Add_Image, packet.toByteArray())
        else:
            player = this.room.clients.get(Utils.parsePlayerName(targetPlayer))
            if player != None:
                player.sendPacket(Identifiers.send.Add_Image, packet.toByteArray())
        return this.room.lastImageID

    def removeImage(this, imageId=0, targetPlayer=""):
        if imageId is None: imageId = 0
        if targetPlayer == "":
            this.room.sendAll(Identifiers.send.Remove_Image, ByteArray().writeInt(imageId).toByteArray())
        else:
            player = this.room.clients.get(Utils.parsePlayerName(targetPlayer))
            if player != None:
                player.sendPacket(Identifiers.send.Remove_Image, ByteArray().writeInt(imageId).toByteArray())

    def playEmote(this, playerName, emoteId, emoteArg = ""):
        if emoteArg is None:
            emoteArg = ""
        player = this.room.clients.get(playerName)
        if player:
            player.sendPlayerEmote(emoteId, emoteArg, False, True)

    def disableChatCommandDisplay(this, command="", hidden=True):
        if not command in this.HiddenCommands and hidden:
            this.HiddenCommands.append(this.FixUnicodeError(command))
        elif command in this.HiddenCommands and not hidden:
            this.HiddenCommands.remove(this.FixUnicodeError(command))

    def tableForeach(this, array, callback):
        for key, value in array.items():
            callback(key, value)

    def disableAfkDeath(this, disable=True):
        this.room.disableAfkKill = disable

    def disableAllShamanSkills(this, disable=True):
        this.room.noShamanSkills = disable

    def disableAutoNewGame(this, disable=True):
        this.room.isFixedMap = disable
        this.roomFix = disable
        
    def disableAutoScore(this, disable=True):
        this.room.noAutoScore = disable

    def disableAutoShaman(this, disable=True):
        this.room.noShaman = disable

    def disableAutoTimeLeft(this, disable=True):
        this.room.never20secTimer = disable

    def addPopup(this, id, type, text, targetPlayer="", x=50, y=50, width=0, fixedPos=False):
        p = ByteArray().writeInt(id).writeByte(type).writeUTF(this.FixUnicodeError(text)).writeShort(x).writeShort(y).writeShort(width).writeBoolean(fixedPos)
        if targetPlayer == "" or not targetPlayer:
            this.room.sendAll(Identifiers.send.Add_Popup, p.toByteArray())
        else:
            player = this.room.clients.get(targetPlayer)
            if player != None:
                player.sendPacket(Identifiers.send.Add_Popup, p.toByteArray())

    def updateTextArea(this, id, text, targetPlayer=""):
        p = ByteArray().writeInt(id).writeUTF(this.FixUnicodeError(text))
        if targetPlayer == "" or not targetPlayer:
            this.room.sendAll(Identifiers.send.Update_Text_Area, p.toByteArray())
        else:
            client = this.room.clients.get(targetPlayer)
            if client != None:
                client.sendPacket(Identifiers.send.Update_Text_Area, p.toByteArray())
    
    def displayParticle(this, particleType=0, xPosition=0, yPosition=0, xSpeed=0, ySpeed=0, xAcceleration=0, yAcceleration=0, targetPlayer=""):
        this.room.displayParticle(particleType, xPosition, yPosition, xSpeed, ySpeed, xAcceleration, yAcceleration, targetPlayer)
    
    def addBonus(this, type=1, x=0, y=0, id=0, angle=0, visible=True, targetPlayer=""):
        p = ByteArray()
        p.writeShort(x)
        p.writeShort(y)
        p.writeByte(type)
        p.writeShort(angle)
        p.writeInt(id)
        p.writeBoolean(visible)
        if targetPlayer == "" or not targetPlayer:
            this.room.sendAll([5, 14], p.toByteArray())
        else:
            player = this.room.clients.get(targetPlayer)
            if player != None:
                player.sendPacket([5, 14], p.toByteArray())
    
    def removeBonus(this, id=0, targetPlayer=""):
        p = ByteArray().writeInt(id)
        if targetPlayer == "" or not targetPlayer:
            this.room.sendAll([5, 15], p.toByteArray())
        else:
            player = this.room.clients.get(targetPlayer)
            if player != None:
                player.sendPacket([5, 15], p.toByteArray())
                
    def removeTextArea(this, id, targetPlayer=""):
        p = ByteArray().writeInt(id)
        if targetPlayer == "" or not targetPlayer:
            this.room.sendAll(Identifiers.send.Remove_Text_Area, p.toByteArray())
        else:
            player = this.room.clients.get(targetPlayer)
            if player != None:
                player.sendPacket(Identifiers.send.Remove_Text_Area, p.toByteArray())

    def addTextArea(this, id, text, targetPlayer="", x=50, y=50, width=0, height=0, backgroundColor=0x324650, borderColor=0, backgroundAlpha=1, fixedPos=False):
        this.roomAreas.append(id)
        if backgroundAlpha:
            backgroundAlpha *= 100
        else:
            backgroundAlpha = 0
        if not targetPlayer:
            targetPlayer = ""
        if x is None:
            x = 50
        if y is None:
            y = 50
        if width is None:
            width = 0
        if height is None:
            height = 0
        if backgroundColor is None:
            backgroundColor = 0x324650
        if borderColor is None:
            borderColor = 0
        if backgroundAlpha is None:
            backgroundAlpha = 0
        if fixedPos is None:
            fixedPos = False

        p = ByteArray().writeInt(int(id))
        p.writeUTF(text)
        p.writeShort(int(x))
        p.writeShort(int(y))
        p.writeShort(int(width))
        p.writeShort(int(height))
        p.writeInt(int(backgroundColor))
        p.writeInt(int(borderColor))
        p.writeByte(int(100 if backgroundAlpha > 100 else backgroundAlpha))
        p.writeBoolean(not fixedPos)
        if targetPlayer == "" or not targetPlayer:
            this.room.sendAll(Identifiers.send.Add_Text_Area, p.toByteArray())
        else:
            player = this.room.clients.get(targetPlayer)
            if player != None:
                player.sendPacket(Identifiers.send.Add_Text_Area, p.toByteArray())

    def setTransformationPlayer(this, target=""):
        playerName = Utils.parsePlayerName(target)
        player = this.room.clients.get(playerName)
        if player != None:
            player.sendPacket(Identifiers.send.Can_Transformation, 1)
            
    def setMapName(this, message=""):
        this.room.sendAll(Identifiers.send.Set_Map_Name, ByteArray().writeUTF(str(message)).toByteArray())
        
    def setShamanName(this, message=""):
        this.room.sendAll(Identifiers.send.Set_Shaman_Name, ByteArray().writeUTF(str(message)).toByteArray())

    def playerVictory(this, target=""):
        playerName = Utils.parsePlayerName(target)
        player = this.room.clients.get(playerName)

        if player != None and not player.isDead:
            if not player.hasCheese:
                this.giveCheese(playerName)

            player.playerWin(1, 0)

    def respawnPlayer(this, target=""):
        playerName = Utils.parsePlayerName(target)
        if playerName in this.room.clients:
            this.room.respawnSpecific(playerName)

    def removeCheese(this, target=""):
        playerName = Utils.parsePlayerName(target)
        player = this.room.clients.get(playerName)
        if player != None and not player.isDead and player.hasCheese:
            player.hasCheese = False
            player.sendRemoveCheese()

    def giveCheese(this, target=""):
        playerName = Utils.parsePlayerName(target)
        player = this.room.clients.get(playerName)
        if player != None and not player.isDead and not player.hasCheese:
            player.sendGiveCheese(0)

    def giveMeep(this, target=""):
        playerName = Utils.parsePlayerName(target)
        player = this.room.clients.get(playerName)
        if player != None and not player.isDead:
            player.sendPacket(Identifiers.send.Can_Meep, 1)

    def killPlayer(this, target=""):
        playerName = Utils.parsePlayerName(target)
        player = this.room.clients.get(playerName)
        if not player.isDead:
            player.isDead = True
            if player.room.noAutoScore:
                player.playerScore += 1
            player.sendPlayerDied()
            player.room.checkChangeMap()

    def setGameTime(this, time=0, add=False):
        if add is None:
            add = False
        if str(time).isdigit():
            if add:
                iTime = this.room.roundTime + (this.room.gameStartTime - Utils.getTime()) + this.room.addTime + int(time)
            else:
                iTime = int(time)
            iTime = 5 if iTime < 5 else (32767 if iTime > 32767 else iTime)
            for player in this.room.clients.values():
                player.sendRoundTime(iTime)

            this.room.roundTime = iTime
            this.room.changeMapTimers(iTime)

    def setShaman(this, target=""):
        player = this.room.clients.get(Utils.parsePlayerName(target))
        if player != None:
            player.isShaman = True
            this.room.sendAll(Identifiers.send.New_Shaman, ByteArray().writeInt(player.playerCode).writeByte(player.shamanType).writeShort(player.shamanLevel).writeShort(player.parseSkill.getShamanBadge()).toByteArray())

    def setCatPlayer(this, target="", yes=True):
        player = this.room.clients.get(Utils.parsePlayerName(target))

        if not player is None:
            this.room.sendAll(Identifiers.send.Gatman_Skill, ByteArray().writeInt(player.playerCode).writeBoolean(True if yes else False).toByteArray())

    def moveCheese(this, x=0, y=0):
        this.room.sendAll(Identifiers.old.send.Move_Cheese, [x, y])

    def addShamanObject(this, type=0, x=0, y=0, angle=0, vx=0, vy=0, ghost=False, options=[]):
        this.LastRoomObjectID += 1
        _id = this.LastRoomObjectID
        this.RoomObjects[_id] = {'id': _id, 'type': type, 'angle': angle, 'ghost': ghost, 'velX': vx, 'velY': vy, 'posX': x, 'posY': y, 'rotationSpeed':(vx+vy)/2, 'stationary': (vx == 0 and vy == 0)}
        this.RefreshTFMGet()
        p = ByteArray()
        p.writeInt(_id)
        p.writeShort(type)
        p.writeShort(x)
        p.writeShort(y)
        p.writeShort(angle)
        p.writeByte(vx)
        p.writeByte(vy)
        p.writeBoolean(not ghost)
        p.writeByte(0)
        this.room.sendAll(Identifiers.send.Spawn_Object, p.toByteArray())

        return _id

    def newGame(this, mapCode=None, mirroredMap=False):
        if isinstance(mapCode, (int, float)):
            if 200 < mapCode:
                if '.0' in str(mapCode): mapCode = str(mapCode).split('.')[0]
                mapCode = "@" + str(mapCode)
        this.room.forceNextMap = mapCode
        this.room.mapInverted = mirroredMap

        this.room.canChangeMap = True
        if this.roomFix:
            this.room.isFixedMap = True
        if this.room.changeMapTimer != None:
            this.room.changeMapTimer.cancel()
        this.room.mapChange()
        if this.roomFix:
            this.room.isFixedMap = True
            

    def sendLuaMessage(this, *args):
        message = ""

        for x in args:
            message += (this.globals.tostring(x) if this.globals.type(x) != "userdata" else "userdata") + ("  " if len(args)>1 else "")

        if message != "" and not this.owner is None:
            this.owner.sendLuaMessage("[<V>%s.lua</V>][<N>%s</N>] %s" % (this.owner.playerName, str(time.strftime("%H:%M:%S")), str(message)))

    def EventLoop(this):
        if not this.runtime is None:
            this.RefreshTFMGet()
            elapsed = (Utils.getTime() - this.room.gameStartTime) * 1000
            remaining = ((this.room.roundTime + this.room.addTime) - (Utils.getTime() - this.room.gameStartTime)) * 1000
            this.emit('Loop', (elapsed if elapsed >= 0 else 0, remaining if remaining >= 0 else 0))

            this.server.addCallLater(0.5, this.EventLoop)

    def emit(this, eventName="", args=()):
        if this.runtime is None:
            return

        this.RefreshTFMGet()
        if eventName == "NewGame":         
            this.RoomObjects = {}

        if type(args) == tuple:
            args_strPack = ""

            for x in args:
                args_strPack += (str(x) if type(x) != str and type(x) != bool else '"%s"' % (x) if type(x) != bool else ("true" if x else "false")) + ","
        else:
            args_strPack = (str(args) if type(args) != str and type(args) != bool else '"%s"' % (args) if type(args) != bool else ("true" if args else "false")) + ","

        try:
            this.runtime.execute("if(event%s)then event%s(%s) end" % (str(eventName), str(eventName), args_strPack[:-1]))
        except Exception as error:
            if not this.owner is None:
                this.owner.sendLuaMessage("[<V>%s.lua</V>][<N>%s</N>]<R>%s</R>" % (this.owner.playerName, str(time.strftime("%H:%M:%S")), str(error)))

    def ModuleStop(this, playerName="", action=0):
        this.room.isMinigame = False
        this.room.minigame = None
        this.runtime = None
        this.running = False
        this.room.blacklistcmd = []
        this.room.startSnow(0, 10, False)

        if this.room.isTribeHouse:
            this.room.countStats = False
            this.room.isTribeHouse = True
            this.room.autoRespawn = True
            this.room.never20secTimer = True
            this.room.noShaman = True
            this.room.disableAfkKill = True
            this.room.isFixedMap = True
            this.room.roundTime = 0

        if this.room.changeMapTimer != None:
            this.room.changeMapTimer.cancel()
        this.room.changeMapTimers(5)
        this.room.canChangeMap = True
        this.room.mapChange()

        if this.LastRoomObjectID > 2000:
            while this.LastRoomObjectID > 2000:
                this.room.removeObject(this.LastRoomObjectID)
                this.LastRoomObjectID -= 1
        
        for i in this.roomAreas:
            this.removeTextArea(i)
        
        for i in this.imagesadd:
            this.removeImage(i)
        
        for _id in this.loops:
            this.loops[_id].cancel()
            
        this.roomAreas = []
        this.imagesadd = []
        this.loops = {}

        if playerName != "" and not this.room.minigame is None:
            if not this.room.minigame.owner is None:
                this.room.minigame.owner.sendLuaMessage("[<V>%s.lua</V>][<N>%s</N>] %s by: <J>%s</J>" % (playerName, str(time.strftime("%H:%M:%S")), "Module stopped" if action == 0 else "Another module was loaded", str(playerName)))

    def RunCode(this, code=""):
        if this.runtime is None:
            this.runtime = LuaRuntime()
            this.SetupRuntimeGlobals()

        try:
            ts = time.time()
            this.runtime.execute(code)
            this.EventLoop()
            te = time.time() - ts

            if not this.owner is None:
                this.owner.sendLuaMessage("[<V>%s.lua</V>][<N>%s</N>] Script loaded in <J>%.2f</J>s." % (this.owner.playerName, str(time.strftime("%H:%M:%S")), te))

            this.script = code
        except Exception as error:
            this.script = ""

            if not this.owner is None:
                this.owner.sendLuaMessage("[<V>%s.lua</V>][<N>%s</N>]<R>%s</R>" % (this.owner.playerName, str(time.strftime("%H:%M:%S")), str(error)))
