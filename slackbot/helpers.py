
def input_to_searchkeys(command):
    command = command.split(' ')
    command = [x.strip(' ') for x in command if len(x.strip(' ')) > 0]
    searchkeys = []
    x = 0
    while x < len(command):
        if command[x][0:2] == '--':
            searchkeys.append(str(command[x]))
            x += 1
        elif x == len(command)-1:
            searchkeys.append(str(command[x]))
            x += 1
        elif command[x][0] == "'" and command[x][-1] != "'":
            found = False
            y = x
            full = command[x]
            while found == False:
                full = ' '.join([full, command[y+1]])
                y += 1
                if command[y][-1] == "'":
                    found = True
            searchkeys.append(str(full))
            x += 1 + (y-x)
        else:
            searchkeys.append(str(command[x]))
            x += 1
    searchkeys = [key.strip("'").strip('"') for key in searchkeys][1:]
    print searchkeys
    return searchkeys


#import re
#print re.findall("([^']*)'", input_command)