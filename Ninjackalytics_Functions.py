state = 'production'
if state == 'localhost':
    import psycopg2 as pps
    import requests
    from datetime import date
    import re
    from . import connection as cnxn
else:
    import psycopg2 as pps
    import requests
    from datetime import date
    import re
    import connection as cnxn

def Run_Ninjackalytics(url):
    totalsql = {}
    response = Get_Response(url)
    logresponse = response[0]
    battle_id = response[1]
    if logresponse != 0:
        #now check if it's a new battle or already in the database
        new = Check_New_Battle(battle_id)
        # #if this battle already exists then go ahead and link to the page
        if new == 'no':
            return(battle_id)
        # #if this battle is new then continue with ninjackalytics
        else:

            bidstat = Get_BID_Info(logresponse)
            if bidstat[0] == 0:
                return(bidstat[1])
            else:
                table = list(bidstat[1])[0]
                stmts = list(bidstat[1][table])
                totalsql[table] = stmts

                tablecheck = list(bidstat[1])[1]
                stmtscheck = list(bidstat[1][tablecheck])
                totalsql[tablecheck] = stmtscheck
            
            teaminfostat = Get_Team_Info(logresponse)
            if teaminfostat[0] == 0:
                return(teaminfostat[1])
            else:
                table = list(teaminfostat[1])[0]
                stmts = list(teaminfostat[1][table])
                totalsql[table] = stmts
                nicknames = teaminfostat[2]

            dmghealstat = Get_Damage_and_Healing_Info(logresponse, nicknames)
            if dmghealstat[0] == 0:
                return(dmghealstat[1])
            else:
                tabledmg = list(dmghealstat[1])[0]
                stmtsdmg = list(dmghealstat[1][tabledmg])
                totalsql[tabledmg] = stmtsdmg

                tableheal = list(dmghealstat[2])[0]
                stmtsheal = list(dmghealstat[2][tableheal])
                totalsql[tableheal] = stmtsheal

            switchstat = Get_Switch_Info(logresponse, nicknames)
            if switchstat[0] == 0:
                return(switchstat[1])
            else:
                table = list(switchstat[1])[0]
                stmts = list(switchstat[1][table])
                totalsql[table] = stmts

            actionstat = Get_Action_Info(logresponse)
            if actionstat[0] == 0:
                return(actionstat[1])
            else:
                table = list(actionstat[1])[0]
                stmts = list(actionstat[1][table])
                totalsql[table] = stmts

        # #now that we've run - double check one last time that it hasn't been added while we were running Ninjackalytics
        new = Check_New_Battle(battle_id)
        if new == 'no':
            return(battle_id)
        # #if this battle doesn't already exist then go ahead and add everything!
        else:
            # if it still is not in the database we are going to try to add it - if it adds succesfully then we will make fnl_chk = 'add'. Otherwise it will be 'do not add'. 
            # This is because a key error will be thrown if 2 try to add simultaneously. Whereas if we simply checked if it existed I think it'd be possible for them to both 
            # not see each other and then both add simultaneously which I do not want. If we decouple the addition of the Unique_Battle_IDs and the rest of the data we should 
            # be able to avoid this.
            try: 
                checkdb = list(totalsql)[1]
                Add_sql(checkdb, totalsql[checkdb][0])
                fnl_check = 'add'
            #if this fails then simply return the battle_id as it already exists now.
            except:
                fnl_check = 'do not add'

                return(battle_id)

            # now we just check fnl_check and follow it's instructions
            finally:
                if fnl_check == 'add':
                    #remove the Unique_Battle_IDs from the totalsql dictionary before adding as it has now already happened
                    del totalsql['unique_battle_ids']
                    for i, table in enumerate(list(totalsql)):
                        for i, stmt in enumerate(totalsql[table]):
                            Add_sql(table, stmt)
                    #if all succeeds then we want to be redirected to the page with the battle statistics
                    #otherwise we want to see a custom message
                    return(battle_id)
                else:
                    return(battle_id)
    #if there was no response from the url provided the battle_id will instead be the user message saying as much
    else:
        return(battle_id)

#--------------------START WITH SQL INTERACTION FUNCTIONS ------------------------------------------------------
def Generate_Insert_Statement(col_names, values, val_types):
    
    """
    This function takes, as a python list, the column names, values to be added, and the types of each value ('Date', 'Text', or 'Number')
    and creates the appropriate strings for Python to pass to the Add to SQL Function. 
    The response from this function is a list where response[0] = column_names_string and response[1] = values_to_be_added_string
    """
    
    #first, let's encapsulate the columns and generate the string to be provided to our add to sql function
    strtencap_col = '"'
    endencap_col = '"'
    col_string = ''
    
    for column in col_names:
        if col_string =='':
            col_string = strtencap_col + column + endencap_col
        else:
            col_string = col_string + ',' + strtencap_col + column + endencap_col
    
    response = [col_string]
    
    
    #------------ now we get to check what type each value is and perform the necessary manipulations to create val_string
    encap_val = "'"
    
    val_string = ''
    
    for i, value in enumerate(values):
        
        if val_string == '':
            if val_types[i] == 'Date':
                val_string = "TO_DATE('" + str(values[i]) + "','YYYY/MM/DD')"
            elif val_types[i] == 'Number':
                val_string = str(values[i])
            elif val_types[i] == 'Text':
                if "'" in str(values[i]):
                    val = values[i].replace("'",' ')
                else:
                    val = values[i]
                val_string = encap_val + val + encap_val
        
        else:
            if val_types[i] == 'Date':
                val_string = val_string + ',' + "TO_DATE('" + str(values[i]) + "','YYYY/MM/DD')"
            elif val_types[i] == 'Number':
                val_string = val_string + ',' + str(values[i])
            elif val_types[i] == 'Text':
                if "'" in str(values[i]):
                    val = values[i].replace("'",' ')
                else:
                    val = values[i]
                val_string = val_string + ',' + encap_val + val + encap_val
    
    response.append(val_string)
    return(response)
#let's create a function that will take any table_name, col_names, col_info and write to any sql table
def Add_sql(table_name, GIS_response):
    
    """
    This function takes the table name, column names, and column_info (values to be added) and adds them to the database and prints any errors if they occur.
    """
    #first connect to the database
    conn = cnxn.connection()
    #define the schema and encapsulation here to use for referencing the Table Name
    schema = 'public.'
    strtencap = '"'
    endencap = '"'
    
    sql = 'INSERT INTO ' + schema + strtencap + table_name + endencap + '(' + GIS_response[0] + ')' + ' VALUES (' + GIS_response[1] + ');'
    #let's attempt what we have just written
    try:
        #create a new cursor
        cur = conn.cursor()
        
        #execute the INSERT statement
        cur.execute(sql)
        
        conn.commit()
    
    #if we encounter an error - return that error
    except (Exception, pps.DatabaseError) as error:
        print(error)

    finally:
        cur.close()
        conn.close()
     
def Check_New_Battle(battle_id):
    """
    take the provided battle_id and see if this battle exists in the Ninjackalytics' database already or not
    (responses are to the variable name used of "new")
    """
    table_name = 'unique_battle_ids'
    col_name = 'Battle_ID'
    GSS_response = Generate_Select_Statement(col_name, battle_id, 'Text')
    
    check_for_bid = Select_sql(table_name, GSS_response)

    if check_for_bid:
        return('no')
    else:
        return('yes')

