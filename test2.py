from mcsmapi import MCSMAPI
mcsm = MCSMAPI("https://verweij.site:23333")
mcsm.login_with_apikey("1a09d7a8a0b141aba376be08cccc38f2")
overview = mcsm.overview()