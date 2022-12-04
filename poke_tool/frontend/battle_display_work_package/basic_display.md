# Guide for Implementing the Battle Dispaly Page
## Packages to Learn:
1. Dash: https://dash.plotly.com
    * There are no examples of this in code currently
    * This will be the main part of the ask - creating a basic Dash display which I will provide an overview sketch of later in this documentation.
2. Pandas: https://pandas.pydata.org/docs/#
    * **Go To**: *frontend/battle_display.py* to see an example. Anything preprended with "pd" is a pandas function.
        * The above example has not yet been tested and may well break or not provide data as expected. If so:
            1. Try to workout the error - it is probably ~90% correct already so I think you'll be close
            2. Don't waste too much time trying to fix tho - if you have an error and it isn't obvious what to do after a few tries, please reach out :)
3. SQLAlchemy: https://docs.sqlalchemy.org/en/14/
    * **Go To:** *frontend/battle_display.py* yet again for an example. I used SQLAlchemy to create a "session" which I use to connect to the database. 
    * **For Example of Writing TO a database:** *battle_analyzer/pivots/Gather_Switch_Info.py*
        * Note: this won't be needed for the ask - I only put it in case you were interested in seeing one. 
4. Postgresql: https://www.postgresql.org/
    * You will need to download postgresql for your local computer for testing. Once you get it, do the following to set it up:
        1. Try running "run.py" in the top level folder ("Poke_Tool")
        2. work through any errors that show up. I think there are a few things you typically have to do related to setting up "Path" environments. Look up a youtube video or stackoverflow to try to solve the issue
        3. Try repeat 1-2 until run.py succesfully completes. You should see a series of messages print about deleting database tables and re-establishing (I forget exact wording and message I wrote).
        4. If you get stuck - again - do not hesitate to reach out. I'm happy to work through any issues with you. I promise you - I broke this thing 1,000,000 times already. I won't judge ;). Heck, I still break it constantly. 