def Generate_Select_Statement(col_name, value, val_type):
    
    """
    This function takes the column you want to search, the value you want to search for (along with its type) and properly syntaxes them for the select_sql function.
    The output of this function is response, where response[0] = the col_string to search for and response[1] = the val_string you'll be searching for
    """
    
    #first, let's encapsulate the columns and generate the string to be provided to our add to sql function
    strtencap_col = '"'
    endencap_col = '"'

    col_string = strtencap_col + col_name + endencap_col
    
    response = [col_string]
    
    encap_val = "'"
        
    if val_type == 'Date':
        val_string = "TO_DATE('" + str(value) + "','YYYY/MM/DD')"
    elif val_type == 'Number':
        val_string = str(value)
    elif val_type == 'Text':
        val_string = encap_val + value + encap_val
    
    response.append(val_string)
    
    return(response)

def Select_sql(table_name, GSS_response):
    
    """
    This function takes the table name, column names, and column_info (values to be added) and pulls their information
    """
    
    #first connect to the database
    conn = cnxn.connection()
    #define the schema and encapsulation here to use for referencing the Table Name
    schema = 'public.'
    strtencap = '"'
    endencap = '"'
    
    sql = 'Select ' + GSS_response[0] + ' From ' + schema + strtencap + table_name + endencap + ' Where ' + GSS_response[0] + ' = ' + GSS_response[1] + ';'
        
    #let's attempt what we have just written
    try:
        #create a new cursor
        cur = conn.cursor()
        
        #execute the INSERT statement
        cur.execute(sql)
        
        response = cur.fetchall()

        conn.commit()
        
        return(response)

    #if we encounter an error - return that error
    except (Exception, pps.DatabaseError) as error:
        print(error)
    
    finally:
        cur.close()
        conn.close()
    
# ---------------------------- BEGIN DB DATA GATHERING FUNCTIONS HERE ------------
def Get_Response(url):
    """
    This function gets the json response for any replay url passed to it and returns that dictionary
    """
    urljson = url + '.json'
    response = requests.get(urljson)

    if response.status_code == 200:

        response = response.json()
        battle_id = response['id']
        return(response, battle_id)

    else:
        usermsg = 'Error = Oops! no response from: ' + url + ' - check that you entered it correctly'
        response = usermsg
        return(0, usermsg)
    
def Search(string, log):
    """
    This function will search the log for a particular string that you pass it and respond with 'yes' if it finds the string in the log and 'no' if it does not
    """
        
    if string in log:
        response = 'yes'
    else:
        response = 'no'
            
    return(response)

def Get_BID_Info(response):
    
    """
    This function gathers the information needed for the Battle_ID database and returns a list of 2 lists:
    1) the information from player 1's perspective
    2) the information from player 2's perspective
    """
    try:
        #Gather battle_id, p1, p2, format
        battle_id = response['id']
        p1 = response['p1id']
        p2 = response['p2id']
        battle_format = response['formatid']

        #prep error table information
        funcname = 'Get_BID_Info'
        current_step = '0 - begin'
        parameters = ''

        #we also want to get the date this url was submitted
        date_sub = date.today()

        #private always defaults to false as this may be added later but will not be right now.
        private = 'FALSE'

        #and then the log (for determining winner and rank)
        log = response['log']

        current_step = '1 - find player names'

        #have to redefine name for rated and win checks because the json response is all lowercase and the split is case sensitive...
        p1nprep = log.split('player|p1|')
        p1nprep = p1nprep[1].split('|')
        p1_name = p1nprep[0]

        p2nprep = log.split('player|p2|')
        p2nprep = p2nprep[1].split('|')
        p2_name = p2nprep[0]

        #define the player ranks ----------------------------------------------------------------------------

        current_step = '2 - determine if ranked, then find rank if so'

        rated_indication = '|rated'
        tournament_indication = '|Tournament battle'
        rated = Search(rated_indication, log)
        tourny = Search(tournament_indication, log)

        if (rated == 'no') or (tourny == 'yes'):
            p1_rank = 'null'
            p2_rank = 'null'

        else:
            p1_rank_str = p1_name + "'s rating: "
            p2_rank_str = p2_name + "'s rating: "
            prepp1 = log.split(p1_rank_str)
            prepp2 = log.split(p2_rank_str)

            p1_rank = (prepp1[1].split(' '))[0]
            p2_rank = (prepp2[1].split(' '))[0]

        current_step = '3 - determine if tie, otherwise find winner'

        tie_indication = 'accepted the tie.\n|\n|tie'
        tie = Search(tie_indication, log)

        if tie == 'yes':
            winner = 'tie'
        else:
            p1_win_indic = '|win|' + p1_name
            p1win = Search(p1_win_indic, log)

            if p1win == 'yes':
                winner = p1
            else:
                winner = p2

        bidp1 = [battle_id, date_sub, battle_format, p1, p1_rank, private, winner]
        bidp2 = [battle_id, date_sub, battle_format, p2, p2_rank, private, winner]
        types = ['Text', 'Date', 'Text', 'Text', 'Number', 'Text', 'Text']

        table_name = 'battle_info'
        col_names = ['Battle_ID', 'Date_Submitted', 'Format', 'Player', 'Rank', 'Private', 'Winner']

        current_step = '4 - create insert statements'

        add_p1 = Generate_Insert_Statement(col_names, bidp1, types)
        add_p2 = Generate_Insert_Statement(col_names, bidp2, types)

        table_name_check = 'unique_battle_ids'

        col_names_check = ['Battle_ID']
        values_check = [battle_id]
        types_check = ['Text']

        check_db = Generate_Insert_Statement(col_names_check, values_check, types_check)

        add_ps = [add_p1, add_p2]
        bidsql = {}
        bidsql[table_name] = add_ps
        bidsql[table_name_check] = [check_db]
        return (1, bidsql)
    except Exception as error:
        usermsg = "Error = Oops! Something went wrong while gathering the battle's identifying information!\nThe Beheeyem employed have been notified of the error and will take a look!"
        
        #if already in errors table then just return the usermsg
        try:
            table_name='errors'
            values = [battle_id, date_sub, funcname, current_step, parameters, error]
            val_types = ['Text', 'Date', 'Text', 'Text', 'Text', 'Text']
            col_names = ['Battle_ID', 'Date', 'Func_Name', 'Current_Step', 'Parameters', 'Error_Message']

            error_stmt = Generate_Insert_Statement(col_names, values, val_types)
            Add_sql(table_name, error_stmt)

            return(0, usermsg)
        except:
            return(0, usermsg)

