'''
analysis data for scale calibrations
'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def date_from_fname(fname):
    date = fname[0:8]
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]
    return {'year':year,'month':month,'day':day,'int_date':date}

def polystr(coeffs,ystr,xstr,digits = 3):
    string = "$"+ ystr + " = "
    n = len(coeffs)
    for c in coeffs:
        n+=-1
        val = '{:.2e}'.format(np.abs(c))
        val = val.replace('e','e^{')
        val+='}'
        if c < 0: sign = '-'
        else:  sign = '+'
        string += sign +val+xstr+"^{"+str(n)+"}"
    string+='$'
    return string
        

def delta_uncertainty(ref_std,stds):
    delta_std = np.zeros(len(stds),float)
    i = 0
    for s in stds:
        delta_std[i] = np.abs(ref_std) + np.abs(stds[i])
        i+=1
    return delta_std
        

#%% Analysis Parameters
data_dir = r"basement_whiteanalog_data"

#title from directory name
title = data_dir.replace('_data', '')
title = title.replace('_',' ')

#assumptions about reference weight error
max_err_ref = .5
min_err_ref = -.5
ref_uncert = np.sqrt((max_err_ref - min_err_ref)**2/12); #assuming that the plates are accuract to plus minus a lb

#fit degree
fit_degree = 2

#%% House Keepingn
plt.close('all')
#%% Math 
#correction factor = gam
#w_real = gam*w_meass
#gam = w_real/w_meas

#bias correction
#w_real  = Delta + W
#Delta = w_real - w_meas

#uncertainty in delta
#meas funn
#Delta = w_real - w_meas
#dDelta/d_real = 1
#dDelta/d_meas = -1


#uncertainty function
#dW

#%% read data 
fig_corr,ax_corr = plt.subplots(1,1,figsize = (8,7))
ax_corr.set_xlabel(r'Measured Weight (lbs)')
ax_corr.set_ylabel(r'Correction Factor ($\Delta$)')
ax_corr.set_title(title+r'Correction factor ($W = W_{measured} + \Delta)$')

for filename in os.listdir(data_dir):
     if '.csv' in filename:
         #read data
         df = pd.read_csv(data_dir+r"\\"+filename,index_col = 'measurement')
         refs = df.loc['ref']
         df = df.drop('ref')
         means = df.mean()
         stds = df.std()
         
         #get correction
         delta = refs.to_numpy() - means.to_numpy()
         
         #get uncertainty
         delta_std = delta_uncertainty(ref_uncert,stds.to_numpy())
         
         #fit delta to polynomial
         fit = np.polyfit(means.to_numpy(),delta,fit_degree)
         xfit = np.linspace(0,max(means.to_numpy()))
         yfit = np.polyval(fit,xfit)
         fit_str = polystr(fit,'\Delta','w_{meas}',fit_degree)
         
         #get date
         date = date_from_fname(filename)
         
         #prit correction for 150 - 210 lb range
         xeasy = np.linspace(150,210,100)
         easy = np.mean(np.polyval(fit,xeasy))
         easy  = np.round(easy,2)
         print('Mean Delta for 150-210lb range: ',easy, ' lbs')
         
         #plot data
         ax_corr.errorbar(means,delta,
                          yerr = delta_std,
                          linestyle = '',
                          capsize= 5,
                          marker = 'o')
         ax_corr.plot(xfit,yfit,'r-',label = 'fit: '+fit_str)
         
       

ax_corr.legend(loc = 'best')
ax_corr.grid()
         
#save figure
fig_corr.savefig(data_dir+r"\\plots\\correction_factor.png")