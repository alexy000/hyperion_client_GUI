"""

        "leds" : 
	[
		{
			"index" : 0,
			"hscan" : { "minimum" : 0.9375, "maximum" : 1.0000 },
			"vscan" : { "minimum" : 0.0000, "maximum" : 0.0625 }
		},
"""

import numpy as np

hlednum = 16
vlednum = 16
#hmin = 0.0000
#hmax = 1.0000
#vmin = 0.0000
#vmax = 1.0000


hrange = list(np.linspace(0, 1, hlednum+1))
vrange = list(np.linspace(0, 1, vlednum+1))


print(hrange, vrange)
jstring = """
    "leds" : 
    ["""
i = 0

if vlednum == 0:
    vmin = 0.9000
    vmax = 1.0000
    for h in range(hlednum):
        hmin = hrange[h]
        hmax = hrange[h] + hrange[1]
        jstring += """
        {
            "index" : """+str(i)+""",
            "hscan" : { "minimum" : """+str("{0:.4f}".format(hmin))+""", "maximum" : """+str("{0:.4f}".format(hmax))+""" },
            "vscan" : { "minimum" : """+str("{0:.4f}".format(vmin))+""", "maximum" : """+str("{0:.4f}".format(vmax))+""" }
        },"""
        i += 1
else:    
    for v in range(vlednum):
        vmin = vrange[v]
        vmax = vrange[v] + vrange[1]
        for h in range(hlednum):
            if (v % 2) == 0:
                hrange.reverse()
                hmin = hrange[h] - hrange[-2]
                hmax = hrange[h]
                jstring += """
            {
                "index" : """+str(i)+""",
                "hscan" : { "minimum" : """+str("{0:.4f}".format(hmin))+""", "maximum" : """+str("{0:.4f}".format(hmax))+""" },
                "vscan" : { "minimum" : """+str("{0:.4f}".format(vmin))+""", "maximum" : """+str("{0:.4f}".format(vmax))+""" }
            },"""
                i += 1
                hrange.reverse()
            else:
                hmin = hrange[h]
                hmax = hrange[h] + hrange[1]
                jstring += """
            {
                "index" : """+str(i)+""",
                "hscan" : { "minimum" : """+str("{0:.4f}".format(hmin))+""", "maximum" : """+str("{0:.4f}".format(hmax))+""" },
                "vscan" : { "minimum" : """+str("{0:.4f}".format(vmin))+""", "maximum" : """+str("{0:.4f}".format(vmax))+""" }
            },"""
                i += 1
            

#jstring = unicode(jstring, "utf-8")        
print(jstring)

f= open("16x16_matrix.txt","w+")
f.write(jstring)
f.close()
