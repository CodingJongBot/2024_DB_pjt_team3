#!/usr/bin/env python
# coding: utf-8

###################################################################
#                                                                 #
#   2024 DS2 Database Project : Recommendation using SQL-Python   #
#                                                                 #
###################################################################

import mysql.connector
from tabulate import tabulate
import pandas as pd
import math
import sys

## Connect to Remote Database
## Insert database information

HOST = "147.46.15.238"
PORT = "7000"
USER = "DS2024_0027"
PASSWD = "DS2024_0027"
DB = "DS_proj_03"

connection = mysql.connector.connect(
    host=HOST,
    port=7000,
    user=USER,
    passwd=PASSWD,
    db=DB,
    autocommit=True  # to create table permanently
)

cur = connection.cursor(dictionary=True)

## 수정할 필요 없는 함수입니다.
# DO NOT CHANGE INITIAL TABLES IN prj.sql
def get_dump(mysql_con, filename):
    '''
    connect to mysql server using mysql_connector
    load .sql file (filename) to get queries that create tables in an existing database (fma)
    '''
    query = ""
    try:
        with mysql_con.cursor() as cursor:
            for line in open(filename, 'r'):
                if line.strip():
                    line = line.strip()
                    if line[-1] == ";":
                        query += line
                        cursor.execute(query)
                        query = ""
                    else:
                        query += line

    except Warning as warn:
        print(warn)
        sys.exit()


## 수정할 필요 없는 함수입니다.
# SQL query 를 받아 해당 query를 보내고 그 결과 값을 dataframe으로 저장해 return 해주는 함수
def get_output(query):
    cur.execute(query)
    out = cur.fetchall()
    df = pd.DataFrame(out)
    return df


# [Algorithm 1] Popularity-based Recommendation - 1 : Popularity by rating count
def popularity_based_count(user_input=True, item_cnt=None):
    if user_input:
        rec_num = int(input('Number of recommendations?: '))
    else:
        assert item_cnt is not None
        rec_num = int(item_cnt)
    print(f"Popularity Count based recommendation")
    print("=" * 99)

    # TODO: remove sample, return actual recommendation result as df
    # YOUR CODE GOES HERE !
    # 쿼리의 결과를 sample 변수에 저장하세요.

    query = "SELECT r.item, COUNT(r.user) as count\
            FROM ratings r\
            WHERE r.rating is not NULL and r.item BETWEEN 150 and 349\
            GROUP BY r.item\
            ORDER BY COUNT(r.user) DESC, r.item ASC\
            LIMIT "+str(rec_num)

    sample = get_output(query).values.tolist()
    
    # do not change column names
    df = pd.DataFrame(sample, columns=['item', 'count'])
    # TODO end

    # Do not change this part
    with open('pbc.txt', 'w') as f:
        f.write(tabulate(df, headers=df.columns, tablefmt='psql', showindex=False))
    print("Output printed in pbc.txt")


# [Algorithm 1] Popularity-based Recommendation - 2 : Popularity by average rating
def popularity_based_rating(user_input=True, item_cnt=None):
    if user_input:
        rec_num = int(input('Number of recommendations?: '))
    else:
        assert item_cnt is not None
        rec_num = int(item_cnt)
    print(f"Popularity Rating based recommendation")
    print("=" * 99)

    # TODO: remove sample, return actual recommendation result as df
    # YOUR CODE GOES HERE !
    # 쿼리의 결과를 sample 변수에 저장하세요.
          
    query= "SELECT sb2.item, ROUND(AVG(sb2.norm_rating),4) as avg_norm_rating\
            FROM (\
                SELECT \
                    rt.item,\
                    IF(sb.num_items = 1,(rt.rating-0/sb.max_rating-0), ((rt.rating - sb.min_rating) / sb.rating_range)) as norm_rating\
                FROM(\
                    SELECT \
                        r.user,\
                        MAX(r.rating) as max_rating,\
                        MIN(r.rating) as min_rating ,\
                        MAX(r.rating) - MIN(r.rating) as rating_range,\
                        COUNT(r.item) as num_items\
                    FROM ratings r\
                    WHERE r.rating is not NULL\
                    GROUP BY r.user\
                    ) AS sb\
                JOIN ratings rt ON rt.user = sb.user\
            ) AS sb2\
            WHERE sb2.item BETWEEN 150 and 349\
            GROUP BY sb2.item\
            ORDER BY avg_norm_rating DESC,sb2.item ASC\
            LIMIT "+ str(rec_num)
    #i번 사용자(Ui)가 1개의 아이템에만 평점을 부여한 경우, min(Ri) = 0으로 계산한다
    #모두 같은 값인 경우는? ex) 5 5 5 5 ->  5-5/5-5 연산 불가

    sample = get_output(query).values.tolist()

    # do not change column names
    df = pd.DataFrame(sample, columns=['item', 'prediction'])
    # TODO end

    # Do not change this part
    with open('pbr.txt', 'w') as f:
        f.write(tabulate(df, headers=df.columns, tablefmt='psql', showindex=False))
    print("Output printed in pbr.txt")


