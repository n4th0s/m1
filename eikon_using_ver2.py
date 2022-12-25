"""
<< 関数一覧 >>　(＋)応用としてFXおよび仮想通貨も取得できる (target_dataをFX,仮想通貨のricsコードにする)

①　eikon_stock：株価指数およびその構成銘柄の<株価>データを取得(引数 index = [True] or [False] で選択)
②　eikon_stock_code：特定銘柄の<株価>データを取得
③　index_date：下記関数④,⑤のプログラムで使用(データ整理のために必要)
④　eikon_financial：株価指数およびその構成銘柄の<財務>データ(ASKやBID, 時価総額など)を取得
⑤　eikon_financial_code：特定銘柄のの<財務>データ(ASKやBID, 時価総額など)を取得

"""

import numpy as np
import eikon as ek
import pandas as pd 
import time
import datetime
import matplotlib.pyplot as plt
import itertools
import collections
import sys
from tqdm.auto import tqdm

def eikon_stock(app_key=None, target_data = None,start_date = None,end_date = None, fields = "CLOSE"\
                  , interval = "daily",index = True,csv_not = False):
    
    """
    （一括型）eikonから引数target_dataに入力した株価データ(指数または構成銘柄の株価←引数指定)を取得し，
              データを整理してcsv保存
              デフォルト：全fieldsのデータをcsv保存

    Parameters
    ----------
    app_key : object
        eikonに登録したApp_keyを入力　※App_keyの登録などについてはeikon検索ツールで「App Key Generator」で調べる
     
    target_data : object
        ・eikonのget_timeseries関数構造と同様
        ・取得したい株価データをeikon特有のrics形式で入力　※引数ミスをすれば正しい表記方法を示すように設定(主要な株価に限定)
    start_date, end_date : object　（デフォルト：None）
        ・eikonのget_timeseries関数構造と同様
        ・例：文字列'%Y-%m-%d'('2018-09-10')や '%Y-%m-%dT%H:%M:%S'('2018-09-10T15:04:05')、
    fields : object　（デフォルト：CLOSE）
        ・eikonのget_timeseries関数構造と同様
        ・使用可能なフィールドは'TIMESTAMP', 'VALUE', 'VOLUME', 'HIGH', 'LOW', 'OPEN', 'CLOSE', 'COUNT'のみ
    interval : object　（デフォルト：daily）
        ・eikonのget_timeseries関数構造と同様
        ・使用可能な値は 'tick', 'minute', 'hour', 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
    
    index : bool
        ・target_dataで指定した株価データを「指数の株価データ」(デフォルト：True) または「構成銘柄の株価データ」(False)
          のどちらを取得するか指定

    csv_not : bool
        ・csv保存を行う(True)か否(False)か
          
    Returns (4data)
    -------
    Parametersによって変化
    全てpandas.DataFrame形式で出力
    
    ＜戻り値についての補足＞
    zero : 戻り値の埋め合わせように作成（特に意味ない）<No_dataと表記>
    err : 構成銘柄の株価データ取得の際に取得できなかった(上場廃止かその時期にデータがないなどが原因)銘柄コードを格納
    """
    ## 時間測定：開始 ##
    start = datetime.datetime.now()
    print("program_start : << " + str(start) + " >>\n")
    ####################
    
    if (interval in ['tick', 'minute', 'hour', 'daily', 'weekly', 'monthly', 'quarterly', 'yearly']) != True:
        print("※ Are the [interval]argument entered correctly?")
        sys.exit()
        
    ## eikon にアクセス ## 
    try:
        ek.set_app_key(app_key)
        print("< Eikon_Access_success >\n")
        print("<※> Assume that the function returns [four] return values")
        print("<※> Please enter the date correctly. example:<〇 2021-06-30,× 2021-06-31>")
    except Exception:
        print("You may not have access to <eikon>. Please start over.")
    ######################    
    
    # csv名称指定, 戻り値returnの埋め合わせなどの調整に必要
    target_data_name = target_data[1:]; zero = "No_data"
        
    # <<<< 指数の株価を取得 >>>>
    if index == True: 
        try:
            get_data = ek.get_timeseries(rics = target_data, start_date=start_date,end_date =end_date,interval=interval)
        except Exception: # エラー対策
            print("<< ➀ Try re-running a few times >>")
            print("<< ② Are the arguments entered correctly? >>"); print("[ Example of inputting target data ]")
            print("TOPIX → .TOPX, TOPIX100 → .TOPX100, TOPIX_Core30 → .TOPXC, TOPIX_Large70 → .TOPXL")
            print("TOPIX_Mid400 → .TOPXM, TOPIX_500 → .TOPX500"); print("日経225 → .N225, 日経300 → .N300, 日経500 → .N500\n")
        
        get_data = get_data.dropna(how = "all") # 取得できなかった期間(NANの部分)を削除
        get_data = get_data[~get_data.index.duplicated(keep="last")] # 重複している期間を削除（index = 1が2つあるなら1つを削除．最新日のみを残す)
        get_data.columns = list(get_data.columns) # カラム名を振り直し(columns.nameがあったら後々面倒だから)
        get_data = get_data[~get_data.index.duplicated(keep="last")]
        get_data = get_data.loc[get_data.index.dropna(how="any")] # 期間にNatを含む行を削除
    
        ## csv保存し, 戻り値returnを返す ##
        if fields == "CLOSE":
            close_data = pd.DataFrame(get_data["CLOSE"])
            close_data = close_data.dropna(how = "all") # 取得できなかった期間(NANの部分)を削除
            return_data = close_data.pct_change() # CLOSEからRUTURNデータを生成
            return_data.columns = ["RETURN"]
            if csv_not == False:
                close_data.to_csv( str(target_data_name) + "_index_CLOSE_" + str(interval) + ".csv")
                return_data.to_csv( str(target_data_name) + "_index_RETURN_" + str(interval) + ".csv")
                get_data.to_csv( str(target_data_name) + "_index_" + str(interval) + ".csv")
            ## 時間測定：終了 ##
            end = datetime.datetime.now()
            print("program_end : << " + str(end) + " >>\n")
            ####################    
            return close_data,return_data,get_data,zero

        else:
            fields_data = pd.DataFrame(get_data[fields])
            fields_data = fields_data.dropna(how = "all") # 取得できなかった期間(NANの部分)を削除
            if csv_not == False:
                fields_data.to_csv( str(target_data_name) + "_index_" + str(fields) + "_" + str(interval) + ".csv")
                get_data.to_csv( str(target_data_name) + "_index_" + str(interval) + ".csv")
            ## 時間測定：終了 ##
            end = datetime.datetime.now()
            print("program_end : << " + str(end) + " >>\n")
            ####################               
            return fields_data,get_data,zero,zero
        ####################################
            
            
    # <<<< 構成銘柄の株価データを取得 >>>>
    else: 
        try:
            target_data_code = ek.get_data(['0#' + str(target_data)],fields = 'DSPLY_NMLL')
        except Exception: # エラー対策
            print("<< ➀ Try re-running a few times >>")
            print("<< ② Are the arguments entered correctly? >>"); print("[ Example of inputting target data ]")
            print("TOPIX → .TOPX, TOPIX100 → .TOPX100, TOPIX_Core30 → .TOPXC, TOPIX_Large70 → .TOPXL")
            print("TOPIX_Mid400 → .TOPXM, TOPIX_500 → .TOPX500"); print("日経225 → .N225, 日経300 → .N300, 日経500 → .N500\n")
        
        # 取得した株価コードをリスト化してsort()
        code = list(target_data_code[0]["Instrument"]); code.sort()

        get_data = [] # codeごとに取得したデータを一時的に格納
        err = [] # エラーの出た銘柄名を格納.
        non_code = [] # 編集後にデータが残らない銘柄を格納
        
        ### codeごとにデータ取得
        pp = tqdm(range(len(code)))
        for i in pp:
            try:
                pp.set_description("<< dataget_process >> ") #rqdmのプロセスバーに名前を付ける
                pass #rqdmのプロセスバーに名前を付ける
            
                df = ek.get_timeseries([code[i]],start_date=start_date,end_date =end_date,interval=interval) # Eikonでデータ取得
                df = df.dropna(how = "all") # 取得できなかった期間(NANの部分)を削除
                df = df[~df.index.duplicated(keep="last")] # 重複している期間を削除（index = 1が2つあるなら1つを削除．最新日のみを残す)
                df["code"] = code[i]  # カラムにcodeを作成して銘柄を明示
                df = df[~df.index.duplicated(keep="last")]
                df = df.loc[df.index.dropna(how="any")] # 期間にNatを含む行を削除
                df.reset_index(inplace=True) # 後々の処理のために一度indexをリセット
                
                if len(df)==0:
                    non_code.append(code[i]) # 編集後にデータが残らない銘柄
                else:
                    get_data.append(df)
            except Exception:# 銘柄のデータ取得で何かしらのエラーが出たとき、その銘柄名をerrに格納して次の銘柄を取得
                err.append(code[i])
                pass            
        ##################################
        
        if len(non_code)!=0:
            print("編集後にデータが残らなかった銘柄があります(エラー銘柄として戻り値のリストに格納しません")
            print(str(len(non_code)) + "：銘柄")
            
        # csv として保存しやすいように銘柄ごとのデータを連結
        data_=pd.concat(get_data) 
        # csv保存のためにindexにDateを入れる
        get_data = data_.set_index('Date')
        get_data.columns = list(get_data.columns) # カラム名を振り直し(columns.nameがあったら後々面倒だから)
        
        get_code = get_data['code'].unique().tolist() # 取得できた株価コードをリスト化
        
        # 警告文　[]部分の表示された銘柄はプログラムを再実行することで取得できる可能性があります
        print("※ Stock symbols with [Backend error. 500 Internal Server Error] displayed may be obtained by re-executing the program")
        print("Get stock symbols that could not be retrieved using function [eikon_stock_code(arguments)]")
        
        df_data = pd.DataFrame() # 戻り値return用に整理した後のデータを格納        
        
        # tqdmのプロセスバーが複数表示されてしまうエラーが出たため，回避のために実行
        for k in tqdm(range(2),disable=True): #disableとはプロセスバーを非表示にすること
            time.sleep(0.01)
        
        ## csv保存し, 戻り値returnを返す ##
        ss = tqdm(range(len(get_code)))
        if fields == "CLOSE":
            for i in ss: # 銘柄ごとにデータを整理
                ss.set_description("<< data_arrange_process >> ") #rqdmのプロセスバーに名前を付ける
                pass #rqdmのプロセスバーに名前を付ける
            
                k = get_data[get_data.code == get_code[i]][fields]
                k = k.dropna(how = "all") # 取得できなかった期間(NANの部分)を削除
                df_data = pd.concat([df_data,k],axis=1)       
            df_data.index.name = "Date"
            close_data = pd.DataFrame(df_data.dropna(how="all")) # CLOSEデータ
            close_data.columns = get_code
            return_data = close_data.pct_change() # CLOSEからRUTURNデータを生成
            if csv_not == False:
                close_data.to_csv( str(target_data_name) + "_CLOSE_" + str(interval) + ".csv")
                return_data.to_csv( str(target_data_name) + "_RETURN_" + str(interval) + ".csv")
                get_data.to_csv( str(target_data_name) + "_" + str(interval) + ".csv")
            ## 時間測定：終了 ##
            end = datetime.datetime.now()
            print("program_end : << " + str(end) + " >>\n")
            ####################            
            return close_data,return_data,get_data,err

        else:
            for i in ss: # 銘柄ごとにデータを整理
                ss.set_description("<< data_arrange_process >> ") #rqdmのプロセスバーに名前を付ける
                pass #rqdmのプロセスバーに名前を付ける  
            
                k = get_data[get_data.code == get_code[i]][fields]
                k = k.dropna(how = "all") # 取得できなかった期間(NANの部分)を削除
                df_data = pd.concat([df_data,k],axis=1)
            df_data.index.name = "Date"
            df_data = pd.DataFrame(df_data.dropna(how="all"))
            df_data.columns = get_code
            if csv_not == False:
                df_data.to_csv( str(target_data_name) + "_" + str(fields) + "_" + str(interval) + ".csv")
                get_data.to_csv( str(target_data_name) + "_" + str(interval) + ".csv")
            ## 時間測定：終了 ##
            end = datetime.datetime.now()
            print("program_end : << " + str(end) + " >>\n")
            ####################
            return df_data, get_data,err,zero
        ###################################
        
        
        
