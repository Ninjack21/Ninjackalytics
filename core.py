from io import BytesIO
import matplotlib.pyplot as plt
import base64
from flask import (
    Blueprint, redirect, render_template, url_for, request, flash
)
import Ninjackalytics_Stat_Queries as nsq
import Ninjackalytics_Functions as nf



bp = Blueprint('core', __name__)


@bp.route('/', methods = ('POST', 'GET'))
def submit():
    #if the user is submitting their battle url then use run_ninjackalytics
    if request.method == 'POST':
        url = request.form['url']

        try:
            redirect_response = nf.Run_Ninjackalytics(url)
            #if we got an error then redirect to url_for error page with message after 'Error = '
            if 'Error' in str(redirect_response):
                #we can get the more specific error here later on, but for now we'll use a general error message
                errormsg = redirect_response[8:]
                errormsg = errormsg.split('\n')
                #add the error messages to flash
                #iterate through for number of lines in error msg
                for msg in enumerate(errormsg):
                    flash(msg[1])
                return redirect(url_for('core.specificerror'))
            #if there is no error, then we redirect to the stats page
            else:
                return redirect(url_for('core.battlestats', bid = redirect_response))
        except Exception as msg: 
            flash(str(msg))
            return redirect(url_for('core.generalerror'))

    return render_template('core/submit.html')

@bp.route('/error', methods = ('GET',))
def specificerror():
    # color palette: #FE0180, #0101FE, #01FE80, #FEFE01

    return render_template('core/specificerror.html')

@bp.route('/generalerror', methods = ('GET',))
def generalerror():

    return render_template('core/generalerror.html')


@bp.route('/battlestats/<bid>', methods=('GET',))
def battlestats(bid):

    core_info = nsq.Core_Info(bid)
    pnums = ['P1', 'P2']
    graphs = {}
    totals = {}
    #generate the plots for this battle
    for player in pnums:
        #https://www.pythonanywhere.com/forums/topic/5017/
        healentr = nsq.Healing_Per_Entrance(bid, player, core_info)
        nsq.Generate_Bar_Chart(healentr)
        figfile = BytesIO()
        plt.savefig(figfile, format='png', transparent=True, bbox_inches='tight')
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue()).decode('ascii')
        graphs[str(player) + ' - Healing Per Entrance'] = figdata_png

        dmgentr = nsq.Damage_Per_Entrance(bid, player, core_info)
        nsq.Generate_Bar_Chart(dmgentr)
        figfile = BytesIO()
        plt.savefig(figfile, format='png', transparent=True, bbox_inches='tight')
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue()).decode('ascii')
        graphs[str(player) + ' - Dmg Per Entrance'] = figdata_png

        turnact = nsq.Turn_Action_Breakdown(bid, player, core_info)
        #sum up the number of turns in this battle for this player
        totalturns=0
        for i in turnact.values():
            if i != '# of Turns Action Selected':
                totalturns += int(i)
        totals[str(player) + ' - Total Turns'] = totalturns

        nsq.Generate_Bar_Chart(turnact)
        figfile = BytesIO()
        plt.savefig(figfile, format='png', transparent=True, bbox_inches='tight')
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue()).decode('ascii')
        graphs[str(player) + ' - Turn Action Breakdown'] = figdata_png
        

        healtype = nsq.Heal_Type_Breakdown(bid, player, core_info)
        totals[str(player) + ' - Total Healing Heal Type Breakdown'] = round(healtype['Total'],2)

        nsq.Generate_Bar_Chart(healtype)
        figfile = BytesIO()
        plt.savefig(figfile, format='png', transparent=True, bbox_inches='tight')
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue()).decode('ascii')
        graphs[str(player) + ' - Heal Type Breakdown'] = figdata_png
        

        healbrkdwn = nsq.Healing_Breakdown(bid, player, core_info)
        totals[str(player) + ' - Total Healing Breakdown'] = round(healbrkdwn['Total'],2)
        nsq.Generate_Bar_Chart(healbrkdwn)
        figfile = BytesIO()
        plt.savefig(figfile, format='png', transparent=True, bbox_inches='tight')
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue()).decode('ascii')
        graphs[str(player) + ' - Healing Breakdown'] = figdata_png
        

        dmgtype = nsq.Dmg_Type_Breakdown(bid, player, core_info)
        totals[str(player) + ' - Total Dmg Type Breakdown'] = round(dmgtype['Total'],2)

        nsq.Generate_Bar_Chart(dmgtype)
        figfile = BytesIO()
        plt.savefig(figfile, format='png', transparent=True, bbox_inches='tight')
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue()).decode('ascii')
        graphs[str(player) + ' - Dmg Type Breakdown'] = figdata_png
        

        dmgrecbrkdwn = nsq.Dmg_Received_Breakdown(bid, player, core_info)
        totals[str(player) + ' - Total Dmg Received Breakdown'] = round(dmgrecbrkdwn['Total'],2)

        nsq.Generate_Bar_Chart(dmgrecbrkdwn)
        figfile = BytesIO()
        plt.savefig(figfile, format='png', transparent=True, bbox_inches='tight')
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue()).decode('ascii')
        graphs[str(player) + ' - Dmg Received Breakdown'] = figdata_png
        
        dmgdealtbrkdwn = nsq.Dmg_Dealt_Breakdown(bid, player, core_info)
        totals[str(player) + ' - Total Dmg Dealt Breakdown'] = round(dmgdealtbrkdwn['Total'],2)
        
        nsq.Generate_Bar_Chart(dmgdealtbrkdwn)
        figfile = BytesIO()
        plt.savefig(figfile, format='png', transparent=True, bbox_inches='tight')
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue()).decode('ascii')
        graphs[str(player) + ' - Dmg Dealt Breakdown'] = figdata_png
    
    return render_template('core/battlestats.html', graphs=graphs, core_info=core_info, bid=bid, totals = totals)