# [Algorithm 2] Item-based Recommendation
def ibcf(user_input=True, user_id=None, item_cnt=None):
    if user_input:
        user = int(input('User Id: '))
        rec_num = int(input('Number of recommendations?: '))
    else:
        assert user_id is not None
        assert item_cnt is not None
        user = int(user_id)
        rec_num = int(item_cnt)

    print("=" * 99)
    print(f'Item-based Collaborative Filtering')
    print(f'Recommendations for user {user}')

    # TODO: remove sample, return actual recommendation result as df
    # YOUR CODE GOES HERE !
    # 쿼리의 결과를 sample 변수에 저장하세요.

    query1="SELECT im.item_1 as it1,\
                    IFNULL(sb2.norm_sim,0) as cal_sim,\
                    im.item_2 as it2\
            FROM item_similarity AS im\
            LEFT JOIN(\
                SELECT sb.item_1,\
                        sb.sim,\
                        sb.item_2,\
                        ROUND(sb.sim/SUM(sb.sim) OVER (PARTITION BY item_1),4) AS norm_sim\
                FROM (\
                    SELECT item_1,\
                            sim,\
                            item_2,\
                            ROW_NUMBER() OVER (PARTITION BY item_1 ORDER BY sim DESC, item_2 ASC) AS raking\
                    FROM item_similarity\
                    ) AS sb\
                WHERE sb.raking <= 5\
            ) AS sb2 ON im.item_1 = sb2.item_1 and im.item_2 = sb2.item_2;"    
    mat_item_sim = get_output(query1).pivot(index='it1', columns='it2', values='cal_sim').astype(float)    
    
    query2 = "SELECT r.item AS item, r.user AS user, r.rating AS rating, IFNULL(r.rating,rt.avg_rating) AS cal_rating\
            FROM ratings r\
            LEFT JOIN (\
                SELECT item, AVG(rating) AS avg_rating\
                FROM ratings\
                GROUP BY item\
            ) rt ON r.item = rt.item\
            ORDER BY r.user ASC, r.item ASC;"
    rs = get_output(query2)
    rs.to_csv("check_algo rs.csv")

    mat_rating = rs.pivot(index='item', columns='user', values='cal_rating').astype(float)       
    mat_predict= mat_item_sim.dot(mat_rating).astype(float).round(4)    
    mat_predict.to_csv("check_algo2_predict.csv")

    sort_result = mat_predict[user].sort_values(ascending=False)
    sort_result_user = [user]*rec_num
    sort_result_indices = sort_result.index
    sort_result_predictions = sort_result.tolist()
    sample = list(zip(sort_result_user,sort_result_indices,sort_result_predictions))
    df = pd.DataFrame(sample, columns=['user', 'item', 'prediction']).sort_values(by=['prediction', 'item'], ascending=[False, True])

    df.to_csv('check_algo2.csv')
    #IBCF, UBCF 계산은 모든 아이템을 이용하되, 최종 추천 시 추천 대상 사용자가 이미 평점을 기록한 아이템은 추천 대상에서 제외
    for item_number in df['item'].unique():
        rating = rs.loc[(rs['item'] == item_number) & (rs['user'] == user), 'rating'].values
        if len(rating) == 0 or rating[0] is None:
            pass
        else:
            df.drop(df[df['item'] == item_number].index, inplace=True)
    df = df[:rec_num]
    df.to_csv('check_algo2_remove.csv')
    # TODO end
    # Do not change this part
    with open('ibcf.txt', 'w') as f:
        f.write(tabulate(df, headers=df.columns, tablefmt='psql', showindex=False))
    print("Output printed in ibcf.txt")



