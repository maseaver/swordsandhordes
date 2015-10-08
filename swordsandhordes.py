import tkFileDialog
import random as r
import datetime
import json
import sys
import os

class Destructible(object):
    vul = {"impact"  : 1.0,
           "slash"   : 1.0,
           "pierce"  : 1.0,
           "abrade"  : 1.0,
           "heat"    : 1.0,
           "cold"    : 1.0,
           "acid"    : 1.0,
           "sound"   : 1.0,
           "shock"   : 1.0,
           "poison"  : 1.0,
           "disease" : 1.0,
           "bleed"   : 1.0,
           "asphyx"  : 1.0,
           "heal"    : 1.0,
           "necro"   : 1.0,
           "blast"   : 1.0,
           "smite"   : 1.0,
                       }
    
    buffs = {"impact"  : (1.0, 0),
             "slash"   : (1.0, 0),
             "pierce"  : (1.0, 0),
             "abrade"  : (1.0, 0),
             "heat"    : (1.0, 0),
             "cold"    : (1.0, 0),
             "acid"    : (1.0, 0),
             "sound"   : (1.0, 0),
             "shock"   : (1.0, 0),
             "psychic" : (1.0, 0),
             "poison"  : (1.0, 0),
             "disease" : (1.0, 0),
             "bleed"   : (1.0, 0),
             "asphyx"  : (1.0, 0),
             "heal"    : (1.0, 0),
             "necro"   : (1.0, 0),
             "blast"   : (1.0, 0),
             "smite"   : (1.0, 0),
                       }
    
    minsubhp = 0.0
    
    def __init__(self, parent, id=None, loc=None, maxhp=1.0, hp=1.0,
                 subhp=1.0, tohit=1.0, hitmod = 0, vul={}, buffs={},
                 desc=["perfectly generic object"], mem={"events" : []},
                 end=None, align=0.0, contents=[]):
        self.parent = parent #a GameState object
        self.id = id         #an int, under which this Destructible will be
        #stored in GameState.IDS if all is well
        self.loc = loc
        
        ##    The way I'm gonna handle this right now is that, if loc is a
        ##2-ple, the first item in loc must be a valid id of something that has
        ##a <contents> attribute, and the second item must be 1 unless this
        ##Destructible is also a Repeatable, in which case it can be any
        ##positive int (representing how many of the thing there are in the
        ##person's inventory.)
        
        self.maxhp = maxhp
        self.hp = hp
        self.subhp = subhp
        
        self.tohit = tohit
        self.hitmod = hitmod
        
        self.vul.update(vul)
        self.buffs.update(buffs)
        self.desc = desc
        
        self.mem = mem
        self.end = end
        
        self.align = align
        
        self.contents = contents
        
        self.valid = self.check()
        
        if self.valid:
            self.add()
    
    def check(self):
        ##    Repeatable must override check (and add?) for a lot of reasons.
        good = True
        
        if self.id == None:
            if self.parent.looksLike(self):
                good = False
            else:
                self.id = self.parent.newID()
        ##    GameState.looksLike(Destructible)- returns a Boolean value that
        ##represents something like:
        ##        for value in self.IDS.values():
        ##            if <this Destructible> == value:
        ##                return True
        ##        else:
        ##            return False
        
        ##    GameState.newID(Destructible)- returns an int not currently in
        ##self.parent.IDS.
        
        elif self.id in self.parent.IDS:
            status = self.parent.idCollision(self)
            
            if status:
                if status == -1:
                    good == good and self.reserved()
                if status == 1:
                    good = False
                elif status == 2:
                    self.id == self.parent.newID(self)
        ##    GameState.idCollision(Destructible)- returns an int, where:
        ##        -1: the id is in self.parent.reservedIDs and is therefore
        ##    either the hero or a Repeatable object
        ##        0: the id is in self.parent.IDs, but nothing's stored in it;
        ##        1: the id is in self.parent.IDs, and the thing stored in it
        ##    == self;
        ##        2: the id is in self.parent.IDs, and the thing stored in it
        ##    != self.
        
        ##game!!
        ##    A place where override is necessary!
        if self.loc == None or self.loc not in self.parent.rooms:
            if self.loc and len(self.loc) == 2:
                if self.loc[0] not in self.parent.IDs:
                    good = False
                elif self.loc[1] != 1:
                    good = False
        ##!!
                
            self.loc = self.parent.locateThing(self.id)
        ##    GameState.locateThing(Destructible)- returns a 3-ple of ints that
        ##represents an existing Room in self.parent.rooms. If none of those
        ##list this Destructible's id among their things-they-have-inside-them,
        ##returns the first Room to list 0- the id that represents the game's
        ##hero- among its things-it-has-inside-it. If we get to this branch of
        ##logic but no room lists 0 as being inside it, 0 is put in the Room at
        ##(0, 0, 0) and the method returns (0, 0, 0). If multiple Rooms list
        ##this Destructible's id, and one of them is the Room 0 is in, it
        ##returns that Room's location; if the Room 0 is in doesn't list this
        ##Destructible's id, it returns the first Room found and removes it
        ##from every other Room it searches.
        
        if self.hp <= 0.0:
            self.destroy()
        elif self.subhp <= 0.0:
            self.ko()
        
        if self.subhp > self.hp:
            self.energize()
            self.subhp = self.hp
        elif self.subhp < self.minsubhp:
            self.blackAndBlue()
            self.subhp = self.minsubhp
        
        return good
        
    def dmgCalc(self, kind, value):
        return value * self.vul[kind] * self.buffs[kind][0])
    
    ##game!!
    ##    Anything that calls a Destructible's harm() should also call its
    ##update().
    def harm(self, other=None, damagesig={}):
        #    Inanimate objects can take subdual damage. Yes, I know. Imagine me
        #shrugging.
        
        damage = 0.0
        subdual = 0.0
        
        #    This is a place I should modify self.mem, I think, so that a
        #burnt painting looks different from a slashed up one.
        for k, (v, s) in damagesig.items():
            if s:
                subdual = subdual + self.dmgCalc(k, v)
            else:
                damage = damage + self.dmgCalc(k, v)
        
        subdual = subdual + (damage / 10.0)
        
        newhp = self.hp - damage
        newsubhp = ((self.subhp / self.hp) * newhp) - subdual
        
        self.hp = newhp
        self.subhp = newsubhp
    ##!!
    
    def update(self):
        if self.hp <= 0.0:
            self.destroy()
        elif self.hp > self.maxhp:  #Note that if maxhp is <= 0.0, exceed will
            self.exceed()           #never be called. More feature than bug. I
                                    #don't recommend doing that.

        if self.subhp <= 0.0:
            self.ko()
        
        if self.subhp > self.hp:
            self.subhp = self.hp
        elif self.subhp < self.hp * -1:
            self.subhp = self.hp * -1
    
    def destroy(self):
        self.lastWill()
        self.parent.freeID(self.id, end=self.end)
    
    ##game,external!!
    ##    Override if you want anything to happen when its hp is raised above
    ##its maxhp. For instance, corpses and dead skellies can potentially become
    ##zombies or living (undead, w/e) skeletons.
    def exceed(self):
        self.hp = self.maxhp
    ##!!
    
    ##game,external!!
    ##    Doesn't necessarily need to do anything, even for Fightable objects,
    ##unless it specifically needs to do something weird when it's KO'd.
    def ko(self):
        pass
    ##!!
    
    ##game,external!!
    ##    Override if you want the thing to do something in particular when
    ##it's destroyed. Aside from leave self.end behind, which it'll do
    ##regardless.
    def lastWill(self):
        pass
    ##!!
    
    ##game,external!!
    ##    Override if you want the thing to do something in particular when its
    ##subhp is higher than its hp. Usually, with Fightables(), this will mean
    ##getting back some amount of AP.
    def energize(self):
        pass
    ##!!
    
    ##game,external!!
    ##    Override if you want the thing to do something in particular when
    ##its subhp drops below self.minsubhp. For Fightables, usually that will be
    ##turning some function of the difference between subhp and minsubhp into
    ##normal damage.
    
    ##    Remember that if something calls a Destructible's harm(), it should
    ##also call its update().
    def blackAndBlue(self):
        pass
    ##!!
    
    def add(self):
        self.parent.IDs[self.id] = self
        
        if len(self.loc) == 2:
            try:
                self.parent.IDs[self.loc[0]].give(self.id, self.loc[1])
            except AttributeError:
                pass
        elif len(self.loc) == 3:
            self.parent.rooms[self.loc].things.append(self.id)
    
    def save(self):
        self.update()
        data = self.makeData()
        return json.dumps(data)
    
    ##game,external!!
    ##    Override for any subclass that adds more attributes to be remembered.
    def makeData():
        data = {"id": self.id
                "loc" : self.loc,
                "maxhp" : self.maxhp,
                "hp" : self.hp,
                "subhp" : self.subhp,
                "tohit" : self.tohit,
                "hitmod" : self.hitmod,
                "vul" : self.vul,
                "buffs" : self.buffs,
                "desc" : self.desc,
                "mem" : self.mem,
                "end" : self.end,
                "align" : self.align
                }
        return data
    ##!!

