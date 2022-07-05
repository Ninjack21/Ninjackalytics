from ast import increment_lineno
import psycopg2 as pps
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import os

def Generate_Bar_Chart(infodict):
    """
    This function will take a dictionary as created by the other query functions and generate a PI Chart which is sorted to show
    largest contributors to smallest contributors using a pleasing and consistent color palette
    It then uses battle_id + gname to create a unique filename to save the file under
    """
    units = infodict['Units']
    if 'Total' in list(infodict):
        del infodict['Total']
    
    del infodict['Units']

    #we want to sort the data going from largest contributors to lowest contributors
    info = sorted(infodict.items(), key=lambda item : item[1], reverse=True)
    #we try to zip and if it fails we create the fake infodict from when all values are 0
    try: 
        label,value = zip(*info)
        #let's remove any 0's from our data since it will not have any impact on the pi chart but will clutter the names
        cleanlabels = []
        cleanvalues = []
        i = 0
        for val in value:
            if val != 0:
                cleanlabels.append(label[i])
                cleanvalues.append(value[i])
            i = i+1

        infodict = {'clean labels' : cleanlabels,
        'clean values' : cleanvalues}

        if len(infodict['clean values']) == 0:
            infodict = {'clean labels' : ['None! - Ignore!'],
            'clean values' : [0.01]}
    except:
        infodict = {'clean labels' : ['None! - Ignore!'],
            'clean values' : [0.01]}

    df = pd.DataFrame.from_dict(infodict)
    sns.set_theme(palette = 'Spectral')
    sns.set_context('poster', font_scale = 0.7)
    sns.set_style(rc={'figure.facecolor' : '#000000', 'axes.facecolor' : '#000000', 'axes.labelcolor' : 'white', 'text.color' : 'white', 'xtick.color' : 'white'
    , 'ytick.color' : 'white', 'axes.spines.right' : 'False', 'axes.spines.top' : 'False', 'patch.edgecolor' : '#000000', 'xtick.bottom' : 'True'})
    fig = plt.figure(figsize=(6,4))
    fig = fig.set_facecolor('black')
    #if there is no plot at all
    ax = sns.barplot(x='clean values', y='clean labels', data = df, ci = None, orient = 'h')
    ax.grid(False)
    ax.set(xlabel = units, ylabel = None)

def Healing_Per_Entrance(battle_id, pnum, core_info):
    """
    This function takes the battle_id, the player number, the core_info, and the dmgs in order to determine the dmg / entrance stat
    It simply pulls the number of entrances for each pokemon and then takes their dmg and divides by entrances (if entrances != 0)
    Output is a dictionary with the dmg / entrance associated with each pokemon on that player's team
    """
    table_name = 'Switch'
    col_name = 'Pokemon_Enter'

    pname = core_info[pnum]['name']
    team = core_info[pnum]['team']

    #get the dmg dealt by all sources by re-running Dmg_Dealt_Breakdown
    #this is inefficient but the code is so simple currently that it is unimportant
    healing = Healing_Breakdown(battle_id, pnum, core_info)

    entrances = {}
    for mon in team:
        basiccond = [['Pokemon_Enter', mon]]
        instances = Basic_Select(table_name, col_name, battle_id, basiccond)
        numentrances = len(instances)
        #note, here we do not want to subtract 1 because of the starting switch-in as this does count as an entrance
        entrances[mon] = numentrances
    
    #healing-per-entrances
    hpes = {}
    for mon in team: 
        #have to check that the mon exists in healing (in case it had no healing)
        if mon in list(healing):
            totheal = healing[mon]
        #if a mon dealt no damage then in this scenario we will set totdmg = 0
        else:
            totheal = 0
        totentrances = entrances[mon]
        #ignore any pokemon who did not enter
        if totentrances != 0:
            hpes[mon] = (totheal / totentrances)
    hpes['Units'] = '% HP Recovery'
    return(hpes)