def eikon_stock_code(app_key=None, target_data = None,start_date = None,end_date = None, fields = "CLOSE"\
                  , interval = "daily"):
    
    """
    関数：eikon_stockとほぼ同様　→　相違点：引数target_dataに取得したい特定の銘柄を入力し、
                                             その銘柄の株価データを取得
    ※※※ <<< csv保存機能はなし >>> ※※※                                           

    Parameters：関数：eikon_stockとほぼ同様（引数indexなし）
    ----------
    (変更引数)
    target_data : objectを内包したlist型
        ・取得したい株価データをeikon特有のrics形式で入力(例：["1333.T", ...])
          
    Returns (4data):関数：eikon_stockと同様
    -------
    """    
    ## 時間測定：開始 ##
    start = datetime.datetime.now()
    print("program_start : << " + str(start) + " >>\n")
    ####################

    if (interval in ['tick', 'minute', 'hour', 'daily', 'weekly', 'monthly', 'quarterly', 'yearly']) != True:
        print("※ Are the [interval]argument entered correctly?")
        sys.exit()    
    
    ## eikon にアクセス ## 
    try:
        ek.set_app_key(app_key)  # 塚原専用
        print("< Eikon_Access_success >\n")
        print("<※> Assume that the function returns [four] return values")
        print("<※> Please enter the date correctly. example:<〇 2021-06-30,× 2021-06-31>")
    except Exception:
        print("You may not have access to <eikon>. Please start over.")
    ######################    
    
    # 戻り値returnの埋め合わせなどの調整に必要
    zero = "No_data"
        
    get_data = [] # codeごとに取得したデータを一時的に格納
    err = [] # エラーの出た銘柄名を格納
    non_code = [] # 編集後にデータが残らない銘柄を格納

    pp = tqdm(range(len(target_data))) # codeごとにデータ取得
    for i in pp:
        try:
            pp.set_description("<< dataget_process >> ") #rqdmのプロセスバーに名前を付ける
            pass #rqdmのプロセスバーに名前を付ける
            
            df = ek.get_timeseries([target_data[i]],start_date=start_date,end_date =end_date,interval=interval) # Eikonでデータ取得
            df = df.dropna(how = "all") # 取得できなかった期間(NANの部分)を削除
            df = df[~df.index.duplicated(keep="last")] # 重複している期間を削除（index = 1が2つあるなら1つを削除．最新日のみを残す)
            df["code"] = target_data[i]  # カラムにcodeを作成して銘柄を明示
            df = df[~df.index.duplicated(keep="last")]
            df = df.loc[df.index.dropna(how="any")] # 期間にNatを含む行を削除
            df.reset_index(inplace=True) # 後々の処理のために一度indexをリセット
            
            if len(df)==0:
                non_code.append(target_data[i]) # 編集後にデータが残らない銘柄
            else:
                get_data.append(df)
        except Exception:# 銘柄のデータ取得で何かしらのエラーが出たとき、その銘柄名をerrに格納して次の銘柄を取得
            err.append(target_data[i])
            pass
        
    if len(non_code)!=0:
        print("編集後にデータが残らなかった銘柄があります(エラー銘柄として戻り値のリストに格納しません")
        print(str(len(non_code)) + "：銘柄")
        
    # csv として保存しやすいように銘柄ごとのデータを連結
    data_=pd.concat(get_data) 
    # csv保存のためにindexにDateを入れる
    get_data = data_.set_index('Date')
    get_data.columns = list(get_data.columns) # カラム名を振り直し(columns.nameがあったら後々面倒だから)

    get_code = get_data['code'].unique().tolist() # 取得できた株価コードをリスト化

    # 警告文　[]部分の表示された銘柄はプログラムを再実行することで取得できる可能性があります
    print("※ Stock symbols with [Backend error. 500 Internal Server Error] displayed may be obtained by re-executing the program")
    print("Try re-running function [eikon_stock_code(arguments)] a few times")
        
    df_data = pd.DataFrame() # 戻り値return用に整理した後のデータを格納
    
    # tqdmのプロセスバーが複数表示されてしまうエラーが出たため，回避のために実行
    for k in tqdm(range(2),disable=True): #disableとはプロセスバーを非表示にすること
        time.sleep(0.01)
    
    ## csv保存し, 戻り値returnを返す ##
    ss = tqdm(range(len(get_code)))
    if fields == "CLOSE":
        for i in ss: # 銘柄ごとにデータを整理
            ss.set_description("<< data_arrange_process >> ") #rqdmのプロセスバーに名前を付ける
            pass #rqdmのプロセスバーに名前を付ける            
            
            k = get_data[get_data.code == get_code[i]][fields]
            k = k.dropna(how = "all") # 取得できなかった期間(NANの部分)を削除
            df_data = pd.concat([df_data,k],axis=1)          
        df_data.index.name = "Date"
        close_data = pd.DataFrame(df_data.dropna(how="all")) # CLOSEデータ
        close_data.columns = get_code
        return_data = close_data.pct_change() # CLOSEからRUTURNデータを生成
        ## 時間測定：終了 ##
        end = datetime.datetime.now()
        print("program_end : << " + str(end) + " >>\n")
        ####################  
        return close_data,return_data,get_data,err

    else:
        for i in ss: # 銘柄ごとにデータを整理
            ss.set_description("<< data_arrange_process >> ") #rqdmのプロセスバーに名前を付ける
            pass #rqdmのプロセスバーに名前を付ける       
        
            k = get_data[get_data.code == get_code[i]][fields]
            k = k.dropna(how = "all") # 取得できなかった期間(NANの部分)を削除
            df_data = pd.concat([df_data,k],axis=1)
        df_data.index.name = "Date"
        df_data = pd.DataFrame(df_data.dropna(how="all"))
        df_data.columns = get_code
        ## 時間測定：終了 ##
        end = datetime.datetime.now()
        print("program_end : << " + str(end) + " >>\n")
        ####################        
        return df_data,get_data, err,zero
    ###################################

    
    
