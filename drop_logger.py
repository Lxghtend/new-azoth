class DropTypeError(NameError):
    """An unknown drop type was passed through"""
    def __init__(self, drop_type: str):
        super().__init__(f"{drop_type.upper()} is an invalid drop_type.")
        


class DropLogger():
    def __init__(self, client):
        self.client = client
        self.flag = False
        self.max_level = False

    def format(self, drops:list) -> dict:

        """Converts drops list into a dictionary"""
        
        drops = {i:drops.count(i) for i in drops}
        return drops
        """
        To print the drops in a farming instance use the following template
        for key, value in reagents.items():
            print(f"({p.title}): {key} x {value}")
            """
    
    def filter(self, dropType:str) -> str:
        dropType = dropType.lower()
        
        hats = ["hat", "hats", "helmet", "helmets"]
        robe = ["robe", "robes", "body"]
        shoes = ["shoes", "shoe", "boots", "boot"]
        reagents = ["reagent", "reagents"]
        housing = ["housing"]
        seed = ["seed", "seeds"]
        petsnack = ["petsnack", "petsnacks"]
        items = [hats, robe, shoes, reagents, housing, seed, petsnack]
        for i, x in enumerate(items):
            if dropType in items[i]:
                return items[i][0]
        return dropType
        
    def cut_text(self, string:str, pos=None) -> str:

        if pos == "start":
            startString = string.find("received ")
            endString = string.find(" experience!")
            cutString = int(string[startString+8:endString])
            return cutString
        
        elif pos == "end":
            startString = string.find("earned ")
            endString = string.find(" gold!")
            cutString = int(string[startString+7:endString])
            return cutString
        
        # for tc
        if "00FF00" in string and "You received:" in string:
            start = string.find("You received:") + len("You received: ")
            end = string.find("</color>")
            name = string[start:end].strip()
            return [name, "TreasureCard"]
        
        startString = string.find("image", string.find("image") + 1)
        midString = string.find(">", string.find(">", string.find(">") + 1) + 1)
        endString = string.find("</color>")

        dropType = string[startString+6:midString]
        
        cutString = string[midString+2:endString]
        return [cutString, dropType]

    async def get_window_from_path(self, root_window, name_path):
        async def _recurse_follow_path(window, path):
            if len(path) == 0:
                return window

            for child in await window.children():
                if await child.name() == path[0]:
                    found_window = await _recurse_follow_path(child, path[1:])
                    if not found_window is False:
                        return found_window

            return False

        return await _recurse_follow_path(root_window, name_path)


    async def get_chat(self):
        try:
            text, *_ = await self.client.root_window.get_windows_with_name("chatLog")
            text = await text.maybe_text()
            textList = text.splitlines()
            return textList
        except ValueError:
            self.flag = True
    
    async def get_last_battle(self, textList):
        start = None
        end = None
        drops = []
        dropsType = []
        #print(textList)
        while (xpBar := await self.get_window_from_path(
                self.client.root_window,
                ["WorldView","windowHUD", "XPBar"]
                )) == False:
            continue

        self.max_level = not await xpBar.is_visible()


        if not self.max_level:
            for i, string in enumerate(reversed(textList)):
                if "System.dds" not in string:
                    continue
                if "AA00AA" in string and start == None:
                    start = "start"
                    string = self.cut_text(string, start)
                    drops.append(string)
                    continue

                elif "AA00AA" in string and start != None:
                    break
                
                elif "00FF00" in string and "!</color>" in string and end == None and start != None:
                    end = "end"
                    string = self.cut_text(string, end)
                    drops.append(string)
                    break

                string = self.cut_text(string)
                
                if len(string[0]) != 0:
                    drops.append(string[0])
                    dropsType.append(string[1])
        else:
            #drops.append(0)  #why the HELL is this even here bruh 
            for i, string in enumerate(reversed(textList)):
                if "System.dds" not in string:
                    continue
                if "00FF00" in string and "!</color>" in string and end == None:
                    end = "end"
                    string = self.cut_text(string, end)
                    drops.append(string)
                    continue

                
                string = self.cut_text(string)
                
                if len(string[0]) != 0:
                    drops.append(string[0])
                    dropsType.append(string[1])

                
        dropsType.reverse()
        drops.reverse()
        return [drops, dropsType]

    def flag_check(self):
        if self.flag:
            return "Could not retrieve chat!"
        return False
    