def Damage_Per_Entrance(battle_id, pnum, core_info):
    """
    This function takes the battle_id, the player number, the core_info, and the dmgs in order to determine the dmg / entrance stat
    It simply pulls the number of entrances for each pokemon and then takes their dmg and divides by entrances (if entrances != 0)
    Output is a dictionary with the dmg / entrance associated with each pokemon on that player's team
    """
    table_name = 'Switch'
    col_name = 'Pokemon_Enter'

    pname = core_info[pnum]['name']
    team = core_info[pnum]['team']

    #get the dmg dealt by all sources by re-running Dmg_Dealt_Breakdown
    #this is inefficient but the code is so simple currently that it is unimportant
    dmgs = Dmg_Dealt_Breakdown(battle_id, pnum, core_info)

    entrances = {}
    for mon in team:
        basiccond = [['Pokemon_Enter', mon]]
        instances = Basic_Select(table_name, col_name, battle_id, basiccond)
        numentrances = len(instances)
        #note, here we do not want to subtract 1 because of the starting switch-in as this does count as an entrance
        entrances[mon] = numentrances
    
    #damage-per-entrances
    dpes = {}
    for mon in team: 
        #have to check that the mon exists in dmgs (in case it dealt no damage)
        if mon in list(dmgs):
            totdmg = dmgs[mon]
        #if a mon dealt no damage then in this scenario we will set totdmg = 0
        else:
            totdmg = 0
        totentrances = entrances[mon]
        #ignore any pokemon who did not enter
        if totentrances != 0:
            dpes[mon] = (totdmg / totentrances)
    dpes['Units'] = '% HP Damage Dealt'
    return(dpes)   

def Turn_Action_Breakdown(battle_id, pnum, core_info):
    """
    This function takes the battle_id, the player number of interest, and the core_info in order to generate the turn action breakdown by the current player
    It returns a dictionary with the total and then each source's % contribution to make up the PI chart.
    May change this to send a graphic in the future to be reflected on the website
    """

    table_name = 'Actions'
    col_name = 'Action'

    pname = core_info[pnum]['name']

    #find the total number of turns in the battle
    turn_col_name = 'Turn'
    turns = Basic_Select(table_name, turn_col_name, battle_id, [])
    turns.sort
    totturns = turns[-1]
    totturns = int(totturns)
    
    #now find how many turns the player switched or moved
    actions = {}

    actionlist = ['switch','move']
    turnsnotnothing = 0
    for action in actionlist:
        basiccond = [[col_name, action], ["Player", pname]]
        instances = Basic_Select(table_name, col_name, battle_id, basiccond)
        turns = len(instances)
        #turn 0 is always switch and thus we should remove this "action" as it is always the case
        #also, if we left turn 0 then totturns needs to be increased by 1 and I disagree with that decision
        if action == 'switch':
            turns = turns - 1
        actions[action] = turns
        turnsnotnothing = turnsnotnothing + turns
    
    #the discrepancy between the number of turns and the sum of turns switching and using moves is how many turns were spent doing nothing
    turnsnothing = totturns - turnsnotnothing
    actions['nothing'] = turnsnothing
    actions['Units'] = '# of Turns Action Selected'
    return(actions)

def Heal_Type_Breakdown(battle_id, pnum, core_info):
    """
    This function takes the battle_id, the player number of interest, and the core_info in order to generate the total healing done by the current player
    and then determine the breakdown of all the different sources. It returns a dictionary with the total and then each source's % contribution to make up the PI chart.
    May change this to send a graphic in the future to be reflected on the website
    """

    table_name = 'Healing'
    col_name = 'Recovery'

    #we'll need to search using like and not like in SQL so prepare the opponent pnum and our pnum
    if pnum == 'P1':
        pnumopp = '%p2: %'
        pnumus = '%p1: %'
        enpnum = 'P2'
    else:
        pnumopp = '%p1: %'
        pnumus = '%p2: %'
        enpnum = 'P1'

    healing = {}

    #find all unique types of healing to the opponent
    advcond = [['Receiver', 'like', pnumus]]
    basiccond = 0
    type_col_name = 'Type'
    types = Advanced_Select(table_name, type_col_name, battle_id, basiccond, advcond)
    types = set(types)

    #now iterate by type
    for type in types:
        basiccond = [['Type', type]]
        advcond = [['Receiver', 'like', pnumus]]
        typeheals = Advanced_Select(table_name, col_name, battle_id, basiccond, advcond)
        sumtypeheals = sum(typeheals)
        healing[type] = sumtypeheals
    
    #finally determine the total healing
    advcond = [['Receiver', 'like', pnumus]]
    basiccond = 0
    total = Advanced_Select(table_name, col_name, battle_id, basiccond, advcond)
    sumtotal = sum(total)

    healing['Total'] = sumtotal
    healing['Units'] = '% HP Recovery'
    return(healing)

