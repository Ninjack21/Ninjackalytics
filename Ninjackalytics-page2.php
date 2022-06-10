<!DOCTYPE html>
    <head><link rel="stylesheet" 
        href="Ninjackalytics.css">
    </head>
    <body>
        <ul>
            <li><a>Home</a></li>
            <li><a href="Ninjackalytics.html">Submit Replay</a></li>
            <li><a>Coming Soon: Meta Stats</a></li>
            <li><a>Coming Soon: Team Build Assist</a></li>
            <li><a>Coming Soon: Scout Opponent</a></li>
        </ul>
        <?php
        echo shell_exec("python Ninjackalytics_Functions.py")
        ?>
    </body>