class Sellable(Destructible):
    def __init__(self, parent, id=None, loc=None, maxhp=1.0, hp=1.0,
                 subhp=1.0, tohit=1.0, hitmod = 0, vul={}, buffs={}, align=0.0,
                 desc=["perfectly generic object"], mem={"events" : []},
                 end=None, kind="thing", state="new", sellval=0.0):
        super(Sellable, self).__init__(parent=parent, id=id, loc=loc,
                                       maxhp=maxhp, hp=hp, subhp=subhp,
                                       tohit=tohit, hitmod=hitmod,
                                       vul=vul, buffs=buffs, align=align
                                       desc=desc, mem=mem, end=end)
        
        self.kind = kind
        self.state = state
        self.sellval = sellval
    
    def getPrice(self):
        return self.sellval * (self.hp / self.maxhp)
            
class Fightable(Destructible):
    pass

class Talkable(Fightable):
    pass

class Attack():
    def __init__(self, other, damagesig={}, hitmod=0, dist=r.triangular()):
        self.other = other
        self.damagesig = {}
        self.hitmod = {}
        self.dist = dist
    
    def aim(self):
        modsum = self.other.hitmod + self.hitmod
        success = 0
        
        if modsum <= 0:
            choice = min
        else:
            choice = max
        
        attempts = [self.dist()]
        
        for i in range(abs(modsum)):
            attempts.append(self.dist())
        
        for attempt in attempts:
            if attempt <= self.other.tohit:
                success = success + 1
        
        
