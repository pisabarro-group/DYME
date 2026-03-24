#!/dyme_env/anaconda/envs/dyme_main/bin/python

import sys

sys.path.insert(0, "/dyme_base/backend/dyme/api")
from dyme_api import app as application
#logging.basicConfig(stream=sys.stderr) 
