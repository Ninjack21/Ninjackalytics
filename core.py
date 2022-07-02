import functools

from flask import (
    Blueprint, redirect, render_template, url_for, request
)

from . import Ninjackalytics_Stat_Queries as nsq
from . import Ninjackalytics_Functions as nf



bp = Blueprint('core', __name__, url_prefix='/core')

@bp.route('/submit', methods = ('POST', 'GET'))
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
    core_info = nsq.Core_Info(bid)
    
    # FINISH THIS ONE LATER - EASILY THE HARDEST

@bp.route('/generalerror')
def generalerror():
    return render_template('core/generalerror.html')