class Room():
    pass

class GameState():
    START_HERO = {"race" : "", "gender" : "", "name" : ""}
    FIRST_ROOM = {}
    
    def __init__(self, parent, filename=None):
        self.parent = parent
        self.filename = filename
        
        if self.filename:
            self.load()
        else:
            self.new()
    
    def newThing(self, template):
        if template["type"] == "Destructible":
            
    
    def nameParseable(self, language, moniker):
        for item in moniker:
            if item in language:
                return True
        else:
            return False
    
    def makeName(self, language):
        start = datetime.datetime.now()
        moniker = random.choice(language["word"])
        parseable = True
        
        while self.nameParseable(language, moniker):
            elapsed = datetime.datetime.now() - start
            
            if elapsed.total_seconds() > 10:
                return "timelong"
            
            builder = []
            
            for string in moniker:
                if string in language:
                    builder.extend(random.choice(language[string]))
                else:
                    builder.append(string)
            
            if len(builder) >= 20:
                return "namelong"
            else:
                moniker = builder
        else:
            outputName = "".join(moniker).upper()
            if len(outputName) >= 20:
                return "namelong"
            else:
                return outputName 
                    
    def makeNames(self, race, number):
        language = {
"word" : [["initial"], ["initial", "midword"], ["initial", "final"],
          ["initial", "midword", "final"]],
"initial" : [["onset", "rime"], ["s", "sonset", "rime"], ["rime"]],
"final" : [["sonorant", "e"], ["c"], ["k"], ["p"], ["que"], ["s"], ["t"],
           ["xe"], ["bhe"], ["che"], ["dhe"], ["ghe"], ["jhe"], ["khe"],
           ["phe"], ["qhe"], ["she"], ["the"], ["zhe"]],
"midword" : [["onset", "rime", "midword"], ["onset", "rime"]],
"onset" : [["b"], ["c"], ["d"], ["f"], ["g"], ["h"], ["j"], ["k"], ["l"],
           ["m"], ["n"], ["p"], ["qu"], ["r"], ["s"], ["t"], ["v"], ["w"],
           ["x"], ["y"], ["z"], ["bh"], ["ch"], ["dh"], ["gh"], ["jh"], ["kh"],
           ["ph"], ["qh"], ["sh"], ["th"], ["zh"], ["br"], ["cr"], ["dr"],
           ["fr"], ["gr"], ["jr"], ["kr"], ["pr"], ["qr"], ["shr"], ["tr"],
           ["vr"], ["wr"], ["zhr"], ["bl"], ["cl"], ["dl"], ["fl"], ["gl"],
           ["jl"], ["kl"], ["pl"], ["ql"], ["shl"], ["tl"], ["vl"], ["zhl"],
           ["ng"]],
"rime" : [["vowel"], ["vowel"], ["vowel", "sonorant"]],
"vowel" : [["a"], ["ae"], ["e"], ["i"], ["oe"], ["ue"], ["o"], ["u"]],
"sonorant" : [["r"], ["l"], ["m"], ["n"], ["ng"], ["y"], ["w"], ["h"]],
"sonset" : [["c"], ["f"], ["h"], ["k"], ["l"], ["m"], ["n"], ["p"], ["qu"],
            ["t"], ["v"], ["w"], ["y"], ["z"], ["ph"], ["th"], ["cr"], ["dr"],
            ["fr"], ["kr"], ["pr"], ["tr"], ["vr"], ["cl"], ["fl"], ["kl"],
            ["pl"], ["ql"], ["tl"], ["vl"], ["ng"]],
}
        monikers = []
        key = "%s.lang" % race
        lang, exists, control = self.config[key]
        
        if exists and control == 0:
            temp = {}
            
            try:
                with(lang, "r") as f:
                    temp = json.load(f)
            except IOError:
                exists = False
                control = 0
                
                error = """\
The file "%s" doesn't exist or can't be opened.
"%s" is the filename specified for naming %s characters.
If you don't know what to do about that, ask someone who does, like me \
(Madison (the writer of Swords and Hordes)), or just deal with every %s \
character having the default style of names.
self.config[%s] = %s, %s, %s""" % (lang, lang, race, race,
                                   key, lang, exists, control)
    
                self.parent.message(error)
                
                self.config[key] = lang, exists, control
                
            except ValueError:
                exists = False
                control = 1
                
                error = """\
The file "%s" exists but isn't a legal JSON document.
"%s" is the filename specified for naming %s characters.
If you don't know what to do about that, ask someone who does, like me \
(Madison (the writer of Swords and Hordes)), or just deal with every %s \
character having the default style of names.
self.config[%s] = %s, %s, %s""" % (lang, lang, race, race,
                                   key, lang, exists, control)
                self.parent.message(error)
            else:
                try:
                    foo = self.makeName(temp)
                except KeyError:
                    exists = False
                    control = 2
                    
                    error = """\
The file "%s" is a legal JSON document that doesn't do what it should. \
Something is wrong with it- it probably doesn't have a "word" entry.
"%s" is the filename specified for naming %s characters.
If you don't know what to do about that, ask someone who does, like me \
(Madison (the writer of Swords and Hordes)), or just deal with every %s \
character having the default style of names.
self.config[%s] = %s, %s, %s""" % (lang, lang, race, race,
                                   key, lang, exists, control)
                    self.config[key] = lang, exists, control
                else:
                    exists = True
                    control = 1
                    
                    monikers.append(foo)
                    language = temp
                    
                    self.config[key] = lang, exists, control
                    
        elif exists and control == 1:
            with open(lang, "r") as f:
                language = json.load(f)
        
        duration = False
        length = False
        
        while len(monikers) < number:
            foo = self.makeName(language)
            
            if foo == "timelong":
                if duration:
                    error = """\
It's taking too long to come up with names for an %s.
If you don't know what to do about that, ask someone who does, like me \
(Madison (the writer of Swords and Hordes)). In the meantime, I'm going to \
close the program- sorry.
language = %s
self.config[%s] = %s, %s, %s""" % (race, json.dumps(language), key, lang,
                                   exists, control)
                    self.parent.message(error)
                    sys.exit("""Seriously, tell me if this happens. \
maseaver@gmail.com""")
                else:
                    duration = True
            elif foo == "namelong":
                if length:
                    error = """\
The language being used makes names that are too long.
If you don't know what to do about that, ask someone who does, like me \
(Madison (the writer of Swords and Hordes)). In the meantime, I'm going to \
close the program- sorry.
language = %s
config[%s] = %s, %s, %s""" % (json.dumps(language), key, lang,
                              exists, control)
                    self.parent.message(error)
                    sys.exit("""Seriously, tell me if this happens. \
maseaver@gmail.com""")
            else:
                monikers.append(foo)
        
        return monikers
    
    def getConfigNew(self):
        #self.config = self.parent.getGameConfig()
        razzamatazz = {"races" : ["orc", "ratfolk", "skeleton", "human"],
                       "genders" : ["puce", "sienna", "periwinkle",
                                    "chartreuse"],}
        for race in razzamatazz["races"]:
            razzamatazz["%s.lang" % race] = "", False, 0
        return razzamatazz
    
    def getConfig(self, config):
        self.config = config
    
    def heroSetupNew(self):
        tempHero = GameState.START_HERO
        
        attempts = 0
        while not tempHero["race"]:
            prompt = ""
            
            if attempts == 0:
                prompt = """\
Welcome to the Hellcave, adventurer. What is your race?"""
            else:
                prompt = """\
Didn't understand that, mate. Really, what's your race?"""
                
            options = self.config["races"]
            
            tempHero["race"] = self.parent.select(prompt, options)
            attempts = attempts + 1
        
        attempts = 0
        while not tempHero["gender"]:
            prompt = ""
            
            if attempts == 0:
                foo = tempHero["race"]
                prompt = """\
Of course, and a fine specimen of %s you are. What is your gender?""" % foo
            else:
                bar = len(self.config["genders"])
                prompt = """\
Come on now, there's only %d, you've got to be one... so which?""" % bar
            options = self.config["genders"]
            
            tempHero["gender"] = self.parent.select(prompt, options)
            
            attempts = attempts + 1
        
        attempts = 0
        while tempHero["name"] in ["", "none of these"]:
            prompt = ""
            
            if attempts == 0:
                foo = tempHero["gender"], tempHero["race"]
                prompt = """\
And may I ask, mighty %s %s warrior, what is your honorable name?""" % foo
            else:
                prompt = """\
None of those? Well then, surely one of these is it?"""
            
            options = self.makeNames(tempHero["race"], 5)
            options.append("none of these")
            
            tempHero["name"] = self.parent.select(prompt, options)
        
        prompt = """\
You are a %s %s named %s.
Is that alright?""" % (tempHero["gender"], tempHero["race"],
                       tempHero["name"])
        options = ["Yes", "No"]
        
        if self.parent.select(prompt, options) == "" or "Yes":
            congratulations = """\
Alright! Your hero is %s the %s %s! When the game's actually up and running, \
there'll be something to do after this... lmao. Until then!""" % (
tempHero["name"], tempHero["gender"], tempHero["race"])
            self.parent.message(congratulations)
            you, value = self.heroSetup(tempHero)
            return you, value
            
        else:
            return {}, True
            
    def heroSetup(self, hero):
        return hero, False
    
    def roomSetupNew(self, coordinates):
        pass
    
    def roomSetup(self, coordinates, room):
        pass
    
    def new(self):
        self.config = self.getConfigNew()
        
        heroNeeded = True
        while heroNeeded:
            self.hero, heroNeeded = self.heroSetupNew()
        self.rooms = {(0, 0, 0): GameState.FIRST_ROOM}
        ##    GameState.getConfig(), GameState.heroSetup(),
        ##GameState.FIRST_ROOM
        
    def load(self):
        savefile = {}
        
        with open(self.filename, "r") as f:
            savefile = json.load(f)
        
        self.config = getConfig(savefile["config"])
        self.hero = self.heroSetup(savefile["hero"])
        self.rooms = {}
        
        for coordinates in savefile["rooms"]:
            savefile["rooms"][coordinates] = room
            self.rooms[coordinates] = self.roomSetup(coordinates, room)
        ##    GameState.heroSetup(hero), GameState.roomSetup(room)