# [Algorithm 3] (Optional) User-based Recommendation
def ubcf(user_input=True, user_id=None, item_cnt=None):
    if user_input:
        user = int(input('User Id: '))
        rec_num = int(input('Number of recommendations?: '))
    else:
        assert user_id is not None
        assert item_cnt is not None
        user = int(user_id)
        rec_num = int(item_cnt)

    print("=" * 99)
    print(f'User-based Collaborative Filtering')
    print(f'Recommendations for user {user}')

    # TODO: remove sample, return actual recommendation result as df
    # YOUR CODE GOES HERE !
    # 쿼리의 결과를 sample 변수에 저장하세요.

    query1="SELECT um.user_1 as us1,\
                    IFNULL(sb2.norm_sim,0) as cal_sim,\
                    um.user_2 as us2\
            FROM user_similarity AS um\
            LEFT JOIN(\
                SELECT sb.user_1,\
                        sb.sim,\
                        sb.user_2,\
                        ROUND(sb.sim/SUM(sb.sim) OVER (PARTITION BY user_1),4) AS norm_sim\
                FROM (\
                    SELECT user_1,\
                            sim,\
                            user_2,\
                            ROW_NUMBER() OVER (PARTITION BY user_1 ORDER BY sim DESC, user_2 ASC) AS raking\
                    FROM user_similarity\
                    ) AS sb\
                WHERE sb.raking <= 5\
            ) AS sb2 ON um.user_1 = sb2.user_1 and um.user_2 = sb2.user_2;"    
    mat_user_sim = get_output(query1).pivot(index='us1', columns='us2', values='cal_sim').astype(float)    

    query2 = "SELECT r.item AS item, r.user AS user, r.rating AS rating, IFNULL(r.rating,rt.avg_rating) AS cal_rating\
            FROM ratings r\
            LEFT JOIN (\
                SELECT user, AVG(rating) AS avg_rating\
                FROM ratings\
                GROUP BY user\
            ) rt ON r.user = rt.user\
            ORDER BY r.user ASC, r.item ASC;"
    rs= get_output(query2)    
    mat_rating =rs.pivot(index='item', columns='user', values='cal_rating').astype(float)        
    mat_predict= mat_rating.dot(mat_user_sim.T).astype(float).round(4) 
    
    sort_result = mat_predict[user].sort_values(ascending=False)
    sort_result_user = [user]*rec_num
    sort_result_indices = sort_result.index
    sort_result_predictions = sort_result.tolist()
    sample = list(zip(sort_result_user,sort_result_indices,sort_result_predictions))    
    
    # do not change column names    
    df = pd.DataFrame(sample, columns=['user', 'item', 'prediction']).sort_values(by=['prediction', 'item'], ascending=[False, True])

    #IBCF, UBCF 계산은 모든 아이템을 이용하되, 최종 추천 시 추천 대상 사용자가 이미 평점을 기록한 아이템은 추천 대상에서 제외
    for item_number in df['item'].unique():
        rating = rs.loc[(rs['item'] == item_number) & (rs['user'] == user), 'rating'].values
        if len(rating) == 0 or rating[0] is None:
            pass
        else:
            df.drop(df[df['item'] == item_number].index, inplace=True)
    # TODO end
    df = df[:rec_num]

    # Do not change this part
    with open('ubcf.txt', 'w') as f:
        f.write(tabulate(df, headers=df.columns, tablefmt='psql', showindex=False))
    print("Output printed in ubcf.txt")


## 수정할 필요 없는 함수입니다.
# Print and execute menu 
def menu():
    print("=" * 99)
    print("0. Initialize")
    print("1. Popularity Count-based Recommendation")
    print("2. Popularity Rating-based Recommendation")
    print("3. Item-based Collaborative Filtering")
    print("4. User-based Collaborative Filtering")
    print("5. Exit database")
    print("=" * 99)

    while True:
        m = int(input("Select your action : "))
        if m < 0 or m > 5:
            print("Wrong input. Enter again.")
        else:
            return m

def execute(argv):
    terminated = False
    while not terminated:
        if len(argv)<2:
            m = menu()
            if m == 0:
                # 수정할 필요 없는 함수입니다.
                # Upload prj.sql before this
                # If autocommit=False, always execute after making cursor
                get_dump(connection, 'prj.sql')
            elif m == 1:
                popularity_based_count()
            elif m == 2:
                popularity_based_rating()
            elif m == 3:
                ibcf()
            elif m == 4:
                ubcf()
            elif m == 5:
                terminated = True
            

        # 평가를 위한 코드입니다. 수정하지 마세요.
        else:
            with open(argv[1], 'r') as f:
                lines = f.readlines()
                for line in lines:
                    rec_args = list(map(float, line.split(',')))
                    if len(rec_args) > 1:
                        rec_args[1] = int(rec_args[1])
                    m = rec_args[0]
                    if m==0:
                        get_dump(connection, 'prj.sql')
                    elif m == 1:
                        popularity_based_count(False, *rec_args[1:])
                    elif m == 2:
                        popularity_based_rating(False, *rec_args[1:])
                    elif m == 3:
                        ibcf(False, *rec_args[1:])
                    elif m == 4:
                        ubcf(False, *rec_args[1:])
                    elif m == 5:
                        terminated = True
                    else:
                        print('Invalid menu option')

# DO NOT CHANGE
if __name__ == "__main__":
    execute(sys.argv)
