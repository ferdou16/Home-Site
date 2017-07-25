activate_this = '/var/www/.virtualenvs/homesite/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
import sys
sys.stdout = sys.stderr 
sys.path.append('/var/www/homesite')
 
from mcss import app as application
