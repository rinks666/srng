import argparse
import subprocess
import pandas as pd
import math
import csv
import plotly.express as px


parser = argparse.ArgumentParser(description='これは素晴らしいSRNG解析用のコマンドラインツールである')    # 2. パーサを作る

# 3. parser.add_argumentで受け取る引数を追加していく
parser.add_argument('cirfile', help='circuitfile ex. si.cir')    # 必須の引数を追加
parser.add_argument('-m','--mode',choices=['c','b','curve'],default='curve',help='c:単純なカウントツール b:ベイジアンネットワークの解析用ツール')

args = parser.parse_args()    # 4. 引数を解析

circuit_file_name = args.cirfile    #name of the circuitfile

def josim():
    subprocess.run(["josim", "-o", "./A.csv", "./" + circuit_file_name, "-V", "1"],stdout=subprocess.DEVNULL)

def counting(c_column):
    out_times_list = list()
    c_column = c_column+1
    for i in range(1,c_column):
        p_df = pd.read_csv("A.csv",usecols=[i])
        p_list = p_df.iloc[:,0].tolist()
        p_range = p_list[-1]-p_list[0]
        out_times_list.append(p_range//(2*math.pi))
    
    for i in range(len(out_times_list)):
        print(i+1,'列目のSRNGの出力数は',int(out_times_list[i]))

def scan_column():
    print("いくつのSRNGの出力をカウントしますか(ex: 3):")
    c_column = int(input())
    return c_column

def scan_curve():
    print("\n最初の.printを出力のJJの位相に設定してください。\n電流源の名前をIzにしてください。\n\n")
    print("電流Ictlの下限値[uA]:")
    i_low = float(input())
    print("電流Ictlの上限値[uA]:")
    i_high = float(input())
    print("Ictlのサンプリング間隔[uA]:")
    sample = float(input())
    print("1シミュレーション当たりの試行回数:")
    num_att = float(input())
    return i_low,i_high,sample,num_att

def create_list(a,b,c):
    # 下限と上限の間の値を0.1刻みで生成する
    my_list = [round(x, 2) for x in frange(a,b,c)]
    return my_list

def frange(start, stop, step):
    # 浮動小数点数の範囲を生成する関数
    while start < stop:
        yield start
        start += step

def process_lines(filename):
    extracted_line = ""
    afterline =""
    default_lines = []
    p_list = []

    # ファイルを開いて処理
    with open(filename, 'r') as file:
        for line in file:
            default_lines.append(line)
            if "Iz" in line:
                extracted_line = line

    extracted_phrases = extracted_line.split()
    #print(extracted_phrases)
    # PWLをに変換
    for val in Ictl_list:
        for i in range(len(extracted_phrases)):
            if "PWL" in extracted_phrases[i]:
                extracted_phrases[i] = "PWL(0ps 0mA 10ps "+str(val)+"uA)" 
                x = i+1   
        for i in range(x):
            afterline = afterline + " " + extracted_phrases[i]  
        afterline = afterline.strip()
        print(val,"uA")
        for i in range(len(default_lines)):
            if "Iz" in default_lines[i]:
                default_lines[i] = afterline+"\n"
                afterline = ""

        with open(filename, 'w+') as file:
            for i in default_lines:
                file.write(i)
        subprocess.run(["josim", "-o", "./A.csv", "./" + filename, "-V", "1"],stdout=subprocess.DEVNULL)
        pout = counter("A.csv")/num_att
        p_list.append(pout)

    return p_list

def counter(filename):
    p_df = pd.read_csv(filename,usecols=[1])
    p_list = p_df.iloc[:,0].tolist()

    range = p_list[-1]-p_list[0]
    o_t = range//(2*math.pi)
    return o_t

def resultcsv():
    with open("result.csv", "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # ヘッダーを書き込む（一列目と二列目）
        csv_writer.writerow(["Ictl [\u03BCA]", "Output Probability"])
        
        # result_listとp_listの対応する要素を一行ずつ書き込む
        for result, p in zip(Ictl_list, p_list):
            csv_writer.writerow([result, p])
    
def graphplot():

    # CSVファイルのパス
    csv_file_path = 'result.csv'

    # CSVファイルをDataFrameとして読み取り
    df = pd.read_csv(csv_file_path)

    # グラフを作成
    fig = px.scatter(df, x=df.columns[0], y=df.columns[1], title='')
    fig.update_xaxes(title_text=df.columns[0])  # 一列目のヘッダーをX軸ラベルに設定
    fig.update_yaxes(title_text=df.columns[1])  # 二列目のヘッダーをY軸ラベルに設定
    fig.update_layout(
        xaxis=dict(title=df.columns[0], showgrid=True, gridcolor='lightgray'),
        yaxis=dict(title=df.columns[1], showgrid=True, gridcolor='lightgray'),
        plot_bgcolor='white',  # 背景色を白に設定
        showlegend=False,  # 凡例を非表示に設定
        xaxis_showline=True,  # X軸の外枠線を表示
        yaxis_showline=True,  # Y軸の外枠線を表示
        xaxis_linecolor='black',  # X軸の外枠線の色を設定
        yaxis_linecolor='black'   # Y軸の外枠線の色を設定
    )

    # グラフを画像として保存
    fig.write_image('result.png')


if __name__ == "__main__":
    if(args.mode == 'c'):
        print('--------COUNTING_TOOL--------')
        print('--------出力したいJJの位相(Phase)を最初に.printしてください。-------')
        c_column = scan_column()
        josim()
        counting(c_column)

    elif(args.mode == 'b'):
        print('-------BAYESIAN_NETWORK_ANALYTICS--------')

    else:
        print('-------CURVE_DRAWER--------')
        i_low, i_high, sample,num_att = scan_curve()
        Ictl_list = create_list(i_low,i_high,sample)
        p_list = process_lines(circuit_file_name)
        print(p_list)
        resultcsv()
        graphplot()    

