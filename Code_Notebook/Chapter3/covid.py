# 新增
import pygmt  #注意：将pygmt写在最前面，避免出现不必要的问题
import linecache

import pandas as pd
import numpy as np
from matplotlib.ticker import MultipleLocator
import matplotlib as mpl
mpl.rcParams["font.family"] = 'Arial'  #默认字体类型
mpl.rcParams["mathtext.fontset"] = 'cm' #数学文字字体
mpl.rcParams["contour.negative_linestyle"] = 'dashed'  #默认字体类型
import matplotlib.pyplot as plt
import os
from netCDF4 import Dataset

# 读取国家代码，e.g. 中国=CN
countries_name_code=pd.read_csv('Data/COVID-19/Data/countryCode.csv')
keys=countries_name_code.keys()
countries=countries_name_code['国家或地区'].values
codes=countries_name_code['国际域名缩写'].values
code_countries={}
for name, code in zip(countries,codes):
    code_countries[name]=code

figpath='../../figures/Chapter3/covid_global'

def plot_global_top_barh(figpath,date,confirms,deaths,recovers,names,dpi,top=10):
    ind=np.argsort(confirms)
    confirms,deaths,recovers,names=confirms[ind],deaths[ind],recovers[ind],names[ind]
    confirms_plot,deaths_plot,recovers_plot,names_plot=confirms[-top:],deaths[-top:],recovers[-top:],names[-top:]

    zhfont=mpl.font_manager.FontProperties(fname="/System/Library/Fonts/Supplemental/Songti.ttc")
    barheight=0.3
    fig=plt.figure()
    ax=plt.gca()
    # ax.text(0.5,0.5,'多金属',fontproperties= zhfont)
    x=np.linspace(0,len(confirms_plot),len(confirms_plot))
    ax.barh(x-barheight,confirms_plot,height=barheight,color='red',label='Confirmed')
    ax.barh(x,recovers_plot,height=barheight,color=(42/255,215/255,91/255),label='Recovered')
    ax.barh(x+barheight,deaths_plot,height=barheight,color='gray',label='Deaths')
    ax.legend(loc='lower right',frameon=False)
    ax.set_title('Global top 10')
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_ticks(x)
    ax.yaxis.set_ticklabels(names_plot,fontproperties= zhfont)
    ax.set_ylim(-0.5,np.max(x)+0.5)
    max_confirm=np.max(confirms_plot)
    if(max_confirm<1000):
        ax.set_xlim(0,1000*1.05)
    elif(max_confirm<1E4):
        ax.set_xlim(0,1E4*1.05)
    elif(max_confirm<1E5):
        ax.set_xlim(0,1E5*1.05)
    elif(max_confirm<1E6):
        ax.set_xlim(0,1E6*1.05)
    elif(max_confirm<5E6):
        ax.set_xlim(0,5E6*1.05)
    elif(max_confirm<8E6):
        ax.set_xlim(0,8E6*1.05)
    elif(max_confirm<1E7):
        ax.set_xlim(0,1E7*1.05)
    else:
        ax.set_xlim(0,np.max(confirms)*1.05)
    xticks=ax.get_xticks()
    # 替换xtick labels
    xticklabels=[]
    for tick in xticks:
        if(tick<1000):
            xticklabels.append(str('%.0f'%(tick)))
        elif((tick>=1000) & (tick<10000)):
            xticklabels.append(str('%.0f千'%(tick/1000)))
        elif((tick>=10000) & (tick<100000)):
            xticklabels.append(str('%.0f万'%(tick/10000)))
        elif((tick>=1000000) & (tick<10000000)):
            xticklabels.append(str('%.0f百万'%(tick/1000000)))
        elif((tick>=10000000) & (tick<100000000)):
            xticklabels.append(str('%.0f千万'%(tick/10000000)))
        else:
            xticklabels.append(str('%.0f'%(tick)))
    ax.xaxis.set_ticklabels(xticklabels,fontproperties= zhfont)
    plt.tight_layout(pad=0.1)
    figname=str('%s/%s.png'%(figpath,date))
    plt.savefig(figname,dpi=400,transparent=True)
    return figname