def Get_Team_Info(response):
    
    """
    This function takes the response from Get_Response(url) and adds to the Team Database what pokemon they brought and returns a dictionary with the nicknames discovered for each pokemon
    """
    try: 

        battle_id = response['id']
        p1 = response['p1id']
        p2 = response['p2id']
        log = response['log']
        col_names = ['Battle_ID', 'Player', 'Pokemon']
        table_name = 'team'

        #prep error table information
        funcname = 'Get_Team_Info'
        current_step = '0 - begin'
        parameters = ''
        date_sub = date.today()

        mon_preview = log.split('|clearpoke\n')
        mon_preview = mon_preview[1].split('|teampreview')
        mon_preview = mon_preview[0]

        parameters = mon_preview

        team_preview = []

        current_step = '1 - find p1 mons'

        p1_mon_preview = (mon_preview.split('poke|p2'))[0]
        p1_mon_preview = p1_mon_preview.split('|poke|p1|')
        p1_mon_preview.pop(0)

        p1_mons = []    
        for mon in p1_mon_preview:
            parameters = mon
            comma = Search(',', mon)
            asterisk = Search('*', mon)
            bracket = Search('|\n', mon)
            #this next one is for you Urshifu...
            dash_asterisk = Search('-*', mon)
            if dash_asterisk == 'yes':
                name = (mon.split('-*'))[0]
                p1_mons.append('p1: ' + name)
            elif comma == 'yes':
                name = (mon.split(','))[0]
                p1_mons.append('p1: ' + name)
            elif asterisk == 'yes':
                name = (mon.split('-*'))[0]
                p1_mons.append('p1: ' + name)
            elif bracket == 'yes':
                name = (mon.split('|\n'))[0]
                p1_mons.append('p1: ' + name)
            else:
                name = (mon.split('\n'))[0]
                p1_mons.append('p1: ' + name)

        team_preview.append(p1_mons) 

        number_p1_mons = len(p1_mons)

        current_step = '2 - find p2 mons'

        p2_mon_preview = (mon_preview.split('poke|p1'))[number_p1_mons]
        p2_mon_preview = p2_mon_preview.split('|poke|p2|')
        p2_mon_preview.pop(0)
        p2_mons = []    
        for mon in p2_mon_preview:
            parameters = mon
            comma = Search(',', mon)
            asterisk = Search('*', mon)
            bracket = Search('|\n', mon)
            #this next one is for you Urshifu...
            dash_asterisk = Search('-*', mon)
            
            if dash_asterisk == 'yes':
                name = (mon.split('-*'))[0]
                p2_mons.append('p2: ' + name)
            elif comma == 'yes':
                name = (mon.split(','))[0]
                p2_mons.append('p2: ' + name)
            elif asterisk == 'yes':
                name = (mon.split('-*'))[0]
                p2_mons.append('p2: ' + name)
            elif bracket == 'yes':
                name = (mon.split('|\n'))[0]
                p2_mons.append('p2: ' + name)
            else:
                name = (mon.split('\n'))[0]
                p2_mons.append('p2: ' + name)

        team_preview.append(p2_mons)

        current_step = '3 - create insert statements for team table'
        parameters = ''

        val_types = ['Text', 'Text', 'Text']
        prepsql = []
        for i, player in enumerate(team_preview):
            for mon in (team_preview[i]):
                if i == 0:
                    values = [battle_id, p1, mon]
                    sql_info = Generate_Insert_Statement(col_names, values, val_types)
                    prepsql.append(sql_info)
                else:
                    values = [battle_id, p2, mon]
                    sql_info = Generate_Insert_Statement(col_names, values, val_types)
                    prepsql.append(sql_info)

        current_step = '4 - build nicknames dict'

        #we've added the nickname failure specific message
        nicknames = Build_nns(log, team_preview, battle_id)
        if nicknames == "Error = Oops! Something went wrong while finding pokemon nickanmes" + "\nThe Beheeyem employed have been notified of the error and will take a look!":
            return(0, nicknames)
        
        else:
            teaminfosql = {}
            teaminfosql[table_name] = prepsql

            return(1, teaminfosql, nicknames)
    except Exception as error:
        usermsg = "Error = Oops! Something went wrong while gathering the info for each Team!\nThe Beheeyem employed have been notified of the error and will take a look!"

        #if already in errors table then just return the usermsg
        try:
            table_name='errors'
            values = [battle_id, date_sub, funcname, current_step, parameters, error]
            val_types = ['Text', 'Date', 'Text', 'Text', 'Text', 'Text']
            col_names = ['Battle_ID', 'Date', 'Func_Name', 'Current_Step', 'Parameters', 'Error_Message']

            error_stmt = Generate_Insert_Statement(col_names, values, val_types)
            Add_sql(table_name, error_stmt)

            return(0, usermsg)
        except:
            return(0, usermsg)
    
def Find_nn(log, player_num, mon, battle_id):
    
    """
    this function finds the nickname of a player's pokemon and returns either the discovered nickname or simply the pokemon's name if that pokemon never entered the battle
    """
    try: 
        
        #prep error table information
        funcname = 'Find_nn'
        current_step = '0 - begin'
        parameters = 'looking for: ' + str(player_num) + "'s " + str(mon)

        mon = mon.split('p' + str(player_num) + ': ')
        mon = mon[1]

        current_step = '1 - create entrance regex search expression'

        entrance = 'p'+ str(player_num) + '.: .+[|]' + mon + '.*[|].*/.*'
        match = re.search(entrance, log)
        if match:
            parameters = str(match)
            current_step = '2 - we found the mon - now get nickname from response'
            splitme = match.group()
            splitme = splitme.split(': ')
            splitme = splitme[1]
            splitme = splitme.split('|' + mon)
            
            name = splitme[0]
            return(name)

        else:
            #if we never see this pokemon enter then we don't need it's name
            return(mon)
    except Exception as error:
        usermsg = "Error = Oops! Something went wrong while finding " + str(player_num) + "'s " + str(mon) + "'s nickname" + "\nThe Beheeyem employed have been notified of the error and will take a look!"

        #if already in errors table then just return the usermsg
        try:
            date_sub = date.today()
            table_name='errors'
            values = [battle_id, date_sub, funcname, current_step, parameters, error]
            val_types = ['Text', 'Date', 'Text', 'Text', 'Text', 'Text']
            col_names = ['Battle_ID', 'Date', 'Func_Name', 'Current_Step', 'Parameters', 'Error_Message']

            error_stmt = Generate_Insert_Statement(col_names, values, val_types)
            Add_sql(table_name, error_stmt)
        except:
            d=1

def Build_nns(log, team_preview, battle_id):
    
    """
    This function iterates through the 2 lists of player's pokemon in team_preview from Get_Team_Info and builds a dictionary that relates the nicknames for a particular player to their
    normal pokemon name and returns these as a dictionary of the form nicknames[p1/2][nickname] = normal pokemon name.
    """
    try:
        nicknames = {}
        p1dict = {}
        p2dict = {}

        #team preview is a list of lists, beginning with player 1's list of mons brought
        for i, player in enumerate(team_preview):
                for mon in (team_preview[i]):
                    
                    if i == 0:
                        player_num = 1
                        name = Find_nn(log, player_num, mon, battle_id)
                        p1dict[name] = mon
                    else:
                        player_num = 2
                        name = Find_nn(log, player_num, mon, battle_id)
                        p2dict[name] = mon
        
        nicknames['p1'] = p1dict
        nicknames['p2'] = p2dict
        return(nicknames)
    except Exception as error:
        usermsg = "Error = Oops! Something went wrong while finding pokemon nickanmes" + "\nThe Beheeyem employed have been notified of the error and will take a look!"
        return(usermsg)