################################################
    
    async def get_xp(self) -> int:
        """Returns the xp from latest battle"""
        
        chat = await self.get_chat()
        if (flag := self.flag_check()):
            return flag
        
        try:    
            drops = await self.get_last_battle(chat)
            if self.max_level:
                return "You cannot get any XP you are max level!"
            if isinstance(drops[0][-1], int):
                return drops[0][-1]
            raise IndexError
        except IndexError:
            return "Could not retrieve latest battle's XP!"

    
    async def get_gold(self) -> int:
        """Returns the gold from latest battle"""
        
        chat = await self.get_chat()
        if (flag := self.flag_check()):
            return flag
        try:
            drops = await self.get_last_battle(chat)
            if len(drops[0]) < 2:
                return "No gold was dropped."
            elif isinstance(drops[0][0], int):
                return drops[0][0]
            else:
                raise IndexError
        except IndexError:
            return "Could not retrieve latest battle's gold!"

    
    async def get_drops(self) -> list:
        """Returns all drops from latest battle"""
        
        chat = await self.get_chat()
        drops = await self.get_last_battle(chat)
        return drops[0]


    async def get_drops_type(self) -> list:
        """Returns all drops types from latest battle"""
        
        chat = await self.get_chat()
        if (flag := self.flag_check()):
            return flag
        
        drops = await self.get_last_battle(chat)
        return drops[1]


    async def get_drop_by_type(self, dropType:str) -> list:
        """Returns a list of specific type of drop from latest battle"""
        """ TODO: get_drop_by_types """
    
        dropType = self.filter(dropType)
        itemTypes = [
            "Hat",
            "Robe",
            "Shoes",
            "Wand",
            "Athame",
            "Amulet",
            "Ring",
            "Pet",
            "Deck",
            "Reagent",
            "PetSnack",
            "Housing",
            "Seed",
            "TreasureCard"
            ]
        dropType = dropType.capitalize()
        if dropType == "Petsnack":
            dropType = "PetSnack"
        try:
            if dropType not in itemTypes:
                raise DropTypeError(dropType)
        except ValueError:
            raise DropTypeError(dropType)
        

        drop_by_type = []

        chat = await self.get_chat()
        drops = await self.get_last_battle(chat)
        dropType = dropType.lower()
        
        for i, x in enumerate(drops[1]):
            x = x.lower()
            if dropType == x:
                drop_by_type.append(drops[0][i+1])
        return drop_by_type


    def drops_by_name(self, drops, items:(str,list), funcType):
        """ Filters drops by names"""

        item_list = []
        for i, x in enumerate(drops[0]):

            if i == 0:
                continue
            elif i == len(drops[0]) - 1:
                break
            x = x.lower()
            if isinstance(items, str):
                items = items.lower()
                if items in x:
                    if funcType == "get":
                        return x
                    elif funcType == "check":
                        return True
            elif isinstance(items, list):
                items = [x.lower() for x in items]
                if funcType == "get":
                    try:
                        item_list.append([x for item in items if item in x][0])
                    except IndexError:
                        continue
                elif funcType == "check":
                    if (any(item in x for item in items)):
                        return True
        if funcType == "get":
            return item_list
        elif funcType == "check":
            return False

    
    async def get_drops_by_name(self, items:(str,list)) -> list:
        """ Returns a string or list of drops by names from latest battle"""

        chat = await self.get_chat()
        if (flag := self.flag_check()):
            return flag
        
        drops = await self.get_last_battle(chat)
        return self.drops_by_name(drops, items, "get")
    

    async def log_all_drops(self):
        drops = await self.get_drops()
        for drop in drops:
            print(f"Drop: {drop}")
  
  
    async def check_drops_by_name(self, items:(str,list)) -> bool:
        """ Returns a boolean if all items were dropped from latest battle"""

        chat = await self.get_chat()
        if (flag := self.flag_check()):
            return flag
        
        drops = await self.get_last_battle(chat)
        return self.drops_by_name(drops, items, "check")






        
    