def Healing_Breakdown(battle_id, pnum, core_info):
    """
    This function takes the battle_id, the player number of interest, and the core_info in order to generate the total healing done by the current player
    and then determine the breakdown of all the different sources. It returns a dictionary with the total and then each source's % contribution to make up the PI chart.
    May change this to send a graphic in the future to be reflected on the website
    """

    table_name = 'Healing'
    col_name = 'Recovery'

    team = core_info[pnum]['team']

    #we'll need to search using like and not like in SQL so prepare the opponent pnum and our pnumus
    if pnum == 'P1':
        pnumopp = '%p2: %'
        pnumus = '%p1: %'
        enpnum = 'P2'
    else:
        pnumopp = '%p1: %'
        pnumus = '%p2: %'
        enpnum = 'P1'

    #iterate through using Advanced Select to get the healing received in total by each pokemon on the player's team
    healing = {}
    for mon in team:
        basiccond = [['Receiver', mon]]
        heals = Basic_Select(table_name, col_name, battle_id, basiccond)
        totheals = sum(heals)
        if totheals != 0:
            healing[mon] = totheals
    
    #finally determine the total healing by the player
    advcond = [['Receiver', 'like', pnumus]]
    basiccond = 0
    total = Advanced_Select(table_name, col_name, battle_id, basiccond, advcond)
    sumtotal = sum(total)

    healing['Total'] = sumtotal
    healing['Units'] = '% HP Recovery'
    return(healing)

def Dmg_Type_Breakdown(battle_id, pnum, core_info):
    """
    This function takes the battle_id, the player number of interest, and the core_info in order to generate the total damage dealt by the current player
    and then determine the breakdown of all the different sources. It returns a dictionary with the total and then each source's % contribution to make up the PI chart.
    May change this to send a graphic in the future to be reflected on the website
    """

    table_name = 'Damage'
    col_name = 'Damage'

    #we'll need to search using like and not like in SQL so prepare the opponent pnum and our pnum
    if pnum == 'P1':
        pnumopp = '%p2: %'
        pnumus = '%p1: %'
        enpnum = 'P2'
    else:
        pnumopp = '%p1: %'
        pnumus = '%p2: %'
        enpnum = 'P1'

    damages = {}

    #find all unique types of damage dealt to the opponent
    advcond = [['Receiver', 'like', pnumopp]]
    basiccond = 0
    type_col_name = 'Type'
    types = Advanced_Select(table_name, type_col_name, battle_id, basiccond, advcond)
    types = set(types)

    #now iterate by type
    for type in types:
        basiccond = [['Type', type]]
        advcond = [['Receiver', 'like', pnumopp]]
        typedmgs = Advanced_Select(table_name, col_name, battle_id, basiccond, advcond)
        sumtypedmgs = sum(typedmgs)
        damages[type] = sumtypedmgs
    
    #finally determine the total damage dealt to the opponent
    advcond = [['Receiver', 'like', pnumopp]]
    basiccond = 0
    total = Advanced_Select(table_name, col_name, battle_id, basiccond, advcond)
    sumtotal = sum(total)

    damages['Total'] = sumtotal
    damages['Units'] = '% HP Damage Dealt'
    return(damages)

def Dmg_Received_Breakdown(battle_id, pnum, core_info):
    """
    This function takes the battle_id, the player number of interest, and the core_info in order to generate the total damage received by the current player
    and then determine the breakdown of all the different sources. It returns a dictionary with the total and then each source's % contribution to make up the PI chart.
    May change this to send a graphic in the future to be reflected on the website
    """

    table_name = 'Damage'
    col_name = 'Damage'

    team = core_info[pnum]['team']

    #we'll need to search using like and not like in SQL so prepare the opponent pnum and our pnumus
    if pnum == 'P1':
        pnumopp = '%p2: %'
        pnumus = '%p1: %'
        enpnum = 'P2'
    else:
        pnumopp = '%p1: %'
        pnumus = '%p2: %'
        enpnum = 'P1'

    #iterate through the pokemon on your team to determine how much dmg each of your pokemon received
    damages = {}
    for mon in team:
        basiccond = [['Receiver', mon]]
        dmgs = Basic_Select(table_name, col_name, battle_id, basiccond)
        totdmg = sum(dmgs)
        if totdmg != 0:
            damages[mon] = totdmg
    
    #finally determine the total damage dealt to the opponent
    advcond = [['Receiver', 'like', pnumus]]
    basiccond = 0
    total = Advanced_Select(table_name, col_name, battle_id, basiccond, advcond)
    sumtotal = sum(total)

    damages['Total'] = sumtotal
    damages['Units'] = '% HP Damage Received'
    return(damages)