def Get_Damage_and_Healing_Info(response, nicknames):
    try: 
        dmgsql = []
        healsql = []
        battle_id = response['id']
        p1 = response['p1id']
        p2 = response['p2id']
        log = response['log']

        #prep error table information
        funcname = 'Get_Damage_and_Healing_Info'
        current_step = '0 - begin'
        parameters = response
        date_sub = date.today()
        #now I need to split the log into turns and remove the intro information
        
        turns = log.split('|start\n')
        turns = turns[1].split('|turn|')
        
        #now we want to initialize our HP tracker dictionary with every pokemon at 100%
        hp = {}
        
        for player in list(nicknames):
            for name in list(nicknames[player]):
                real_name = nicknames[player][name]
                hp[real_name] = 100
        
        #now we want to begin iterating through the turns, line by line in each turn, and classifying all the types of damages, 
        #prepare their Add_sql information, and update the hp tracker
        
        #we need to define what hazards and status conditions exist at the current moment 
        #(later, can pull these from a file if desired but for now, will hard code in)
        haz_list = ['Stealth Rock', 'Spikes', 'G-Max Steelsurge']
        stat_list = ['psn', 'brn']
        #this will run through the battle sequentially and i will indicate what turn we are currently looking at

        current_step = '1 - begin iterating through turns'

        i = -1
        for turn in turns:
            i = i + 1
            lines = turn.split('\n')
            turn_num = i
            for line in lines:
                funcname = 'Get_Damage_and_Healing_Info'
                #have the parameter always be the current line
                parameters = line
                #we need to ignore any line that begins with '|c|'
                if not '|c|' in line:
                    is_damage = Search('|-damage|', line)
                    is_faint = Search('|faint|', line)
                    is_heal = Search('|-heal|', line)
                    
                    #----- begin damage logic -----------
                    
                    if is_damage == 'yes':
                        col_names = ['Battle_ID', 'Turn', 'Type', 'Dealer', 'Name', 'Receiver', 'Damage']
                        table_name = 'damage'
                        
                        is_not_move = Search('[from]', line)
                        #ik ik, double negatives, it works, though
                        if is_not_move == 'no':
                            dmg_type = 'move'
                            dmg_static_vals = [battle_id, turn_num, dmg_type, col_names]
                            
                            current_step = '2 - gather move damage info'
                            funcname = 'Gather_Move_Info'
                            dmg_info = Gather_Move_Info(line, turn, log)
                            funcname = 'Add_To_Damage'
                            atd_response = Add_To_Damage(dmg_static_vals, dmg_info, nicknames, hp)
                            hp = atd_response[0]
                            dmgsql.append(atd_response[1])
                        #now begin [from] damages logic parsing
                        else:
                            is_item = Search('[from] item:', line)
                            is_ability = Search('[from] ability:', line)
                            stat_haz_check = line.split('[from] ')
                            stat_haz_check = stat_haz_check[1]
                            stat_haz_check = stat_haz_check.split('|')
                            stat_haz_check = stat_haz_check[0]
                            
                            #let's try making the default response no and only changing it if necessary
                            is_haz = 'no'
                            is_stat = 'no'
                            
                            if stat_haz_check in haz_list:
                                is_haz = 'yes'
                            elif stat_haz_check in stat_list:
                                is_stat = 'yes'
                            
                            #now define dmt_type and let's add to the database!
                            
                            if is_item == 'yes': 
                                dmg_type = 'item'

                            elif is_ability == 'yes':
                                dmg_type = 'ability'

                            elif is_haz == 'yes':
                                dmg_type = 'hazard'

                            elif is_stat == 'yes':
                                dmg_type = 'status'

                            #if none of the above if statements are true then the only remaining type is passive
                            else:
                                dmg_type = 'passive'
                            
                            current_step = '2 - gather non-move damage info'
                            funcname = 'Add_Damage_Info'
                            adi_response = Add_Damage_Info(dmg_type, battle_id, turn_num, col_names, table_name, line, turn, nicknames, hp)
                            hp = adi_response[0]
                            dmgsql.append(adi_response[1])
                    
                    #if the line has |faint| then we are going to determine who fainted and simply call it passive
                    elif is_faint == 'yes':
                        current_step = '2 - gather faint mon background info'
                        dmg_type = 'passive'
                        col_names = ['Battle_ID', 'Turn', 'Type', 'Dealer', 'Name', 'Receiver', 'Damage']
                        table_name = 'damage'
                        
                        # https://replay.pokemonshowdown.com/gen8ou-1510969757 -> |faint|p1a: Al'Queda
                        
                        line = line.split('|')
                        receiver = line[2]
                        receiver = receiver.split('\n')
                        receiver = receiver[0]
                        dealer = receiver
                        name = 'faint'
                        new_hp = 0
                        
                        #if the receiver's hp is already 0, then ignore, otherwise add this (indicates the user used a self-killing move like final gambit)
                        if 'p1' in receiver:
                            player = 'p1'
                        else:
                            player = 'p2'
                        
                        nickname = receiver[5:]
                        real_name_receiver = nicknames[player][nickname]
                        check_cur_hp = hp[real_name_receiver]
                        if check_cur_hp != 0:
                            dmg_info = [dealer, name, receiver, new_hp]
                            dmg_static_vals = [battle_id, turn_num, dmg_type, col_names, table_name]
                            current_step = '3 - gather faint mon damage info'
                            funcname = 'Add_Damage_Info'
                            adi_response = Add_Damage_Info(dmg_type, battle_id, turn_num, col_names, table_name, line, turn, nicknames, hp)
                            hp = adi_response[0]
                            dmgsql.append(adi_response[1])

                    #now let's check for if the heal keyword is present            
                    elif is_heal == 'yes':
                        current_step = '2 - determine heal type'
                        col_names = ['Battle_ID', 'Turn', 'Type', 'Name', 'Receiver', 'Recovery']
                        table_name = 'healing'
                        is_item = Search('[from] item', line)
                        is_ability = Search('[from] ability', line)
                        is_passive = Search('[silent]', line)
                        #this one has to be last
                        is_other = Search('[from] ', line)
                        if is_item == 'yes':
                            heal_type = 'item'
                        elif is_ability == 'yes':    
                            heal_type = 'ability'
                        elif is_passive == 'yes':
                            heal_type = 'passive'
                        elif is_other == 'yes':
                            #now we need to check if it's from the drain, which indicates the user used a move or if it's truly something else and we should consider it passive - like grassy terrain
                            check_for_drain = Search('drain', line)
                            check_for_move = Search('move', line)
                            if (check_for_drain == 'yes') or (check_for_move == 'yes'):
                                heal_type = 'move'
                            else:
                                heal_type = 'passive'
                        else:
                            heal_type = 'move'

                        heal_static_vals = [battle_id, turn_num, heal_type, col_names, table_name]
                        current_step = '3 - gather heal info'
                        funcname = 'Add_Healing_Info'
                        ahi_response = Add_Healing_Info(heal_static_vals, line, turn, nicknames, hp, battle_id)
                        hp = ahi_response[0]
                        healsql.append(ahi_response[1])
                    #----- begin hp_update logic for switch lines-----------
                    #here we need to check if the hp has changed without a damage or heal keyword - if so - the reason is regenerator
                    else:
                        current_step = '4 - determine if regenerator healing occured'
                        hp_seen = regex_search(line)
                        if hp_seen == 'yes':
                            if 'p1' in line:
                                player = 'p1'
                            else:
                                player = 'p2'
                            funcname = 'Gather_HP_Info'
                            hp_info = Gather_HP_Info(line, player, nicknames)
                            #first obj in hp_info is name and second is current hp   
                            name = hp_info[0]
                            #let's see what the dictionary currently believes the hp to be
                            compare_hp = hp[name]
                            cur_hp = hp_info[1]

                            #this means the mon must have regenerator if they are not equal
                            if compare_hp != cur_hp:
                                heal_type = 'ability'

                                col_names = ['Battle_ID', 'Turn', 'Type', 'Name', 'Receiver', 'Recovery']
                                table_name = 'healing'

                                heal_static_vals = [battle_id, turn_num, heal_type, col_names, table_name]
                                current_step = '5 - gather regerator healing info'
                                funcname = 'Add_Healing_Info'
                                ahi_response = Add_Healing_Info(heal_static_vals, line, turn, nicknames, hp, battle_id)
                                hp = ahi_response[0]
                                healsql.append(ahi_response[1])

                            hp[name] = cur_hp

        finaldmgsql = {}
        finalhealsql = {}
        finaldmgsql['damage'] = dmgsql
        finalhealsql['healing'] = healsql
        
        return([1, finaldmgsql, finalhealsql])
    except Exception as error:
        usermsg = "Error = Oops! Something went wrong while gathering this battle's damage and healing information! \nThe Beheeyem employed have been notified of the error and will take a look!"
        #if already in errors table then just return the usermsg
        try:
            table_name='errors'
            date_sub = date.today()
            values = [battle_id, date_sub, funcname, current_step, parameters, str(error)]
            val_types = ['Text', 'Date', 'Text', 'Text', 'Text', 'Text']
            col_names = ['Battle_ID', 'Date', 'Func_Name', 'Current_Step', 'Parameters', 'Error_Message']

            error_stmt = Generate_Insert_Statement(col_names, values, val_types)
            Add_sql(table_name, error_stmt)

            return(0, usermsg)
        except:
            return(0, usermsg)