def index_date(data):
        
    """
    関数eikon_financialおよびeikon_financial_codeのプログラムで使用する関数
    
    関数eikon_financialおよびeikon_financial_codeで取得したデータのindexは正しく表現されないのでindexを適切に直す関数
    
    Parameters
    ----------
    data : DataFrame
        indexに日付があるデータフレーム(かつ, そのindexの日付表現がdatetime64[ns, UTC]のとき)

    Returns (1data)
    -------
    data : indexの表現を適切に直したデータフレーム
    
    """
    index = data.index
    list_=[]
    for i in range(len(index)):
        w = index[i].date()
        list_.append(w)
    data.index = list_
    data.index = pd.to_datetime(data.index)
    data.index.names = ['Date']
    return data

def eikon_financial(app_key=None, target_data = None,start_date = None,end_date = None,\
                    curn = None, frq=None, period=None,scale=None,fields = None,\
                    index = True,csv_not=False,periodenddate=False,params=True):
    
    """
    （一括型）eikonから引数target_dataに入力した株価データ(指数または構成銘柄の株価←引数指定)を取得し，
              データを整理してcsv保存
    
    Parameters
    ----------
    app_key : object
        eikonに登録したApp_keyを入力　※App_keyの登録などについてはeikon検索ツールで「App Key Generator」で調べる
     
    target_data : object
        ・eikonのget_timeseries関数構造と同様
        ・取得したい株価データをeikon特有のrics形式で入力　※引数ミスをすれば正しい表記方法を示すように設定(主要な株価に限定)
    start_date, end_date : object　（デフォルト：None）
        ・eikonのget_timeseries関数構造と同様
        ・例：文字列'%Y-%m-%d'('2018-09-10')や '%Y-%m-%dT%H:%M:%S'('2018-09-10T15:04:05')、
    fields : object（デフォルト：None） 
        Example：引数 fileds = "TR.ASKPRICE" // TR.ASKPRICE → ASKのricsコード 
        ・取得したいデータ(ASK,BID,時価総額など)のricsコードを調べて入力
    
    curn,frg,period,scale : eikonのget_data関数構造と同様
    
    index : bool
        ・target_dataで指定した株価データを「指数の株価データ」(デフォルト：True) または「構成銘柄の株価データ」(False)
          のどちらを取得するか指定
    
    csv_not : bool
    ・csv保存を行う(True)か否(False)か
    
    periodenddate：bool
    ・データ取得日をperiodenddateで取得するか否か
    
    params：bool（デフォルト：True）
    ・引数parametersを使用するか否か（Eikon関数は引数parametersを使用するものとそうでない二つの記述方法がある）
          
    Returns (2data)
    -------
    Parametersによって変化
    全てpandas.DataFrame形式で出力
    
    ＜戻り値についての補足＞
    zero : 戻り値の埋め合わせように作成（特に意味ない）
    err : 構成銘柄の株価データ取得の際に取得できなかった(上場廃止かその時期にデータがないなどが原因)銘柄コードを格納
    """    
    ## 時間測定：開始 ##
    start = datetime.datetime.now()
    print("program_start : << " + str(start) + " >>\n")
    ####################
    
    ## eikon にアクセス ## 
    try:
        ek.set_app_key(app_key)  # 塚原専用
        print("< Eikon_Access_success >\n")
        print("<※> Assume that the function returns [two] return values")
        print("<※> Please enter the date correctly. example:<〇 2021-06-30,× 2021-06-31>")
    except Exception:
        print("You may not have access to <eikon>. Please start over.")
    ######################    
    
    # csv名称指定, 戻り値returnの埋め合わせなどの調整に必要
    target_data_name = target_data[1:]; zero = "No_data"
    
    # fieldsデータの取得日をデータに追加
    fields_list = [] # 空リスト作成
    if periodenddate==True:
        fields_date = fields + ".periodenddate" # fieldsの取得日をricsコードに変換
    else:
        fields_date = fields + ".date" # fieldsの取得日をricsコードに変換
    fields_list.append(fields_date); fields_list.append(fields) 
        
    if params != False:
        parameters = {'SDate':start_date,'EDate':end_date}

        # 下記4つのパラメータが指定されたら調整する
        if (curn != None)or(frq!=None)or(period!=None)or(scale!=None):
            parameters.update({"Curn":curn}) if curn != None else parameters.update()
            parameters.update({"Frq":frq}) if frq != None else parameters.update()
            parameters.update({"Period":period}) if period != None else parameters.update()
            parameters.update({"Scale":scale}) if scale != None else parameters.update()

            parameters.update({"Frq":period[:2]}) if (frq ==None)and(period!=None) else parameters.update()
    else:
        parameters =None
                    
    # <<<< 指数の財務データ(引数fields)を取得 >>>>
    if index == True: 
        try:
            data = ek.get_data(target_data,fields = fields_list,parameters =parameters)

        except Exception: # エラー対策
            print("<< ➀ Try re-running a few times >>")
            print("<< ② Are the arguments entered correctly? >>"); print("[ Example of inputting target data ]")
            print("TOPIX → .TOPX, TOPIX100 → .TOPX100, TOPIX_Core30 → .TOPXC, TOPIX_Large70 → .TOPXL")
            print("TOPIX_Mid400 → .TOPXM, TOPIX_500 → .TOPX500"); print("日経225 → .N225, 日経300 → .N300, 日経500 → .N500\n")
        
        try: # 取得した変数dataを整理する
            value=np.array(data[0].iloc[:,2:])
            if periodenddate==True:
                index = pd.to_datetime(data[0]["Period End Date"])
            else:
                index = pd.to_datetime(data[0]["Date"])
            columns = data[0].iloc[:,2:].columns[0]
            columns = columns.replace(" ", '_') 
        except Exception: # エラー対策
            print("Maybe you haven't entered the appropriate [fields] for [target_data] and [index]")
            print("Or [start_date] and [end_date] periods may not be correct")
            print("Or [curn, frq, period, scale] parameters are not the appropriate combination of ")
            print("   themselves or other parameters")
        get_data = pd.DataFrame(data = value,index = index)
        get_data = get_data.rename(columns={0:columns})
        get_data = get_data.dropna(how = "all") # 取得できなかった期間(NANの部分)を削除
        get_data = get_data[~get_data.index.duplicated(keep="last")] # 重複している期間を削除（index = 1が2つあるなら1つを削除．最新日のみを残す)
        get_data = index_date(get_data) # 関数index_date()でindex表現を適切に直す
        get_data = get_data[~get_data.index.duplicated(keep="last")]
        
        # 期間にNatを含む行を削除
        get_data = get_data.loc[get_data.index.dropna(how="any")]

        ## csv保存し, 戻り値returnを返す ##
        if csv_not == False:
            get_data.to_csv( str(target_data_name) + "_index_" + str(columns) + ".csv")
        ## 時間測定：終了 ##
        end = datetime.datetime.now()
        print("program_end : << " + str(end) + " >>\n")
        ####################    
        return get_data,zero

        ####################################

    # <<<< 構成銘柄の株価データを取得 >>>>
    else: 
        try:
            target_data_code = ek.get_data(['0#' + str(target_data)],fields = 'DSPLY_NMLL')
        except Exception: # エラー対策
            print("<< ➀ Try re-running a few times >>")
            print("<< ② Are the arguments entered correctly? >>"); print("[ Example of inputting target data ]")
            print("TOPIX → .TOPX, TOPIX100 → .TOPX100, TOPIX_Core30 → .TOPXC, TOPIX_Large70 → .TOPXL")
            print("TOPIX_Mid400 → .TOPXM, TOPIX_500 → .TOPX500"); print("日経225 → .N225, 日経300 → .N300, 日経500 → .N500\n")
        
        # 取得した株価コードをリスト化してsort()
        code = list(target_data_code[0]["Instrument"]); code.sort()

        get_data_list = [] # codeごとに取得したデータを一時的に格納
        err = [] # エラーの出た銘柄名を格納
        non_code = [] # 編集後にデータが残らない銘柄を格納
        
        pp = tqdm(range(len(code))) # codeごとにデータ取得
        for i in pp:
            try:
                pp.set_description("<< dataget_process >> ") #rqdmのプロセスバーに名前を付ける
                pass #rqdmのプロセスバーに名前を付ける       
            
                data = ek.get_data(code[i],fields = fields_list,parameters =parameters)
                
                try: # 取得した変数dataを整理する
                    value=np.array(data[0].iloc[:,2:])
                    if periodenddate==True:
                        index = pd.to_datetime(data[0]["Period End Date"])
                    else:
                        index = pd.to_datetime(data[0]["Date"])
                    columns = code[i]
                except Exception: # エラー対策
                    print("Maybe you haven't entered the appropriate [fields] for [target_data] and [index]")
                    print("Or [start_date] and [end_date] periods may not be correct")
                    print("Or [curn, frq, period, scale] parameters are not the appropriate combination of ")
                    print("   themselves or other parameters")

                get_data = pd.DataFrame(data = value,index = index)
                get_data = get_data.rename(columns={0:columns})
                get_data = get_data.dropna(how = "all") # 取得できなかった期間(NANの部分)を削除
                get_data = get_data[~get_data.index.duplicated(keep="last")] # 重複している期間を削除（index = 1が2つあるなら1つを削除．最新日のみを残す)
                get_data = index_date(get_data) # 関数index_date()でindex表現を適切に直す     
                get_data = get_data[~get_data.index.duplicated(keep="last")] # # 重複している期間を削除（最新日のみを残す)
                if len(get_data)==0:
                    non_code.append(code[i]) # 編集後にデータが残らない銘柄
                else:
                    get_data_list.append(get_data)
            except Exception:# 銘柄のデータ取得で何かしらのエラーが出たとき、その銘柄名をerrに格納して次の銘柄を取得
                err.append(code[i])
                pass            
        
        if len(non_code)!=0:
            print("編集後にデータが残らなかった銘柄があります(エラー銘柄として戻り値のリストに格納しません")
            print(str(len(non_code)) + "：銘柄")
        
        print("<< data_arrange_process >>\n")
        
        # csv として保存しやすいように銘柄ごとのデータを連結
        data_all=pd.concat(get_data_list,axis=1) 
        # 期間にNatを含む行を削除
        data_all = data_all.loc[data_all.index.dropna(how="any")]
        
        fields_name = data[0].iloc[:,2:].columns[0] # csv保存用にfieldsの名前を取得
        fields_name = fields_name.replace(" ", '_') 
        
        # 警告文　[]部分の表示された銘柄はプログラムを再実行することで取得できる可能性があります
        print("※ Stock symbols with [Backend error. 500 Internal Server Error] displayed may be obtained by re-executing the program")
        print("Get stock symbols that could not be retrieved using function [eikon_financial_code(arguments)]\n")
        
        ## csv保存し, 戻り値returnを返す ##
        if csv_not == False:
            data_all.to_csv( str(target_data_name) + "_" + str(fields_name) + ".csv")
        ## 時間測定：終了 ##
        end = datetime.datetime.now()
        print("program_end : << " + str(end) + " >>\n")
        ####################          
        return data_all,err
        ###################################
        
        
