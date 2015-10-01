import tkFileDialog
import random, datetime
import json, sys, os

class Thing():
    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.kwargs = kwargs
        
        if "kind" in self.kwargs:
            self.kind = self.findKind(self.kwargs["kind"])
        else:
            self.kind = self.findKind("thing")
            
        if "state" in self.kwargs and self.kwargs["state"] == "random":
            self.makeRandom()
        elif "state" in self.kwargs and self.kwargs["state"] == "exact":
            self.makeExact()
        else:
            self.makeNew()
    
    def findKind(self, searchString):
        pass
    ##    Thing.findKind(searchString)
    
    def makeRandom(self):
        pass
    
    ##    Thing.makeRandom()
    
    def makeExact(self):
        pass
    
    ##    Thing.makeExact()
    
    def makeNew(self):
        pass
    
    ##    Thing.makeNew()
            
class Combatant():
    pass

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
        
class ProgramState():
    def __init__(self):
        self.message("""\
S W O R D S + A N D + H O R D E S

""")
        self.game = None

        self.setupCommands()

    def message(self, string):
        middle = ""
        
        for line in string.splitlines():
            if not line:
                print("")
            else:
                middle = "   "
                
                for character in line:
                    middle = middle + character
                
                while len(middle) >= 80:
                    if " " in middle:
                        lineend = middle.rfind(" ", 0, 80)
                        print(middle[:lineend])
                        middle = middle[lineend + 1:]
                else:
                    print(middle)
    
    def checkFiles(self):

    def setupCommands(self):
        """Create the command lexicon.

        The form of an entry in self.commands is as follows:
            * The key is a string the user may enter as a "verb".
            * The value is a 4-ple.
            * value[0] is a function, the one eventually called when the key is
        entered as a command.
            * value[1] is a description of what the command does, for menus and
        the like.
            * value[2] is a list of clarifiers the verb takes. A clarifier is a
        string without which the verb cannot be interpreted. In essence, a verb
        that requires a clarifier is a blanket identifier for a whole class of
        verbs, and the clarifier tells you which verb is meant. The archetypal
        clarifier verbs are ones that involve an item in the player's inventory-
        "use", "drop", etc. Most of the time, value[2] will be an empty list or
        a method on the GameState that returns a list of valid clarifiers.
            * value[3] is an integer 0, 1, or 2, indicating the verb's behavior
        with respect to objects. 0 indicates that the verb takes no objects, 1
        indicates that the verb takes an object but has a default object if
        no explicit object is given, and 2 indicates that the verb requires an
        explicit object- there is no reasonable way to deduce which object was
        intended if the player did not supply one. The GameState keeps track of
        what objects can be acted on, and this list consists of the player
        character, every non-player character in the current room, and every
        inanimate object in the current room that is not in the player's
        inventory. So, for instance, "save"- like most of the commands that do
        not advance the GameState's clock- is 0, but so is "wait"- which
        advances the GameState's clock but does nothing else. "attack" is 1,
        because its function has a default behavior if no object is specified
        (that is, if the room is empty except for the player character, it
        describes the player attacking empty air; if there are non-PC objects in
        the room, it preferentially attacks hostile NPCs, then non-hostile NPCs,
        then inanimate objects, always picking the first in the list), but an
        explicit object can be given (the player can pick one of the objects in
        the room to attack, including the player character themself if desired).
        At the moment, I can't think of any commands that I intend to implement
        that act on one of the objects in the room but which has no reasonable
        default behavior, but I wanted to build it in just in case.

        -----

        self.modifiers is a list of "adverbs" that can affect how the verb is
        executed, but are never required. What a modifier "means" for a given
        verb is idiosyncratic, but- if I've done my job correctly- intuitive.

        """
        
        self.commands = {
"new" : (self.newGame, "Start new game.", [], 0),
"resume" : (self.resumeGame, "Resume active game.", [], 0),
"load" : (self.loadGame, "Load existing gamefile.", [], 0),
"save" : (self.saveGame, "Save active game.", [], 0),
"help" : (self.helpScreen, "View help screen.", [], 0),
"options" : (self.optionsScreen, "View options screen.", [], 0),
"quit" : (self.quitGame, "Quit game.", [], 0),
"menu" : (self.mainMenu, "Go to main menu.", [], 0),
##  self.newGame, self.resumeGame, self.loadGame, self.helpScreen,
##self.saveGame, self.optionsScreen, self.quitGame, self.mainMenu


"inventory" : (self.game.viewYourInventory, "View your inventory.", [], 0),
"use" : (self.game.useItem, "Use an item in the inventory.",
         self.game.getYourInventory, 1),
"take" : (self.game.takeItem, "Pick up an object in the room.", [], 1),
"drop" : (self.game.dropItem, "Drop an item from the inventory.",
          self.game.getYourInventory, 0),
"throw" : (self.game.throwItem, """Throw something in your inventory at some\
thing in the room.""", self.game.getYourInventory, 2),
"toss" : (self.game.tossItem, """Toss something in your inventory to someone in\
the room.""", self.game.getYourInventory, 2),
##  self.game.viewYourInventory, self.game.useItem,
##self.game.getYourInventory, self.game.takeItem, self.game.dropItem,
##self.game.throwItem, self.game.tossItem

"shop" : (self.game.viewShop, "View what's available for purchase.",
          [], 0),
"buy" : (self.game.buyItem, "Purchase something.",
         self.game.getShopInventory, 1),
"sell" : (self.game.sellItem, "Sell something from your inventory.",
          self.game.getYourInventory, 0),
##  self.game.viewShop, self.game.buyItem, self.game.getShopInventory,
##self.game.sellItem

"level" : (self.game.viewGains, "View techniques and attributes you can learn.",
           [], 0),
"learn" : (self.game.learnGain, "Learn a technique or attribute.",
           self.game.getNewGains, 0),
"forget" : (self.game.forgetGain, "Forget a technique or attribute.",
            self.game.getYourGains, 0),
##  self.game.viewGains, self.game.learnGain, self.game.getNewGains,
##self.game.forgetGain, self.game.getYourGains

"wait" : (self.game.wait, "Do nothing.", [], 0),
"attack" : (self.game.attack, "Attack with your main weapon.", [], 1),
"tech" : (self.game.useTech, "Use a technique.",
          self.game.getTechniques, 1),
##  self.game.wait, self.game.attack, self.game.useTech,
##self.game.getTechniques
                         }

        self.modifiers = ["carefully",      #slower but better
                          "quickly",        #faster but worse
                          ]
        
    def command(self):
        """Return a stack of verb phrases.

        Honestly this is a bear of a method. It takes an arbitrary input string
        and grinds out a stack of verb phrases, ignoring anything that doesn't
        fit into its framework.
        """
        ##  Write a better docstring for command()
        
        rawCommand = raw_input("\n> ")
        #   Grab the user's input.

        command = rawCommand.split()
        #   Split it by whitespace.
        
        actions = []
        mods = []
        modifier = ""
        #   <actions> takes 3-ples as its elements.
        #   * action[0] is a string, the verb of the "verb phrase."
        #   * action[1] is a string representing the verb clarifier, the value
        #       True if the verb requires no clarifier, or the value False if
        #       the verb requires a clarifier that it doesn't have yet.
        #       (If an action closes out without a required clarifier, action[1]
        #       is set to the string "error" as the next action is opened.)
        #   * action[2] is either the value False, denoting that the verb phrase
        #       needs no object, or a list containing only strings, minimally
        #       empty, denoting the objects the player is indicating for the
        #       verb phrase.
        #       (If an action closes out with an empty list of objects, not even
        #       containing the string "default", "error" is appended to
        #       action[2] as the next action is opened.)

        #   <mods> takes strings as its elements. <mods> is appended to if and
        #only if <actions> is appended to, and the appended value is always
        #<modifier>. Because of the logic of the loop that follows, except for
        #the special case that <modifier> is non-empty when the loop exits while
        #the last item in <mods> is "", the index of a string in <mods> is always
        #equal to the index of the first tuple in <actions> created after the
        #modifier was entered.

        #   <modifier> is always one of the strings in <self.modifiers that the
        #player has entered or "" if no modifier has been entered or if a once-
        #floating modifier has been attached to an action.
        
        for word in command:
            #   Iterates through the command's words, stripping out non-
            #alphanumeric characters from the word.
            
            edit = ""
            
            for character in word[:]:
                if character.isalnum():
                    edit = edit + character

            word = edit
            
            if word in self.modifiers:
                #   Adverbs frequently come before verbs in English, so as a bit
                #of syntactic sugar, we'll hold on to one modifier at a time and
                #append whatever the "current" modifier is to <mods> every time
                #we create an action, then clear <modifier> to "". Later, we'll
                #<zip> them together.
                                    
                modifier = word
                
            elif not actions:
                #   If we don't have any actions yet, and this word wasn't a
                #modifier, this executes. We're on the hunt for a verb.
                
                if self.game.isObject(word):
                    #   If there aren't any actions, but this word is a valid
                    #object, it's assumed the player intends to examine the
                    #object.
                    
                    action = self.verbStructure("examine")
                    action[2].append(word)
                    actions.append(action)
                    
                    mods.append(modifier)
                    modifier = ""
                    
                elif word in self.commands.keys():
                    #   If, however, the word is a valid command, a new action
                    #is created with this word as the verb, and the action is
                    #appended to <actions>.
                    
                    action = self.verbStructure(word)
                    actions.append(action)
                    
                    mods.append(modifier)
                    modifier = ""
                    
            elif actions[-1][1]:
                #   The conditions above ensure that there is an action. If that
                #action's second value evaluates to True- that is, either
                #<verbStructure> returned True or the value is a non-empty
                #string- the code does not look for any more clarifiers.
                
                if actions[-1][2] == False:
                    #   <actions[-1][2]> can be either False, an empty list, or
                    #a non-empty list. If it's False, there can be no object,
                    #and following objects must be interpreted as forming their
                    #own verb phrases ("examine" phrases, to be precise.)
                    
                    #   Note that the elif clause in which this if clause is
                    #contained ensures that the clarifier, if necessary, has
                    #been found, while this if clause ensures that no object is
                    #necessary. Therefore, the action we're operating on must be
                    #a valid action; we need not check further when appending
                    #new actions.
                    
                    if self.game.isObject(word):
                        #   The next word is a valid object, but there's no
                        #action to tack it onto, so we assume the player wants
                        #to examine the object.
                        
                        action = self.verbStructure("examine")
                        action[2].append(word)
                        actions.append(action)
                        
                        mods.append(modifier)
                        modifier = ""
                            
                    elif word in self.commands.keys():
                        #   The next word is a valid verb, and we know the
                        #action we were working on is valid, so we start a new
                        #action.
                        
                        action = self.verbStructure(word)
                        actions.append(action)
                        
                        mods.append(modifier)
                        modifier = ""
                            
                elif self.game.isObject(word):
                    #   <actions[-1][2]> can be either False, an empty list, or
                    #a non-empty list. It didn't equal False, so here we are. If
                    #it isn't False, the word permits objects. And lo! the word
                    #is an object! Tack it onto the list of objects the current
                    #actions is collecting.
                    
                    actions[-1][2].append(word)
                    
                elif actions[-1][2] == []:
                    #   The current action needs an object, but this word isn't
                    #one- see the elif clause immediately preceding. That's OK,
                    #as long as this word isn't a verb- we can just ignore it,
                    #and hope the next word is something we need.
                    
                    if word in self.commands.keys():
                        #   Uh-oh. Someone started a new action without giving
                        #an object for the last one. Well, we'll chain it on,
                        #and later we'll ask the user for clarification. To make
                        #sure the clarification bit happens, we append "error"
                        #to the object list before starting the new action.

                        actions[-1][2].append("error")
                        action = self.verbStructure(word)
                        actions.append(action)
                        
                        mods.append(modifier)
                        modifier = ""
                
            elif word in self.commands[actions[-1][0]][2]:
                #   Recall that in the last elif clause at this depth, we
                #checked if the clarifier position was necessary, and, if so,
                #filled. If it's necessary but not filled, we're looking for a
                #clarifier. If this elif evalueates True- if the word is in the
                #action's verb's list of possible clarifiers- then great! We'll
                #just make this the clarifier for the action.
                
                actions[-1] = actions[-1][0], word, actions[-1][2]
                
            elif actions[-1][2] != False:
                #   Well, the clarifier position is necessary and unfilled, but
                #according to the last elif block, this word is not a clarifier.
                #We'll keep looking, but in the meantime, if this action can
                #take an object, we're also looking for an object.
                
                if self.game.isObject(word):
                    #   Lo and behold, this word's an object! Tack it on and
                    #move on.
                    
                    actions[-1][2].append(word)
                    
                elif word in self.commands.keys():
                    #   Uh-oh. We're missing a clarifier, but the command has
                    #moved on to the next action- which is to say, this word's a
                    #verb. We'll mark this verb as having an error in its
                    #clarifier slot and check if we also need to mark the object
                    #slot as being in error.
                    
                    actions[-1] = actions[-1][0], "error", actions[-1][2]

                    if not actions[-1][2]:
                        #   Notice that above we ensured that <actions[-1][2]>
                        #doesn't literally equal False. If it does evaluate to
                        #False, then, it must be an empty list. If it's an empty
                        #list, then it needs an object it doesn't have. Append
                        #"error" and move on.

                        actions[-1][2].append("error")
                
            elif self.game.isObject(word):
                #   Holy shit, where are we. We've established that either there
                #is a modifier or this word is not a modifier. Check. We've also
                #established that there is at least one action. Check. That
                #action needs a clarifier, and this word is not it. Check.
                #According to the last block, this action cannot take an object.
                #Check. So what we need to do is check if this word starts a new
                #action, and, if so, mark the action as having a problem with
                #its clarifier.
                
                #   We'll start with the case that the next action is a verbless
                #object. If so, mark the old action as having an error in its
                #clarifier and make a new "examine" action.

                actions[-1] = actions[-1][0], "error", actions[-1][2]
                action = self.verbStructure("examine")
                action[2].append(word)
                actions.append(action)
                
                mods.append(modifier)
                modifier = ""

            elif word in self.commands.keys():
                #   I think this is the last case? Invalid clarifier,
                #intransitive verb, and this word is a new verb. Mark the
                #clarifier as being in error and start a new action with this
                #verb.

                actions[-1] = actions[-1][0], "error", actions[-1][2]
                action = self.verbStructure(word)
                actions.append(action)
                
                mods.append(modifier)
                modifier = ""

        if not actions[-1][1]:
            #   We've exited the for loop, but what if the very last action is
            #incomplete? We have to mark it as being in error. This if deals
            #with the clarifier, if needed and absent.

            actions[-1] = actions[-1][0], "error", actions[-1][2]

        if not actions[-1][2]:
            #   And this if deals with the object, if needed and absent.

            actions[-1][2].append("error")

        if modifier and not mods[-1]:
            #   What if we end the parsing process with <modifier> non-empty?
            #Clearly the player intended to apply it to an action, and if the
            #last action lacks one, it's pretty simple to deduce what the player
            #intended. I flatly refuse to handle any case of syntactic ambiguity
            #less tractable than this. It's a parser, not an AI, thanks, and if
            #I understood Tkinter better I wouldn't have written this at all.

            mods[-1] = modifier

        #   We have <actions> and <mods>, but wouldn't it be pleasant if we had
        #one list? So, we zip the two together. Note that the form of an item in
        #<actions> after this line is ((verb, clarifier, objects), modifier).

        actions = zip(actions, mods)

        #   We assume that the player has entered the actions they want to take
        #queue-wise, with the first action first, etc.. I want to use the list
        #output as a stack later, because it'll be really fast that way, so I'll
        #reverse <actions> in place.

        actions.reverse()

        #   Whoa, Madison! you say. This list of actions still has hella errors
        #in it! Well, yeah, but it gives more power to the player if I let them
        #edit/decline/etc. the commands they gave as they come up. Plus, like...
        #if I was a newbie player floundering with the command syntax, and I
        #accidentally indicated a long queue of erroneous actions, and the game
        #made me stop and clarify what I meant for every single one all in a
        #row, I'd probably just stop playing. It's much kinder to allow bad
        #input and correct it in small bites just as soon as it becomes
        #necessary, you feel me?
        
        #   Also, <actions> can be empty at this point, so I sure had better
        #write the code that this returns to in such a way that that's not a
        #problem.

        ## Write the code handling the action stack and what to do with
        ##empty stacks and erroneous actions.
        
        return actions
        
        #    As always, I'm assuming the user can only enter text via
        #keysmashing, and so the parser is built to be maximally permissive of
        #noise in the signal, perhaps to the point of extracting meaningful
        #input from chaos. I can only hope that, if someone for whom typing is
        #difficult for whatever reason pays me the tremendous compliment of
        #playing Swords and Hordes, these parsers are sufficiently generous to
        #make their playing experience worthwhile.
                
        #    Although, honestly, the logic in <command> is not safe for that
        #kind of input problem... but I have no idea how to write a parser
        #whose output satisfies the
        #    (adverb) verb/verb + clarifier (object possibly mandatory)
        #syntax but whose input processing is involved enough to handle typo-
        #rich input. This is the kind of problem that outside accessibility
        #accessories were designed for.
                
        ##program    Maybe I should write a <slowcommand> method that can be
        ##set as the preferred input handler and only parses one "word" at a
        ##time, but is extremely permissive of typos...? That'd cut the
        ##complexity down a lot, but it'd still be a pretty big job to tackle.
                    
    def verbStructure(self, verb):
        ##  Write a docstring for <verbStructure>, probably just one line.
        clarifier = 0
        if self.commands[verb][2]:
            #   If the third value of the verb's listing in self.commands, which
            #is the list of clarifiers the verb takes, contains anything, we
            #note that the verb requires a clarifier that has not been found.
            
            clarifier = False
        else:
            #   If, on the other hand, the verb requires no clarifier, we tell
            #command that the clarifier has been found- it's just nil.
            
            clarifier = True

        obj = 0
        if self.commands[verb][3] == 0:
            #   0-class verbs take no objects. If <obj> == False, <command> will
            #treat following objects as new "examine" actions, causing an error
            #if the last action is incomplete.
            
            obj = False
            
        elif self.commands[verb][3] == 1:
            #   1-class verbs always have "default" as their first object. If
            #there are any other objects, "default" is ignored.
            
            obj = ["default"]

        elif self.commands[verb][3] == 2:
            #   2-class verbs must have an explicit, player-specified object.
            #The empty list evaluates False but is not False, which is... a
            #really stupid-seeming way to handle this? I think it works, though,
            #so I'm not touching it. Anyway, this allows a 2-class verb to take
            #objects while noting that, at the time this method is called, there
            #is no explicit object.

            obj = []
            
        return verb, clarifier, obj
    
    def select(self, prompt, options):
        patternMatcher = {}
        
        self.message(prompt)
        
        for i, option in enumerate(options):
            patternMatcher[str(i)] = option
            patternMatcher[str(option)] = option
            #    All hell will break loose if str(option) is ever in [str(x)
            #for x in range(len(options))]. Don't do that. (I guess it's fine
            #in the degenerate case that str(i) == str(option) for option in
            #options.)
            
            self.message("%8d: %s" % (i, option))
                
        patterns = patternMatcher.keys()
        
        rawSelection = raw_input("\n> ")
        processing = rawSelection.lstrip()
        
        if processing:
            findings = []
            for pattern in patterns:
                if pattern in processing:
                    findings.append((processing.index(pattern), pattern))
            
            if findings:
                results = []
                first = len(processing)
                
                #    Okay, so the idea here is that every element of findings
                #is a 2-ple whose second element is a string representing one
                #of the options between which the user is selecting and whose
                #first element is the index of the first occurrence of that
                #string.
                
                #    But we don't want all of them, we just want the earliest-
                #occurring option string and, in the case of a tie, the longest
                #of them. (Why do we care how long it is? If the user is given
                #a list of eleven options, and the user enters "10", they will
                #be confused and irritated if <select> chooses "1" over the
                #longer "10".
                
                #    As always, I'm assuming the user can only enter text via
                #keysmashing, and so the parser is built to be maximally
                #permissive of noise in the signal, perhaps to the point of
                #extracting meaningful input from chaos. I can only hope that,
                #if someone for whom typing is difficult for whatever reason
                #pays me the tremendous compliment of playing Swords and
                #Hordes, these parsers are sufficiently generous to make their
                #playing experience worthwhile.
                
                #    Although, honestly, the logic in <command> is not safe for
                # that kind of input problem... but I have no idea how to write
                #a parser whose output satisfies the
                #    (adverb) verb/verb + clarifier (object possibly mandatory)
                #syntax but whose input processing is involved enough to handle
                #typo-rich input. This is the kind of problem that outside
                #accessibility accessories were designed for.
                
                ##program    Maybe I should write a <slowcommand> method that
                ##can be set as the preferred input handler and only parses one
                ##"word" at a time, but is extremely permissive of typos...?
                ##That'd cut the complexity down a lot, but it'd still be a
                ##pretty big job to tackle.
                
                for finding in findings:
                    if finding[0] < first:
                        first = finding[0]
                        results = [patternMatcher[finding[1]]]
                    elif finding[0] == first:
                        results.append(patternMatcher[finding[1]])
                
                results.sort(key=len)
                
                print("")
                
                return results.pop()
        else:
            print("")
            
            return ""

if __name__ == "__main__":
    program = ProgramState()