def regex_search(line):
    """
    This function takes a line and checks to see if hp indication is anywhere in it 
    I needed regex because some formats do not standardize hp to 100 and thus '/100' will not work as a search criteria
    """
    
    hp_look = '[/]\d+'
    match = re.search(hp_look, line)
    if match:
        return('yes')
    else:
        return('no')    

def Gather_Move_Info(line, turn, log):
    try: 
        og_line = line
        line = line.split('|')
        line = line[2:]
        receiver = line[0]

        if 'fnt' in line[1]:
            new_hp = 0
        else:
            line = line[1].split('/')
            #because in some cases hp is reflected as raw numbers, we must now check for and remove any status condition labels like psn or brn
            cur_hp = float(line[0])
            
            max_hp = line[1]
            max_hp = max_hp.split(' ')
            max_hp = max_hp[0]
            max_hp = max_hp.split('\n')
            max_hp = float(max_hp[0])
            
            new_hp = round(((cur_hp / max_hp) * 100), 2)
            
        prev_lines = turn.split(og_line)
        #need to only check what occured before this damage keyword
        prev_lines = prev_lines[0]
        search_lines = prev_lines.split('\n')
        search_lines.reverse()
        
        dealer = []
        
        for search_line in search_lines:
            is_move = Search('|move|', search_line)
            # |-end|p1a: Corvikstall|move: Future Sight <-- example of a move damage that is of a different format
            is_end_move = Search('|-end|', search_line)
            #apparently, multi turn moves will not reveal their target until we see the -anim keyword
            is_anim = Search('|-anim|', search_line)
            if is_move == 'yes':
                search_line = search_line.split('|')
                search_line.pop(0)
                if search_line[3]:
                    #need to drop '\n' if it's at the end potentially
                    check = search_line[3].split('\n')
                    compare_receiver = check[0]
                    if receiver == compare_receiver:
                        dealer = search_line[1]
                        name = search_line[2]
                        #we have to exit our for loop once we have found the information we desire
                        break
            elif is_anim == 'yes':
                search_line = search_line.split('|')
                search_line.pop(0)
                if search_line[3]:
                    compare_receiver = search_line[3]
                    if receiver == compare_receiver:
                        dealer = search_line[1]
                        name = search_line[2]
                        #we have to exit our for loop once we have found the information we desire
                        break
            elif is_end_move == 'yes':
                #now we have to ensure that the -end is of a move and not something like a sub breaking
                is_move = Search('move:', search_line)
                if is_move == 'yes':
                    name_search = search_line.split('|')
                    name_search = name_search[3]
                    name_search = name_search.split(': ')
                    name_search = name_search[1]
                    name = name_search.split('\n')
                    name = name[0]
                    #need to ensure this end move is actually impacting the receiver we are currently looking at - future sight and doom desire are serious pains lol
                    receiver_search = search_line.split('|')
                    compare_receiver = receiver_search[2]
                    if compare_receiver == receiver:
                        #getting the dealer for this move will require going backwards in the log to find who, on the enemy team, used this last
                        log = log.split(turn)
                        prev_turns = log[0]

                        #we'll need to know who the receiver player is to determine who the dealer is (and if you future sight yourself well... yeah idc, LOL)
                        rec_player = receiver[:2]
                        if rec_player == 'p1':
                            player = 'p2'
                        else:
                            player = 'p1'
                        #now let's head backwards until we find who used this move
                        prev_lines = prev_turns.split('\n')
                        prev_lines.reverse()
                        for line in prev_lines:
                            is_move = Search(name, line)
                            is_correct_player = Search(player, line)
                            if (is_move == 'yes') and (is_correct_player == 'yes'):
                                line = line.split('|')
                                dealer = line[2]
                                #we have to exit our for loop once we have found the information we desire
                                break
        #thus far, if we still have not defined the dealer this means that we used a move that hits multiple targets like rock slide (and thus may not have originally indicated it would target
        #the second pokemon as well (or third, like EQ into self-hit)
        #reference --> https://replay.pokemonshowdown.com/doublesou-232753081
        if not dealer:
            for search_line in search_lines:
                is_move = Search('|move|', search_line)
                if is_move == 'yes':
                    search_line = search_line.split('|')
                    search_line.pop(0)
                    dealer = search_line[1]
                    name = search_line[2]

        info = [dealer, name, receiver, new_hp]
        
        return(info)
    except Exception as error:
        d=1

def Gather_HP_Info(line, player, nicknames):
    
    """
    this function takes the line fed to it along with the player and nicknames dict and returns the full_name of the mon who's hp was revealed on this line along with the current hp of that mon
    """
    try:
        print('line: '+ str(line))
        print('player: ' + str(player))
        line = line.split('|')
        nickname = line[2]
        #we now directly tie the nickname alone, with the player number, to the 'px: real_mon_name' 
        #value in the dictionary and thus need to drop 'pxy: ' everytime 
        nickname = nickname[5:]
        name = nicknames[player][nickname]
        print('name: ' + str(name))

        #no need to check the first 3 since we know it's '', 'keyword hp trigger', 'name' - this also removes any potential nicknames with \s
        line.pop(0)
        line.pop(0)
        line.pop(0)
        print('newline: ' + str(line))
        for obj in line:
            check_if_dead = Search('fnt', obj)
            if check_if_dead == 'yes':
                cur_hp = 0
            else:
                check_for_hp = obj.split('/')
                if len(check_for_hp) == 2:
                    cur_hp = float(check_for_hp[0])
                    
                    max_hp = check_for_hp[1]
                    max_hp = max_hp.split(' ')
                    max_hp = max_hp[0]
                    max_hp = max_hp.split('\n')
                    max_hp = float(max_hp[0])

                    new_hp = round(((cur_hp / max_hp) * 100), 2)
                    

        return(name, new_hp)
    except Exception as error:
        d=1
        
def Add_To_Damage(static_vals, dmg_info, nicknames, hp):
    
    """
    this function takes the static vals (which are bid, turn, dmgtype, colnames, and table name - which are easily set without needing to parse the log)
    the info related to the dmg (dealer, name, receiver, new_hp), the nicknames, and the current hp tracker dictionary and adds the information to the
    sql table and then returns the updated hp tracker dictionary based on the damage dealt
    
    Also - before sending information to the database we remove single quotes and put in spaces instead as those will mess up the addition to the database and I don't really care
    if you love having a single quote in your name. Sorry not sorry fam. 
    """
    try:
        battle_id = static_vals[0]
        turn_num = static_vals[1]
        dmg_type = static_vals[2]
        col_names = static_vals[3]
        
        name = dmg_info[1]
        name = name.replace("'", ' ')
        if dmg_type == 'status':
            dealer = dmg_info[0]
            dealer = dealer.replace("'", ' ')
        elif dmg_type == 'hazard':
            dealer = dmg_info[0]
            dealer = dealer.replace("'", ' ')
        elif dmg_type == 'passive':
            dealer = dmg_info[0]
            dealer = dealer.replace("'", ' ')
            
        #have to get and convert dealer and receiver names from nickname to original mon name
        else:
            dealer = dmg_info[0]
            if 'p1' in dealer:
                player = 'p1'
            else:
                player = 'p2'
            #we now directly tie the nickname alone, with the player number, to the 'px: real_mon_name' value in the dictionary and thus need to drop 'pxy: ' everytime 
            nickname = dealer[5:]
            dealer = nicknames[player][nickname]
            dealer = dealer.replace("'", ' ')
        receiver = dmg_info[2]
        if 'p1' in receiver:
            player = 'p1'
        else:
            player = 'p2'
        nickname = receiver[5:]
        receiver = nicknames[player][nickname]
        
        new_hp = dmg_info[3]
        cur_hp = hp[receiver]
        hp[receiver] = new_hp
        
        #get rid of single quotes after we've updated the hp dictionary
        receiver = receiver.replace("'", ' ')

        dmg_dealt = float(cur_hp) - float(new_hp)
        
        values = [battle_id, turn_num, dmg_type, dealer, name, receiver, dmg_dealt]
        val_types = ['Text', 'Number', 'Text', 'Text', 'Text', 'Text', 'Number']

        GIS_response = Generate_Insert_Statement(col_names, values, val_types)
        
        return(hp, GIS_response)
    except Exception as error:
        d=1
    