def plot_map_global_covid(date,csvfile,ind_proj=1,dpi=600):
    data_covid=pd.read_csv(csvfile)
    keys_covid=data_covid.columns
    #print(keys_covid)
    countries_covid={}
    names=data_covid[keys_covid[1]].values
    data_covid=data_covid.replace({keys_covid[2]:' -',keys_covid[3]:' -',keys_covid[4]:' -'},0)
    data_covid=data_covid.replace({keys_covid[2]:' ',keys_covid[3]:' ',keys_covid[4]:' '},0)
    #print(date,data_covid[keys_covid[4]].values)
    confirms=np.array(data_covid[keys_covid[2]].values,dtype=float)
    deaths=np.array(data_covid[keys_covid[3]].values,dtype=float)
    recovers=np.array(data_covid[keys_covid[4]].values,dtype=float)
    
    max_confirm,max_death=np.max(confirms),np.max(deaths)
    for name, confirm,death,recover in zip(names,confirms ,deaths,recovers):
        countries_covid[name.replace(' ','')]={'confirm':confirm,'death':death,'recover':recover}
    country_names_covid=countries_covid.keys()
    # 根据确诊人数归一化颜色
    norm = mpl.colors.Normalize(vmin=np.log10(np.min(confirms+0.9)), vmax=np.log10(np.max(confirms)))
    # write cpt file
    color_nodes=np.linspace(norm.vmin,norm.vmax,20)
    fpout=open('covid_global.cpt','w')
    for i in range(0,len(color_nodes)-1):
        value1=color_nodes[i]
        value2=color_nodes[i+1]
        rgb1=mpl.cm.YlOrRd(norm(value1),bytes=True) 
        rgb2=mpl.cm.YlOrRd(norm(value2),bytes=True) 
        fpout.write('%f %.0f/%.0f/%.0f %f %.0f/%.0f/%.0f\n'%(value1, rgb1[0],rgb1[1],rgb1[2],value2, rgb2[0],rgb2[1],rgb2[2]))
    fpout.close()
    # 绘图
    projections_name=['Hammer','Mollweide','Winkel Tripel','Robinson','Eckert IV','Eckert VI',
                      'Sinusoidal','Van der Grinten','Hemisphere','Orthographic','Gnomonic','Cylindrical equidistant']
    projections=['H','W','R','N','Kf','Ks','I','V','A280/30/','G-75/41/','F-120/35/60/','Q']
    proj=projections[ind_proj]
    proj_name=projections_name[ind_proj]
    fig = pygmt.Figure()
    pygmt.config(MAP_GRID_PEN_PRIMARY="0.25p,black",
             FORMAT_GEO_MAP="ddd:mm:ssF MAP_FRAME_PEN thin,white ",
             FONT_ANNOT_PRIMARY="7p",
             FONT_TITLE="11p,Helvetica,black",MAP_TITLE_OFFSET='-8p',
             FONT_LABEL="8p,Helvetica",
             MAP_LABEL_OFFSET="4p")
    # Make a global Mollweide map with automatic ticks
    fig.basemap(region="g", projection=proj+'0/16c',B=str('+t"%s"'%(date)))
    # Plot the land as light gray
    fig.coast(borders=['1/0.01p,black@50'],shorelines=['1/0.01p,black@100'],water='lightblue',land='gray')
    # plot confirm data for each country or region
    for country in country_names_covid:
        if(not (country in countries)):
            continue
        confirm=countries_covid[country]['confirm']
        code=code_countries[country]
        if(confirm<=0):
            continue
        rgba_color = mpl.cm.YlOrRd(norm(np.log10(confirm)),bytes=True) 
        if(code==' '):
            continue
        fig.coast(E=str('%s+p0.01p,black@50+g%.0f/%.0f/%.0f'%(code,rgba_color[0],rgba_color[1],rgba_color[2])))

    with pygmt.config(MAP_FRAME_PEN="1p"):
        fig.colorbar(D='jCB+w6c/0.2c+o0.2c/0c+h',cmap='covid_global.cpt',frame='a1f0.1+l"Covid-19 confirm(log10)"',F='+gwhite@90',B='y+l"ds"')
    # plot bar using mpl
    imagename=plot_global_top_barh(figpath,date,confirms,deaths,recovers,names,dpi)
    fig.image(imagename,D='x0c/0c+w5c')
    figname=str('%s/%s_%s.png'%(figpath,proj_name.replace(' ','_'),date))
    fig.savefig(figname,show=False,dpi=dpi)
    fig.savefig(str('%s/%s_%s.pdf'%(figpath,proj_name.replace(' ','_'),date)),show=False)
    #fig.show()
    plt.close()
    return figname,[names, confirms,deaths,recovers]
# # 读取COVID-19数据
# date='2020-08-27'
# figname,data=plot_map_global_covid(date,dpi=800)
import datetime
date_start=datetime.date(2020,1,22)
date_end=datetime.date(2020,9,13)
days=(date_end-date_start).days
fignames=[]
for i in range(0,days):
    date=str(date_start+datetime.timedelta(days=i))
    csvfile='Data/COVID-19/Data/Global_Chinese/'+date+'.csv'
    if(not os.path.exists(csvfile)):
        continue
    print(date)
    figname,data=plot_map_global_covid(date,csvfile,dpi=800)
    fignames.append(figname)
# make gif
cmd='convert -delay 40 '
for figname in fignames:
    cmd+=figname+' '
cmd+=figpath+'/covid_global.gif'
os.system(cmd)