def eikon_financial_code(app_key=None, target_data = None,start_date = None,end_date = None,\
                    curn = None, frq=None, period=None,scale=None,fields = None,periodenddate=False,params=True):
    """
    関数：eikon_financialとほぼ同様　→　相違点：引数target_dataに取得したい特定の銘柄を入力し、
                                                その銘柄の財務データを取得
    ※※※ <<< csv保存機能はなし >>> ※※※                                          

    Parameters：関数：eikon_financialとほぼ同様（引数indexなし）
    ----------
    (変更引数)
    target_data : objectを内包したlist型
        ・取得したい株価データをeikon特有のrics形式で入力(例：["1333.T", ...])
          
    Returns (2data)：関数：eikon_financialと同様
    -------
    """    
    ## 時間測定：開始 ##
    start = datetime.datetime.now()
    print("program_start : << " + str(start) + " >>\n")
    #################### 
    
    ## eikon にアクセス ## 
    try:
        ek.set_app_key(app_key)  # 塚原専用
        print("< Eikon_Access_success >\n")
        print("<※> Assume that the function returns [two] return values")
        print("<※> Please enter the date correctly. example:<〇 2021-06-30,× 2021-06-31>")
    except Exception:
        print("You may not have access to <eikon>. Please start over.")
    ######################    

    # csv名称指定, 戻り値returnの埋め合わせなどの調整に必要
    zero = "No_data"
    
    # fieldsデータの取得日をデータに追加
    fields_list = [] # 空リスト作成
    if periodenddate==True:
        fields_date = fields + ".periodenddate" # fieldsの取得日をricsコードに変換
    else:
        fields_date = fields + ".date" # fieldsの取得日をricsコードに変換
    fields_list.append(fields_date); fields_list.append(fields)
   
    if params != False:
        parameters = {'SDate':start_date,'EDate':end_date}

        # 下記4つのパラメータが指定されたら調整する
        if (curn != None)or(frq!=None)or(period!=None)or(scale!=None):
            parameters.update({"Curn":curn}) if curn != None else parameters.update()
            parameters.update({"Frq":frq}) if frq != None else parameters.update()
            parameters.update({"Period":period}) if period != None else parameters.update()
            parameters.update({"Scale":scale}) if scale != None else parameters.update()

            parameters.update({"Frq":period[:2]}) if (frq ==None)and(period!=None) else parameters.update()
    else:
        parameters = None
    
    get_data_list = [] # codeごとに取得したデータを一時的に格納
    err = [] # エラーの出た銘柄名を格納
    non_code = [] # 編集後にデータが残らない銘柄を格納

    pp = tqdm(range(len(target_data))) # codeごとにデータ取得
    for i in pp:
        try:
            pp.set_description("<< dataget_process >> ") #rqdmのプロセスバーに名前を付ける
            pass #rqdmのプロセスバーに名前を付ける             
            
            data = ek.get_data(target_data[i],fields = fields_list,parameters =parameters)
            
            try: # 取得した変数dataを整理する
                value=np.array(data[0].iloc[:,2:])
                if periodenddate==True:
                    index = pd.to_datetime(data[0]["Period End Date"])
                else:
                    index = pd.to_datetime(data[0]["Date"])
                columns = target_data[i]
            except Exception: # エラー対策
                print("Maybe you haven't entered the appropriate [fields] for [target_data] and [index]")
                print("Or [start_date] and [end_date] periods may not be correct")
                print("Or [curn, frq, period, scale] parameters are not the appropriate combination of ")
                print("   themselves or other parameters")
                    
            get_data = pd.DataFrame(data = value,index = index)
            get_data = get_data.rename(columns={0:columns})
            get_data = get_data.dropna(how = "all") # 取得できなかった期間(NANの部分)を削除
            get_data = get_data[~get_data.index.duplicated(keep="last")] # 重複している期間を削除（index = 1が2つあるなら1つを削除．最新日のみを残す)
            get_data = index_date(get_data) # 関数index_date()でindex表現を適切に直す
            get_data = get_data[~get_data.index.duplicated(keep="last")] # # 重複している期間を削除（最新日のみを残す)
            
            if len(get_data)==0:
                non_code.append(target_data[i]) # 編集後にデータが残らない銘柄
            else:
                get_data_list.append(get_data)
        except Exception:# 銘柄のデータ取得で何かしらのエラーが出たとき、その銘柄名をerrに格納して次の銘柄を取得
            err.append(target_data[i])
            pass      
        
    if len(non_code)!=0:
        print("編集後にデータが残らなかった銘柄があります(エラー銘柄として戻り値のリストに格納しません")
        print(str(len(non_code)) + "：銘柄")
    
    print("<< data_arrange_process >>\n")
        
    # csv として保存しやすいように銘柄ごとのデータを連結
    data_all=pd.concat(get_data_list,axis=1)
    # 期間にNatを含む行を削除
    data_all = data_all.loc[data_all.index.dropna(how="any")]

    # 警告文　[]部分の表示された銘柄はプログラムを再実行することで取得できる可能性があります
    print("※ Stock symbols with [Backend error. 500 Internal Server Error] displayed may be obtained by re-executing the program")
    print("Try re-running function [eikon_financial_code(arguments)] a few times\n")
    
    ## 時間測定：終了 ##
    end = datetime.datetime.now()
    print("program_end : << " + str(end) + " >>\n")
    ###################         
    return data_all,err