def Gather_Item_or_Ability_Info(line, turn): 
    try: 
        og_line = line
        line = line.split('|')
        line = line[2:]
        receiver = line[0]
        
        if 'fnt' in line[1]:
            new_hp = 0
        else:
            line = line[1].split('/')
            cur_hp = float(line[0])
            
            #because in some cases hp is reflected as raw numbers, we must now check for and remove any status condition labels like psn or brn
            max_hp = line[1]
            max_hp = max_hp.split(' ')
            max_hp = max_hp[0]
            max_hp = max_hp.split('\n')
            max_hp = float(max_hp[0])
            
            new_hp = round(((cur_hp / max_hp) * 100), 2)
        
        line = og_line.split('|')
        line = line[4:]
        line = line[0].split(': ')
        name = line[1]
        
        line = og_line
        #need to check if '[of] ' exists - if it doesn't then the dealer is the same as the receiver (think life-orb)
        is_not_self_inflicted = Search('[of] ', line)
        if is_not_self_inflicted == 'no':
            dealer = receiver
        else:
            line = og_line.split('|')
            line = line[5:]
            line = line[0].split('[of] ')
            line = line[1].split('\n')
            dealer = line[0]
        info = [dealer, name, receiver, new_hp]
        
        return(info)
    except Exception as error:
        d=1

def Gather_Status_or_Hazard_Info(line, turn): 
    try: 
        og_line = line
        line = line.split('|')
        line = line[2:]
        receiver = line[0]
        
        if 'fnt' in line[1]:
            new_hp = 0
        else:
            line = line[1].split('/')
            #because in some cases hp is reflected as raw numbers, we must now check for and remove any status condition labels like psn or brn
            cur_hp = float(line[0])
            
            max_hp = line[1]
            max_hp = max_hp.split(' ')
            max_hp = max_hp[0]
            max_hp = max_hp.split('\n')
            max_hp = float(max_hp[0])
            
            new_hp = round(((cur_hp / max_hp) * 100), 2)

        line = og_line.split('|')
        line = line[4:]
        line = line[0].split('[from] ')
        dealer = line[1]

        name = dealer

        info = [dealer, name, receiver, new_hp]
        
        return(info)
    except Exception as error:
        d=1

def Gather_Passive_Info(line, turn): 
    try:
        og_line = line
        line = line.split('|')
        line = line[2:]
        receiver = line[0]
        
        if 'fnt' in line[1]:
            new_hp = 0
        else:
            line = line[1].split('/')
            #because in some cases hp is reflected as raw numbers, we must now check for and remove any status condition labels like psn or brn
            cur_hp = float(line[0])
            
            max_hp = line[1]
            max_hp = max_hp.split(' ')
            max_hp = max_hp[0]
            max_hp = max_hp.split('\n')
            max_hp = float(max_hp[0])
            
            new_hp = round(((cur_hp / max_hp) * 100), 2)
            
        line = og_line.split('|')
        line = line[4:]
        line = line[0].split('[from] ')
        name = line[1]
        dealer = name

        info = [dealer, name, receiver, new_hp]
        
        return(info)
    except Exception as error:
        d=1

def Add_Damage_Info(dmg_type, battle_id, turn_num, col_names, table_name, line, turn, nicknames, hp):

    try:        
        #prep error table information
        funcname = 'Add_Damage_Info'
        current_step = '0 - begin'
        parameters = 'looking for dmg type = ' + str(dmg_type) + ' in turn number = ' + str(turn_num) + ' and in line = ' + str(line)

        static_vals = [battle_id, turn_num, dmg_type, col_names, table_name]
        if dmg_type == 'item':
            funcname = 'Gather_Item_or_Ability_Info'
            current_step = '1 - look for item dmg_type'

            dmg_info = Gather_Item_or_Ability_Info(line, turn)
            atd_response = Add_To_Damage(static_vals, dmg_info, nicknames, hp)
            hp = atd_response[0]
            dmgsql = atd_response[1]

        elif dmg_type == 'ability':
            funcname = 'Gather_Item_or_Ability_Info'
            current_step = '1 - look for ability dmg_type'

            dmg_info = Gather_Item_or_Ability_Info(line, turn)
            atd_response = Add_To_Damage(static_vals, dmg_info, nicknames, hp)
            hp = atd_response[0]
            dmgsql = atd_response[1]
            
        elif dmg_type == 'hazard':
            funcname = 'Gather_Status_or_Hazard_Info'
            current_step = '1 - look for hazard dmg_type'

            dmg_info = Gather_Status_or_Hazard_Info(line, turn)
            atd_response = Add_To_Damage(static_vals, dmg_info, nicknames, hp)
            hp = atd_response[0]
            dmgsql = atd_response[1]
            
        elif dmg_type == 'status':
            funcname = 'Gather_Status_or_Hazard_Info'
            current_step = '1 - look for status dmg_type'

            dmg_info = Gather_Status_or_Hazard_Info(line, turn)
            atd_response = Add_To_Damage(static_vals, dmg_info, nicknames, hp)
            hp = atd_response[0]
            dmgsql = atd_response[1]
            
        else:
            funcname = 'Gather_Passive_Info'
            current_step = '1 - look for passive dmg_type'

            dmg_info = Gather_Passive_Info(line, turn)
            atd_response = Add_To_Damage(static_vals, dmg_info, nicknames, hp)
            hp = atd_response[0]
            dmgsql = atd_response[1]
        return(hp, dmgsql)
    except Exception as error: 
        usermsg = "Error = Oops! Something went wrong while gathering this battle's damage information! \nThe Beheeyem employed have been notified of the error and will take a look!"
        #if already in errors table then just return the usermsg
        try:
            table_name='errors'
            date_sub = date.today()
            values = [battle_id, date_sub, funcname, current_step, parameters, error]
            val_types = ['Text', 'Date', 'Text', 'Text', 'Text', 'Text']
            col_names = ['Battle_ID', 'Date', 'Func_Name', 'Current_Step', 'Parameters', 'Error_Message']

            error_stmt = Generate_Insert_Statement(col_names, values, val_types)
            Add_sql(table_name, error_stmt)
        except:
            d=1

