import tkFileDialog, random, json

class ProgramState():
    def __init__(self):
        self.game = None
        ##  Fucking write the GameState class goddammit

        self.setupCommands()

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
##self.optionsScreen, self.quitGame, self.mainMenu


"inventory" : (self.game.viewYourInventory, "View your inventory.", [], 0),
"use" : (self.game.useItem, "Use an item in the inventory.",
         self.game.getYourInventory, 1),
"take" : (self.game.takeItem, "Pick up an object in the room.", [], 1)
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
                    
                elif actions[-1][2] = []:
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
        #empty stacks and erroneous actions.

        return actions
                    
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
        if self.commands[verb][3] = 0:
            #   0-class verbs take no objects. If <obj> == False, <command> will
            #treat following objects as new "examine" actions, causing an error
            #if the last action is incomplete.
            
            obj = False
            
        elif self.commands[verb][3] = 1:
            #   1-class verbs always have "default" as their first object. If
            #there are any other objects, "default" is ignored.
            
            obj = ["default"]

        elif self.commands[verb][3] = 2:
            #   2-class verbs must have an explicit, player-specified object.
            #The empty list evaluates False but is not False, which is... a
            #really stupid-seeming way to handle this? I think it works, though,
            #so I'm not touching it. Anyway, this allows a 2-class verb to take
            #objects while noting that, at the time this method is called, there
            #is no explicit object.

            obj = []
            
        return verb, clarifier, obj
