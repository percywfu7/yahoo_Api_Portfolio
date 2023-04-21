import numpy as np
import pandas as pd
from datetime import date
from datetime import datetime
import yfinance as yf
from pandas_finance import Equity
from datetime import timedelta
inception= date(2020,6,30)
today = date(2020,11,16)


# reading the holdings positions and cash for the periods
i=0

#in the next two lines I am reading my local portfolio holding information. you can add your personal path there or an any api to read similar information
df_position= pd.read_csv(r'***ADD YOUR HOLDINGS DATA HERE')
df_cash= pd.read_csv(r'ADD YOUR CASH HOLDINGS HERE ')


#removing the US bit from ticker segment

df_position['ticker'] = df_position['ticker'].str.rstrip('US')

df_info=pd.DataFrame()

df_info['ticker']= df_position['ticker']
df_info['name']= df_position['name']
df_info['sector']= df_position['sector']
#pivoting the position twice to convert date
df_positiondates = df_position.iloc[:,2:]
df_pp= df_positiondates.pivot_table( columns='ticker')

df_pp['date']= df_pp.index
df_pp['date'] =pd.to_datetime(df_pp.date)
df_pp= df_pp.sort_values(by='date')


df_pp['date']= df_pp['date'].dt.to_pydatetime()
df_pp['date']= df_pp['date'].dt.date
# datetime.fromtimestamp(timestamp).strftime('%d-%m-%y')
df_p=df_pp.pivot_table( columns='date')


#pivoting the cash twice to convert date
df_cc=df_cash.pivot_table( columns='name')
df_cc['date']= df_cc.index
df_cc['date'] =pd.to_datetime(df_cc.date)
df_cc= df_cc.sort_values(by='date')
df_cc['date']= df_cc['date'].dt.to_pydatetime()
df_cc['date']= df_cc['date'].dt.date

df_c=df_cc.pivot_table( columns='date')



# Getting and restrucuring sp 500 data
sp=pd.DataFrame()
sp = yf.download("^GSPC" ,start=inception,end=date(2020,11,18))
sp['date'] = sp.index
sp['date']= sp['date'].dt.to_pydatetime()
sp['date']= sp['date'].dt.date
sp_final = pd.DataFrame()
sp_final['Close']= sp['Close']
sp_final['date']= sp['date']
sp_final=sp_final.pivot_table(columns='date', values='Close')


#reading stock price data
df=pd.DataFrame()
for Security in df_info['ticker']:
    df_1= yf.download(Security ,start=inception,end=date(2020,11,18))
    df_1['date'] = df_1.index
    df_1['ticker']= Security
    df=df.append(df_1, ignore_index=True)
    i=i+1
    print(Security)
    print(i)



df_close= df[['Close','ticker', 'date']].copy()
df_close['date']= df_close['date'].dt.to_pydatetime()
df_close['date']= df_close['date'].dt.date

df_final = df_close.pivot_table(index='ticker', columns='date', values='Close')

df_final['ticker'] = df_final.index

df_pr= df_final
df_p['ticker']= df_p.index
df_p=df_p.fillna(0)


#performance for a time period--------------------------------------------------------------
#defining the data frames required
df_info.index=df_info['ticker']
df_bv=df_info.copy()
df_ev=df_info.copy()
#defining period begining and end
ep= date(2020,11,17)
bp= inception
#bp= date(2020,11,10)


#calculating enterprise value for each period
df_ev['ev']=df_p[ep]*df_pr[ep]
df_bv['ev']=df_p[bp]*df_pr[bp]
#Calculating sector performance measures for the period
secbp=df_bv.groupby(['sector'])['ev'].agg('sum')
secep=df_ev.groupby(['sector'])['ev'].agg('sum')
secchg=(secep-secbp)/secbp
#calculating total portfolio and benchmark returns over the period
totchgport= ((df_ev['ev'].sum()+df_c[ep].sum())-(df_bv['ev'].sum()+df_c[bp].sum()))/(df_c[ep].sum()+df_bv['ev'].sum()+df_c[bp].sum())
totchgbench= ((sp_final[ep].sum()-sp_final[bp].sum())/sp_final[bp]).sum()
# finding the best and worst stock performers during the period
pricechange=pd.DataFrame()
pricechange[bp]=df_pr[bp].copy()
pricechange[ep]=df_pr[ep].copy()
pricechange['name']=df_info['name'].copy()
pricechange['check']=(df_p[bp]*df_p[ep])
pricechange.drop(pricechange[pricechange['check'] < 1].index, inplace = True)
pricechange['change']= (pricechange[ep]-pricechange[bp])/pricechange[bp]

bestperformers= pricechange.nlargest(5,'change')[['change','name']].copy()
worstperformers=pricechange.nsmallest(5,'change')[['change','name']].copy()

#printing measures
print('performance time period: from' ,bp,'to',ep,'\n')
print('total portfolio returns in the time period (%): \n', totchgport,'\n')
print('total benchmark returns in the time period (%): \n', totchgbench,'\n')
print('portfolio performance in by changes in sector value (%):\n ', secchg,'\n')
print('top 5 performers over the period (%): \n', bestperformers,'\n')
print('worst 5 performers over the period (%):\n ', worstperformers,'\n')