def Healing_Item_or_Ability_Info(line): 
    try: 
        og_line = line
        line = line.split('|')
        line = line[2:]
        receiver = line[0]
        #first we need to check for if this is a regenerator ability (and thus coming from the switch keyword when the hp upon switch in did not match the previously known hp)
        
        is_regenerator = Search('|switch|', og_line)
        if is_regenerator == 'yes':
            name = 'regenerator'
            
            #regenerator hp is found on the 4th index from og_line, so here, from 3
            line = line[2].split('/')
            cur_hp = float(line[0])
            
            #because in some cases hp is reflected as raw numbers, we must now check for and remove any status condition labels like psn or brn
            max_hp = line[1]
            max_hp = max_hp.split(' ')
            max_hp = max_hp[0]
            max_hp = max_hp.split('\n')
            max_hp = float(max_hp[0])

            new_hp = round(((cur_hp / max_hp) * 100), 2)
            
        else:
            line = og_line.split('|')
            line = line[4:]
            line = line[0].split(': ')
            name = line[1]
            name = name.split('\n')
            name = name[0]
            
            line = og_line.split('|')
            line = line[3]
            line = line.split('/')
            cur_hp = float(line[0])

            #because in some cases hp is reflected as raw numbers, we must now check for and remove any status condition labels like psn or brn
            max_hp = line[1]
            max_hp = max_hp.split(' ')
            max_hp = max_hp[0]
            max_hp = max_hp.split('\n')
            max_hp = float(max_hp[0])

            new_hp = round(((cur_hp / max_hp) * 100), 2)
        
        
        
        info = [name, receiver, new_hp]
        
        return(info)
    except Exception as error:
        d=1

def Healing_Passive_Info(line):
    try: 
        #these have very little information - they are simply an indication that healing occured
        is_silent = Search('silent', line)
        if is_silent == 'yes':
            name = 'silent'
        else:
            find_source = line.split('|')
            find_source = find_source[4]
            find_source = find_source.split('[from] ')
            find_source = find_source[1]
            find_source = find_source.split('\n')
            name = find_source[0]
        
        og_line = line
        line = line.split('|')
        line = line[2:]
        receiver = line[0]
        
        line = line[1].split('/')
        cur_hp = float(line[0])

        #because in some cases hp is reflected as raw numbers, we must now check for and remove any status condition labels like psn or brn
        max_hp = line[1]
        max_hp = max_hp.split(' ')
        max_hp = max_hp[0]
        max_hp = max_hp.split('\n')
        max_hp = float(max_hp[0])

        new_hp = round(((cur_hp / max_hp) * 100), 2)

        info = [name, receiver, new_hp]
        
        return(info)
    except Exception as error:
        d=1

def Healing_Move_Info(line, turn): 
    #this will have 2 forms - a directly healing move like roost or strength sap - or a delayed healing like wish
    #forgot about [from] drain| which happens from moves like giga drain
    try: 
        og_line = line
        line = line.split('|')
        line = line[2:]
        receiver = line[0]
        
        player = receiver[:3]
        
        is_indirect = Search('[from] move: ', og_line)
        if is_indirect == 'yes':
            #used the below to develop this logic
            #|-heal|p1a: Blissey|100/100|[from] move: Wish|[wisher] Blissey
            line = og_line
            find_name = line.split('|')
            find_name = find_name[4]
            find_name = find_name.split(': ')
            name = find_name[1]
        else:
            prev_lines = turn.split(og_line)
            #need to only check what occured before this heal keyword
            prev_lines = prev_lines[0]
            search_lines = prev_lines.split('\n')
            search_lines.reverse()
            
            for search_line in search_lines:
                is_move = Search('|move|', search_line)
                if is_move == 'yes':
                    check_receiver_is_user = search_line.split('|')
                    check_receiver_is_user = check_receiver_is_user[2]
                    is_correct_player = Search(player, check_receiver_is_user)
                    if is_correct_player == 'yes':
                        search_line = search_line.split('|')
                        name = search_line[3]
                        #we have to exit our for loop once we have found the information we desire
                        break
        
        line = og_line
        line = line.split('|')
        line = line[3].split('/')
        cur_hp = float(line[0])

        #because in some cases hp is reflected as raw numbers, we must now check for and remove any status condition labels like psn or brn
        max_hp = line[1]
        max_hp = max_hp.split(' ')
        max_hp = max_hp[0]
        max_hp = max_hp.split('\n')
        max_hp = float(max_hp[0])

        new_hp = round(((cur_hp / max_hp) * 100), 2)

        info = [name, receiver, new_hp]
        
        return(info)
    except Exception as error:
        d=1

def Add_Healing_Info(static_vals, line, turn, nicknames, hp, battle_id):
    try:

        heal_type = static_vals[2]

        #prep error table information
        funcname = 'Add_Healing_Info'
        current_step = '0 - begin'
        parameters = 'looking for heal type = ' + str(heal_type) + ' in turn = ' + str(turn) + ' and in line = ' + str(line)
        
        if heal_type == 'item':
            funcname = 'Healing_Item_or_Ability_Info'
            current_step = '1 - look for heal info for type = item'

            heal_info = Healing_Item_or_Ability_Info(line)
            ath_response = Add_To_Healing(static_vals, heal_info, nicknames, hp)
            hp = ath_response[0]
            healsql = ath_response[1]

        elif heal_type == 'ability':
            funcname = 'Healing_Item_or_Ability_Info'
            current_step = '1 - look for heal info for type = ability'

            heal_info = Healing_Item_or_Ability_Info(line)
            ath_response = Add_To_Healing(static_vals, heal_info, nicknames, hp)
            hp = ath_response[0]
            healsql = ath_response[1]
            
        elif heal_type == 'passive':
            funcname = 'Healing_Passive_Info'
            current_step = '1 - look for heal info for type = passive'

            heal_info = Healing_Passive_Info(line)
            ath_response = Add_To_Healing(static_vals, heal_info, nicknames, hp)
            hp = ath_response[0]
            healsql = ath_response[1]
            
        else:
            funcname = 'Healing_Move_Info'
            current_step = '1 - look for heal info for type = move'

            heal_info = Healing_Move_Info(line, turn)
            ath_response = Add_To_Healing(static_vals, heal_info, nicknames, hp)
            hp = ath_response[0]
            healsql = ath_response[1]

        return([hp, healsql])  
    except Exception as error: 
        usermsg = "Error = Oops! Something went wrong while gathering this battle's healing information! \nThe Beheeyem employed have been notified of the error and will take a look!"
        #if already in errors table then just return the usermsg
        try:
            table_name='errors'
            date_sub = date.today()
            values = [battle_id, date_sub, funcname, current_step, parameters, error]
            val_types = ['Text', 'Date', 'Text', 'Text', 'Text', 'Text']
            col_names = ['Battle_ID', 'Date', 'Func_Name', 'Current_Step', 'Parameters', 'Error_Message']

            error_stmt = Generate_Insert_Statement(col_names, values, val_types)
            Add_sql(table_name, error_stmt)
        except:
            d=1

def Add_To_Healing(static_vals, heal_info, nicknames, hp):
    try: 
        battle_id = static_vals[0]
        turn_num = static_vals[1]
        heal_type = static_vals[2]
        col_names = static_vals[3]
        table_name = static_vals[4]
        
        #prep error table information
        funcname = 'Add_To_Healing'
        current_step = '0 - begin'
        parameters = str(heal_info)

        name = heal_info[0]
        name = name.replace("'", ' ')
        
            
        #have to get and convert dealer and receiver names from nickname to original mon name
        receiver = heal_info[1]
        if 'p1' in receiver:
            player = 'p1'
        else:
            player = 'p2'
        nickname = receiver[5:]
        receiver = nicknames[player][nickname]
        new_hp = heal_info[2]
        cur_hp = hp[receiver]
        hp[receiver] = new_hp
        
        #get rid of single quotes after we've updated the hp dictionary
        receiver = receiver.replace("'", ' ')

        recovery = float(new_hp) - float(cur_hp)

        values = [battle_id, turn_num, heal_type, name, receiver, recovery]
        val_types = ['Text', 'Number', 'Text', 'Text', 'Text', 'Number']

        GIS_response = Generate_Insert_Statement(col_names, values, val_types)
        return(hp, GIS_response)
    except Exception as error: 
        usermsg = "Error = Oops! Something went wrong while adding this battle's healing information! \nThe Beheeyem employed have been notified of the error and will take a look!"
        #if already in errors table then just return the usermsg
        try:
            table_name='errors'
            date_sub = date.today()
            values = [battle_id, date_sub, funcname, current_step, parameters, error]
            val_types = ['Text', 'Date', 'Text', 'Text', 'Text', 'Text']
            col_names = ['Battle_ID', 'Date', 'Func_Name', 'Current_Step', 'Parameters', 'Error_Message']

            error_stmt = Generate_Insert_Statement(col_names, values, val_types)
            Add_sql(table_name, error_stmt)
        except:
            d=1

