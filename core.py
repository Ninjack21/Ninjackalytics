from io import BytesIO
import matplotlib.pyplot as plt
import base64
from flask import (
    Blueprint, redirect, render_template, url_for, request
)
from . import Ninjackalytics_Stat_Queries as nsq
from . import Ninjackalytics_Functions as nf
import psycopg2 as pps

bp = Blueprint('core', __name__)


@bp.route('/', methods = ('POST', 'GET'))
def submit():
    #if the user is submitting their battle url then use run_ninjackalytics
    if request.method == 'POST':
        url = request.form['url']

        try:
            redirect_response = nf.Run_Ninjackalytics(url)
            #if we got an error then redirect to url_for error page with message after 'Error = '
            if 'Error' in redirect_response:
                #we can get the more specific error here later on, but for now we'll use a general error message
                errormsg = redirect_response[8:]
                return redirect(url_for('core.error'))
            #if there is no error, then we redirect to the stats page
            else:
                return redirect(url_for('core.battlestats', bid = redirect_response))
        except: 
            return redirect(url_for('core.error'))

    return render_template('core/submit.html')

@bp.route('/error', methods = ('GET',))
def error():
    # color palette: #FE0180, #0101FE, #01FE80, #FEFE01

    return render_template('core/error.html')

@bp.route('/battlestats/<bid>', methods=('GET',))
def battlestats(bid):
    # prepare the basic information and the graphs variable to be passed to the battlestats.html
    #establish a connection that we will ultimately close at the end
    conn = pps.connect(host = 'ec2-44-196-174-238.compute-1.amazonaws.com', database = 'd39sfuos9nk0v3', user = 'geodgxbrnykumu', password = '6f97a508f497d1a7354e4e82791772b0837c4e66ca361090483e96fdce55e4c8')
    cur = conn.cursor()
    try:
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

    finally:
        cur.close()
        conn.close()
