import investpy as inv
import matplotlib.pyplot as plt
from scipy.stats import linregress as line
import pandas as pd

class rank:  ##return the rank of the assets with more average monthly gains above benchmark and less volatility
    ##qts=how many will appear in the rank
    def lessrisk_moregains(self,datei,datef,index_,qts):
        country_='Brazil'   ##I don't know how the symbols of stocks in other country works, so i will limit my code to Brazil
        symbols = inv.get_stocks(country=country_).symbol
        my_rank = pd.DataFrame({'symb':[],'abv_bench_mean':[],'beta':[],'ratio':[]})
        bench_hist = inv.get_index_historical_data(index=index_,country=country_,from_date=datei,to_date=datef,interval="Monthly").Open
        bench_hist_change = bench_hist[bench_hist!=0].pct_change()
        bench_hist_change = bench_hist_change.dropna()
        how_many_errors=0 ###counts how many unavailable assets
        for symb in symbols:
            if symb[-1]!='3':
                continue
            ##There's some stocks names listed in inv.get_stocks that information is unavailable
            ##so i will do a test first
            works=False
            try:
                asset_hist = inv.get_stock_historical_data(stock=symb,country=country_,from_date=datei,to_date=datef,interval="Monthly").Open
                asset_hist_change = asset_hist[asset_hist!=0].pct_change()
                asset_hist_change = asset_hist_change.dropna()
                works=True
                sort = pd.DataFrame({'benchmark':bench_hist_change,'asset':asset_hist_change}).dropna().reset_index()
            except:
                if(how_many_errors<30):
                    how_many_errors+=1
                    print("Sorry, but "+symb+" is not available, it will be excluded from the rank")
                    print("How many unavailable:"+str(how_many_errors))
                if(how_many_errors==30):
                    print("More than 30 assets unavailable, it could be a connection problem")
                    how_many_errors+=1
                pass
            ##sort = data sorted by common dates and delete dates not in common
            if (works)and(len(sort.benchmark)!=0)and(len(sort.asset)!=0):
                beta = line(sort.benchmark,sort.asset)[0]
                if(beta<=0):
                    continue
                abv_bench =  sort.asset-sort.benchmark
                abv_bench_mean = abv_bench.mean()
                ratio = abv_bench_mean/beta
                
                add={'symb':symb,'abv_bench_mean':(str(round(abv_bench_mean*100,2))+"%"),'beta':round(beta,4),'ratio':ratio}
                my_rank = my_rank.append(add,ignore_index=True)

        my_rank = my_rank.sort_values(by='ratio',ascending=False).head(qts)
        my_rank = my_rank.drop('ratio',1)
        fig,ax = plt.subplots(figsize=[10,5])
        ax.set_title("Top "+str(qts)+" stocks with highest gains above "+index_+" index and lowest risks in "+country_)
        period_string = ("Period: "+datei +" to "+datef)
        ax.set_xlabel("Average monthly relative rentability(AMRR)="+" Average gains above Benchmark("+index_+" Index)\n"+period_string)
        plt.xticks([])
        plt.yticks([])
        ax.table(bbox=[0,0.1,1,0.8],rowLabels=range(1,qts+1),colLabels=['Symbol','AMRR','Beta(risk)'],cellText=my_rank.values,loc='center',rowLoc='center',cellLoc='center')

        fig.savefig('Rank.png')
        plt.show()
        
rank().lessrisk_moregains('30/05/2015','30/05/2020','Bovespa',10)