def Get_Switch_Info(response, nicknames):
    try:
        switchsql = []
        col_names = ['Battle_ID', 'Turn', 'Player', 'Pokemon_Enter' , 'Source']
        table_name = 'switch'
        
        battle_id = response['id']
        p1 = response['p1id']
        p2 = response['p2id']
        log = response['log']
        
        #prep error table information
        funcname = 'Get_Switch_Info'
        current_step = '0 - begin'
        parameters = ''

        #now I need to split the log into turns and remove the intro information
        
        turns = log.split('|start\n')
        turns = turns[1].split('|turn|')
        i = -1
        for turn in turns:
            i = i + 1
            lines = turn.split('\n')
            turn_num = i
            for line in lines:
                parameters = line
                funcname = 'Get_Switch_Info'
                #we need to ignore any line that begins with '|c|' since these are spectator or player chat messages
                if not '|c|' in line:
                    is_switch = Search('|switch|', line)
                    if is_switch == 'yes':
                        is_move = Search('[from]move: ', line)
                        
                        get_player = line.split('|')
                        get_player = get_player[2]
                        player = get_player[:2]
                        if player == 'p1':
                            player_name = p1
                        else:
                            player_name = p2

                        get_mon = line.split('|')
                        get_mon = get_mon[2]
                        get_mon = get_mon.split(': ')
                        get_mon = get_mon[1]
                        nickname_mon = get_mon
                        
                        real_name_mon = nicknames[player][nickname_mon]
                            
                        if is_move == 'yes':
                            get_move = line.split('|')
                            get_move = get_move[5]
                            get_move = get_move.split(': ')
                            get_move = get_move[1]
                            get_move = get_move.split('\n')
                            source = get_move[0]
                            
                            values = [battle_id, turn_num, player_name, real_name_mon, source]
                            val_types = ['Text', 'Number', 'Text', 'Text', 'Text']

                            funcname = 'Generate_Insert_Statement'
                            current_step = '1 - generate insert information for move switch'

                            GIS_response = Generate_Insert_Statement(col_names, values, val_types)

                            switchsql.append(GIS_response)
                        else:
                            #note, this will count even eject button / eject pack as an action but it is reported literally identically to a hard swap action
                            #perhaps in the future I can go back and add that information but for now, I won't worry about it
                            source = 'action'
                            
                            funcname = 'Generate_Insert_Statement'
                            current_step = '1 - generate insert information for hard switch'

                            values = [battle_id, turn_num, player_name, real_name_mon, source]
                            val_types = ['Text', 'Number', 'Text', 'Text', 'Text']

                            GIS_response = Generate_Insert_Statement(col_names, values, val_types)
                            switchsql.append(GIS_response)
        
        switchinfo = {}
        switchinfo[table_name] = switchsql
        return([1, switchinfo])

    except Exception as error:
        usermsg = "Error = Oops! Something went wrong while gathering this battle's mon switching information! \nThe Beheeyem employed have been notified of the error and will take a look!"
        #if already in errors table then just return the usermsg
        try:
            table_name='errors'
            date_sub = date.today()
            values = [battle_id, date_sub, funcname, current_step, parameters, error]
            val_types = ['Text', 'Date', 'Text', 'Text', 'Text', 'Text']
            col_names = ['Battle_ID', 'Date', 'Func_Name', 'Current_Step', 'Parameters', 'Error_Message']

            error_stmt = Generate_Insert_Statement(col_names, values, val_types)
            Add_sql(table_name, error_stmt)

            return(0, usermsg)
        except:
            return(0, usermsg)

def Get_Action_Info(response):
    try:
        actionsql = []
        col_names = ['Battle_ID', 'Turn', 'Player', 'Action']
        table_name = 'actions'
        
        battle_id = response['id']
        p1 = response['p1id']
        p2 = response['p2id']
        log = response['log']
        
        #prep error table information
        funcname = 'Get_Action_Info'
        current_step = '0 - begin'
        parameters = ''
        #now I need to split the log into turns and remove the intro information
        
        turns = log.split('|start\n')
        turns = turns[1].split('|turn|')
        
        i = -1
        for turn in turns:
            #We need i and turn num to be offset here which is why we increment i after turn num
            #for some reason I wrote it so that you add the previous turn's info first, 
            #then you prep the next turns information, which is why turn num and i must be offset
            turn_num = i
            i = i + 1
            funcname = 'Get_Action_Info'
            #on all post-start turns we want to write an insert statement to the database with each 
            #player's action for that turn
            if i != 0:
                for player in list(turn_dict):
                    player_num = player[:2]
                    if player_num == 'p1':
                        player_name = p1
                    else:
                        player_name = p2
                    action = turn_dict[player]

                    funcname = 'Generate_Insert_Statement'
                    current_step = "1 - add previous turn's info"
                    
                    values = [battle_id, turn_num, player_name, action]
                    val_types = ['Text', 'Number', 'Text', 'Text']
                    GIS_response = Generate_Insert_Statement(col_names, values, val_types)
                    actionsql.append(GIS_response)
            #want to ignore anything after 'upkeep' as players who sack pokemon switch after that
            turn = turn.split('|upkeep')
            turn = turn[0]
            lines = turn.split('\n')
            #by reversing the lines, we can ensure that the final dictionary value 
            #will be what was the players first action that turn - either switch or move
            #which is what I am after in this table
            lines.reverse()
            #empty the turn_dict in order to get the new turn's information
            turn_dict = {}
            for line in lines:
                funcname = 'Get_Action_Info'
                current_step = "2 - begin working backwards through lines and prep this turn's info"
                parameters = line
                #we need to ignore any line that begins with '|c|'
                if not '|c|' in line:  
                    line = line.split('|upkeep')
                    line = line[0]
                    is_switch = Search('|switch|', line)
                    is_move = Search('|move|', line)
                    
                    if is_switch == 'yes':
                        get_player = line.split('|')
                        get_player = get_player[2]
                        player = get_player[:3]
                        action = 'switch'
                        turn_dict[player] = action
                    if is_move == 'yes':
                        get_player = line.split('|')
                        get_player = get_player[2]
                        player = get_player[:3]
                        action = 'move'
                        turn_dict[player] = action    
        
        actioninfo = {}
        actioninfo[table_name] = actionsql
        return(1, actioninfo)     
    except Exception as error:
        usermsg = "Error = Oops! Something went wrong while gathering this battle's player action information! \nThe Beheeyem employed have been notified of the error and will take a look!"
        #if already in errors table then just return the usermsg
        try:
            table_name='errors'
            date_sub = date.today()
            values = [battle_id, date_sub, funcname, current_step, parameters, error]
            val_types = ['Text', 'Date', 'Text', 'Text', 'Text', 'Text']
            col_names = ['Battle_ID', 'Date', 'Func_Name', 'Current_Step', 'Parameters', 'Error_Message']

            error_stmt = Generate_Insert_Statement(col_names, values, val_types)
            Add_sql(table_name, error_stmt)

            return(0, usermsg)
        except:
            return(0, usermsg)