def Dmg_Dealt_Breakdown(battle_id, pnum, core_info):
    """
    This function takes the battle_id, the player number of interest, and the core_info in order to generate the total damage dealt by the current player
    and then determine the breakdown of all the different sources. It returns a dictionary with the total and then each source's % contribution to make up the PI chart.
    May change this to send a graphic in the future to be reflected on the website
    """

    table_name = 'Damage'
    col_name = 'Damage'

    team = core_info[pnum]['team']

    #we'll need to search using like and not like in SQL so prepare the opponent pnum and our pnumus
    if pnum == 'P1':
        pnumopp = '%p2: %'
        pnumus = '%p1: %'
        enpnum = 'P2'
    else:
        pnumopp = '%p1: %'
        pnumus = '%p2: %'
        enpnum = 'P1'

    #first iterate through using Advanced Select to get the damage dealt in total by each pokemon on the player's team
    damages = {}
    for mon in team:
        basiccond = [['Dealer', mon]]
        advcond = [['Receiver', 'like', pnumopp]]
        dmgs = Advanced_Select(table_name, col_name, battle_id, basiccond, advcond)
        totdmg = sum(dmgs)
        if totdmg != 0:
            damages[mon] = totdmg

    #now find all damages dealt to opponent from the non-pokemon types (other than opponent's own moves)
    #NOTE: THIS IGNORES ITEM BECAUSE ITEM CORRECTLY IDENTIFIES THE MON THAT HAD THE ITEM WHO DEALT IT - item dmgs will be reflected in type breakdowns
    dmg_types = ['hazard', 'status', 'passive']

    for dtype in dmg_types:
        #where column type is current damage type
        basiccond = [['Type', dtype]]
        #where receiver like opponent to remove damages we took
        advcond = [['Receiver', 'like', pnumopp]]

        curdmgs = Advanced_Select(table_name, col_name, battle_id, basiccond, advcond)
        totcurdmgs = sum(curdmgs)

        #now add to dictionary
        damages[dtype] = totcurdmgs

    #all that's left is finding the damages dealt to the opponent by the opponent themselves
    enteam = core_info[enpnum]['team']
    basiccond = 0
    for mon in enteam:
            #for receiver like enemy and dealer like current mon
            advcond = [['Receiver', 'like', pnumopp],['Dealer', 'like', '%' + mon + '%']]
            selfdmgs = Advanced_Select(table_name, col_name, battle_id, basiccond, advcond)
            totselfdmg = sum(selfdmgs)
            if totselfdmg != 0:
                damages[mon] = totselfdmg
    
    #finally determine the total damage dealt to the opponent
    advcond = [['Receiver', 'like', pnumopp]]
    basiccond = 0
    total = Advanced_Select(table_name, col_name, battle_id, basiccond, advcond)
    sumtotal = sum(total)

    damages['Total'] = sumtotal
    damages['Units'] = '% HP Damage Dealt'
    return(damages)

def Advanced_Select(table_name, col, battle_id, basiccond, advcond):
    
    """
    This function selects from "table_name" - "col" where "battle_id" and "basiccond"[0] equals "basiccond"[1] and "advcond" is more dynamic

    basiccond is a list of lists - [column, value] to be used in additional where clauses
    advcond is a list of lists of the form - [column, type, str] to be used for like and not like statements
        type is to be either 'like' or 'not like'

    This function will return the response as a list
    """
    #first connect to the database
    conn = pps.connect(host = 'ec2-44-196-174-238.compute-1.amazonaws.com', database = 'd39sfuos9nk0v3', user = 'geodgxbrnykumu', password = '6f97a508f497d1a7354e4e82791772b0837c4e66ca361090483e96fdce55e4c8')
    table_name = table_name.lower()
    #define the schema and encapsulation here to use for referencing the Table Name
    schema = 'public.'
    strtencap_col = '"'
    endencap_col = '"'
    strtencap_tbl = '"'
    endencap_tbl = '"'
    valencap = "'"
    
    #create the initial sql statement that we'll be adding where clauses to from conditionals
    sql = 'Select ' + strtencap_col + col + endencap_col + ' From ' + schema + strtencap_tbl + table_name + endencap_tbl + ' Where ' + strtencap_col + 'Battle_ID' + endencap_col + ' = ' +  valencap + battle_id + valencap

    if basiccond != 0:
        for clause in basiccond: 
            cur_col = clause[0]
            cur_val = clause[1]
            sql = sql + ' AND ' + strtencap_col + cur_col + endencap_col + ' = ' + valencap + cur_val + valencap

    for advclause in advcond:
        cur_col = advclause[0]
        cur_type = advclause[1]
        cur_str = advclause[2]
        sql = sql + ' AND ' + strtencap_col + cur_col + endencap_col + ' '  + cur_type + ' ' + valencap + cur_str + valencap

    sql = sql + ';'
        
    #let's attempt what we have just written
    try:
        #create a new cursor
        cur = conn.cursor()
        
        #execute the INSERT statement
        cur.execute(sql)
        
        response = cur.fetchall()

        #fetchall provides a list of tuples, want to get only the values and ignore the types provided
        cleanresponse = []
        for value in enumerate(response):
            if "'" in str(value):
                stringvalue = str(value[1])
                splitup = stringvalue.split("'")
                newval = splitup[1]
                newvaltype = splitup[0]
                if newvaltype == '(Decimal(':
                    cleanresponse.append(round(float(newval), 2))
                else:
                    cleanresponse.append(newval)
            else:
                stringvalue = str(value)
                splitup = stringvalue.split(', (')
                integercomma = splitup[1]
                integercommasplitup = integercomma.split(',')
                integer = integercommasplitup[0]
                cleanresponse.append(integer)

        conn.commit()

        return(cleanresponse)
    
    #if we encounter an error - return that error
    except (Exception, pps.DatabaseError) as error:
        print(error)



def Core_Info(battle_id):
    """
    This function takes the battle_id and finds the players, who won, and what pokemon were on each player's team

    The response of the function is a nested dictionary with 'px' --> [name, result, team] 
    where name is the name, result is either 'won' or 'lost', and team is a list of the mons as they are in the database
    """
    core_info = {}

    players = Basic_Select('battle_info', 'Player', battle_id, [])
    p1 = players[0]
    p2 = players[1]
    winner = Basic_Select('battle_info', 'Winner', battle_id, [])
    winner = winner[0]

    p1cond = [['Player', p1]]
    team1 = Basic_Select('team', 'Pokemon', battle_id, p1cond)
    player1 = {'name' : p1,
    'team' : team1
    }

    p2cond = [['Player', p2]]
    team2 = Basic_Select('team', 'Pokemon', battle_id, p2cond)
    player2 = {'name' : p2,
    'team' : team2
    }

    if winner == p1:
        player1['result'] = 'won'
        player2['result'] = 'lost'
    else:
        player1['result'] = 'lost'
        player2['result'] = 'won'
    
    core_info['P1'] = player1
    core_info['P2'] = player2
    return(core_info)

def Basic_Select(table_name, col, battle_id, conditionals):
    
    """
    This function selects from "table_name" - "col" where "battle_id" and "conditionals"[0] equals "conditionals"[1]
    conditionals is a list of lists - [column, value] to be used in additional where clauses
    This function will return the response as a list
    """
    #first connect to the database
    conn = pps.connect(host = 'ec2-44-196-174-238.compute-1.amazonaws.com', database = 'd39sfuos9nk0v3', user = 'geodgxbrnykumu', password = '6f97a508f497d1a7354e4e82791772b0837c4e66ca361090483e96fdce55e4c8')
    
    #heroku database uses all lowercase table names
    table_name = table_name.lower()

    #define the schema and encapsulation here to use for referencing the Table Name
    schema = 'public.'
    strtencap_col = '"'
    endencap_col = '"'
    strtencap_tbl = '"'
    endencap_tbl = '"'
    valencap = "'"
    
    #create the initial sql statement that we'll be adding where clauses to from conditionals
    sql = 'Select ' + strtencap_col + col + endencap_col + ' From ' + schema + strtencap_tbl + table_name + endencap_tbl + ' Where ' + strtencap_col + 'Battle_ID' + endencap_col + ' = ' +  valencap + battle_id + valencap

    for clause in conditionals: 
        cur_col = clause[0]
        cur_val = clause[1]
        sql = sql + ' AND ' + strtencap_col + cur_col + endencap_col + ' = ' + valencap + cur_val + valencap
    
    sql = sql + ';'
        
    #let's attempt what we have just written
    try:
        #create a new cursor
        cur = conn.cursor()
        
        #execute the INSERT statement
        cur.execute(sql)
        
        response = cur.fetchall()

        #fetchall provides a list of tuples, want to get only the values and ignore the types provided
        cleanresponse = []
        for value in enumerate(response):
            if "'" in str(value):
                stringvalue = str(value[1])
                splitup = stringvalue.split("'")
                newval = splitup[1]
                newvaltype = splitup[0]
                if newvaltype == '(Decimal(':
                    cleanresponse.append(round(float(newval), 2))
                else:
                    cleanresponse.append(newval)
            else:
                stringvalue = str(value)
                splitup = stringvalue.split(', (')
                integercomma = splitup[1]
                integercommasplitup = integercomma.split(',')
                integer = integercommasplitup[0]
                cleanresponse.append(integer)

        conn.commit()

        return(cleanresponse)
    
    #if we encounter an error - return that error
    except (Exception, pps.DatabaseError) as error:
        print(error)