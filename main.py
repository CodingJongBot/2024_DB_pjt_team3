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
    autocommit=True,  # to create table permanently
)

cur = connection.cursor(dictionary=True)


## 수정할 필요 없는 함수입니다.
# DO NOT CHANGE INITIAL TABLES IN prj.sql
def get_dump(mysql_con, filename):
    """
    connect to mysql server using mysql_connector
    load .sql file (filename) to get queries that create tables in an existing database (fma)
    """
    query = ""
    try:
        with mysql_con.cursor() as cursor:
            for line in open(filename, "r"):
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


'''
## 비개인화 추천 알고리즘 (모든 사용자에게 동일한 아이템을 추천)
: 과거 데이터를 기반으로 사용자로부터 평점을 가장 많이 부여 받은 아이템을 추천

Popularity by rating count
1. 사용자가 아이템에 부여한 평점들로 구성된 데이터를 불러온다
2. 각 아이템에 평점을 부여한 사용자 수를 확인한다.
3. 가장 많은 평점을 부여 받은 아이템 n개를 추천한다
'''
# [Algorithm 1] Popularity-based Recommendation - 1 : Popularity by rating count
def popularity_based_count(user_input=True, item_cnt=None):
    if user_input:
        rec_num = int(input("Number of recommendations?: "))
    else:
        assert item_cnt is not None
        rec_num = int(item_cnt)
    print(f"Popularity Count based recommendation")
    print("=" * 99)

    # TODO: remove sample, return actual recommendation result as df
    # YOUR CODE GOES HERE !
    # 쿼리의 결과를 sample 변수에 저장하세요.
    query = (
        "SELECT r.item, COUNT(r.user) as count\
            FROM ratings r\
            WHERE r.rating is not NULL\
            GROUP BY r.item\
            ORDER BY COUNT(r.user) DESC\
            LIMIT "
        + str(rec_num)
    )
    sample = get_output(query).values.tolist()

    # do not change column names
    df = pd.DataFrame(sample, columns=["item", "count"])
    # TODO end

    # Do not change this part
    with open("pbc.txt", "w") as f:
        f.write(tabulate(df, headers=df.columns, tablefmt="psql", showindex=False))
    print("Output printed in pbc.txt")


'''
## 비개인화 추천 알고리즘 (모든 사용자에게 동일한 아이템을 추천)
: 과거 데이터를 기반으로 사용자로부터 평점을 가장 많이 부여 받은 아이템을 추천

average rating
1. 사용자가 아이템에 부여한 평점들로 구성된 데이터를 불러온다
2. 사용자마다 평점을 부여하는 경향성이 다르기 때문에, 평점을 보정한다. 각 사용자마다 최저 평점이 0, 최고 평점이 1이 되도록 보정한다.
3. 보정됨 평점을 기반으로 각 아이템마다 사용자들이 부여한 평점의 평균을 구한다.  
4. 가장 높은 평균 평점을 부여 받은 아이템 n개를 추천한다.
'''
# [Algorithm 1] Popularity-based Recommendation - 2 : Popularity by average rating
def popularity_based_rating(user_input=True, item_cnt=None):
    if user_input:
        rec_num = int(input("Number of recommendations?: "))
    else:
        assert item_cnt is not None
        rec_num = int(item_cnt)
    print(f"Popularity Rating based recommendation")
    print("=" * 99)

    # TODO: remove sample, return actual recommendation result as df
    # YOUR CODE GOES HERE !
    # 쿼리의 결과를 sample 변수에 저장하세요.
    query = "SELECT sb2.item, AVG(sb2.norm_rating) as avg_norm_rating\
            FROM (SELECT rt.item, ((rt.rating-sb.min_rating)/sb.rating_range) as norm_rating\
                FROM \
                (SELECT r.user, MAX(r.rating) as max_rating, MIN(r.rating) as min_rating ,MAX(r.rating) - MIN(r.rating) as rating_range\
                    FROM ratings r\
                    WHERE r.rating is not NULL\
                    GROUP BY r.user) AS sb\
                JOIN ratings rt ON rt.user = sb.user\
            ) AS sb2\
            GROUP BY sb2.item\
            ORDER BY AVG(sb2.norm_rating) DESC\
            LIMIT "+ str(rec_num)

    sample = get_output(query).values.tolist()
    # do not change column names
    df = pd.DataFrame(sample, columns=["item", "prediction"])
    # TODO end

    # Do not change this part
    with open("pbr.txt", "w") as f:
        f.write(tabulate(df, headers=df.columns, tablefmt="psql", showindex=False))
    print("Output printed in pbr.txt")


'''
## 개인화 추천 알고리즘 (사용자마다 서로 다른 아이템을 추천)
: 과거 데이터를 기반으로, 내가 좋아한 아이템과 유사한 아이템을 추천한다.

Item-based Collaborative Filtering
1. 아이템-사용자 평점 데이터와 아이템-아이템 유사도 데이터를 불러온다.
2. 아이템마다 가장 유사도가 높은 이웃 K개를 구한다. 만약 유사도가 같은 경우, 번호가 작은 아이템을 선택한다.
3. 유사도는 예측 평점을 계산할 때 이웃들을 반영하는 비율을 나타낸다. 그러므로, 유사도를 모두 더하면 1.0 (100%) 이 되도록 보정한다.
4. 아이템-사용자 평점 데이터의 빈 공간을 각 아이템의 평균 평점으로 채운다
5. 보정된 아이템-아이템 유사도 행렬과, 아이템-사용자 평점 행렬을 곱해서 예측 평점을 구한다
'''
# [Algorithm 2] Item-based Recommendation
def ibcf(user_input=True, user_id=None, rec_threshold=None, rec_max_cnt=None):
    if user_input:
        user = int(input("User Id: "))
        rec_cnt = int(input("Recommend Count: "))
        rec_num = float(input("Recommendation Threshold: "))
    else:
        assert user_id is not None
        assert rec_max_cnt is not None
        assert rec_threshold is not None
        user = int(user_id)
        rec_cnt = int(rec_max_cnt)
        rec_num = float(rec_threshold)

    print("=" * 99)
    print(f"Item-based Collaborative Filtering")
    print(f"Recommendations for user {user}")

    # TODO: remove sample, return actual recommendation result as df
    # YOUR CODE GOES HERE !
    # 쿼리의 결과를 sample 변수에 저장하세요.

    # item별 유사도(정규화) 상위 k개
    query1 = "SELECT sb.item_1,sb.sim,sb.item_2,sb.sim/SUM(sb.sim) OVER (PARTITION BY item_1) as norm_sim\
            FROM (SELECT item_1,sim,item_2,ROW_NUMBER() OVER (PARTITION BY item_1 ORDER BY sim DESC, item_2 ASC) AS raking\
                FROM item_similarity) as sb\
            WHERE sb.raking <="+ str(rec_num)
    rs1 = get_output(query1)

    # update null value its average
    query2 = "UPDATE ratings rt\
            JOIN (\
                SELECT item, AVG(rating) as avg_rating\
                FROM ratings\
                GROUP BY item\
            ) rs ON rt.item = rs.item\
            SET rt.rating = rs.avg_rating\
            WHERE rt.rating IS NULL;"
    rs2 = get_output(query2)

    # Read item user rating(updated)
    query3 = "SELECT r.item AS item, r.user AS user, r.rating AS rating\
            FROM ratings r\
            ORDER BY r.user ASC, r.item ASC"    
    

    # change Query
    # query3 = "SELECT r.item AS item, r.user AS user, IFNULL(r.rating,rt.avg_rating) AS rating\
    #         FROM ratings r\
    #         LEFT JOIN (\
    #             SELECT item, AVG(rating) AS avg_rating\
    #             FROM ratings\
    #             GROUP BY item\
    #         ) rt ON r.item = rt.item\
    #         ORDER BY r.user ASC, r.item ASC;"



    mat_rating = get_output(query3).pivot(index='item', columns='user', values='rating').astype(float)    
    
    # 1. Num_row / rec_num -> item 수 확인 가능 -> 예제에서는 453개의 item
    row_count = int((rs1.shape[0])/rec_num)

    # 2. 0으로 초기화된 size(453) x size(453) df만들고
    temp_df = pd.DataFrame(0, index=range(row_count), columns=range(row_count)).values[:, :].astype(float)
    
    # 3. item1과 유사한 rec_num개의 item2의 값(index)를 만든 df에 값 삽입(총 item수 x rec_num번)
    items = rs1.values[:,:].astype(float)
    for item in items :
        temp_df[int(item[0])][int(item[2])] = item[3]
    mat_item_sim = pd.DataFrame(temp_df).astype(float)

    # 4. 행렬곱 연산 (item x item similarity 행렬 @ item x user rating 행렬)
    mat_predict= mat_item_sim.dot(mat_rating)

    # 5. 구한 행렬로 가장 높은 평균 평점을 부여 받은 아이템 n개를 추천한다.
    sort_result = mat_predict[user].sort_values(ascending=False).head(rec_cnt)    
    sort_result_user = [user]*rec_cnt
    sort_result_indices = sort_result.index
    sort_result_predictions = sort_result.tolist()
    sample = list(zip(sort_result_user,sort_result_indices,sort_result_predictions))
    
    # do not change column names
    df = pd.DataFrame(sample, columns=["user", "item", "prediction"])
    # TODO end

    # Do not change this part
    with open("ibcf.txt", "w") as f:
        f.write(tabulate(df, headers=df.columns, tablefmt="psql", showindex=False))
    print("Output printed in ibcf.txt")

'''
(Optional) User-based Collaborative Filtering
## 개인화 추천 알고리즘 (사용자마다 서로 다른 아이템을 추천)
: 과거 데이터를 기반으로, 나와 유사한 (취향이 비슷한) 사용자들이 높은 평점을 부여한 아이템
들을 추천한다
1. 아이템-사용자 평점 데이터와 사용자-사용자 유사도 데이터를 불러온다
2. 사용자마다 가장 유사도가 높은 이웃 K개를 구한다. 만약 유사도가 같은 경우, 번호가 작은 사용자를 선택한다.
3. 유사도는 예측 평점을 계산할 때 이웃들을 반영하는 비율을 나타낸다. 그러므로, 유사도를 모두 더하면 1.0 (100%) 이 되도록 보정한다.
4. 아이템-사용자 평점 데이터의 빈 공간을 각 사용자의 평균 평점으로 채운다.
5. 보정된 사용자-사용자 유사도 행렬과, 아이템-사용자 평점 행렬을 곱해서 예측 평점을 구한다.
'''
# [Algorithm 3] (Optional) User-based Recommendation
def ubcf(user_input=True, user_id=None, rec_threshold=None, rec_max_cnt=None):
    if user_input:
        user = int(input("User Id: "))
        rec_cnt = int(input("Recommend Count: "))
        rec_num = float(input("Recommendation Threshold: "))
    else:
        assert user_id is not None
        assert rec_max_cnt is not None
        assert rec_threshold is not None
        user = int(user_id)
        rec_cnt = int(rec_max_cnt)
        rec_num = float(rec_threshold)

    print("=" * 99)
    print(f"User-based Collaborative Filtering")
    print(f"Recommendations for user {user}")

    # TODO: remove sample, return actual recommendation result as df
    # YOUR CODE GOES HERE !
    # 쿼리의 결과를 sample 변수에 저장하세요.

    query1="SELECT sb.user_1,sb.sim,sb.user_2,sb.sim/SUM(sb.sim) OVER (PARTITION BY user_1) as norm_sim\
            FROM (SELECT user_1,sim,user_2,ROW_NUMBER() OVER (PARTITION BY user_1 ORDER BY sim DESC, user_2 ASC) AS raking\
                FROM user_similarity) as sb\
            WHERE sb.raking <="+str(rec_num)
    rs1 = get_output(query1)

    query2 = "UPDATE ratings rt\
            JOIN (\
                SELECT user, AVG(rating) as avg_rating\
                FROM ratings\
                GROUP BY user\
            ) rs ON rt.user = rs.user\
            SET rt.rating = rs.avg_rating\
            WHERE rt.rating IS NULL;"
    rs2 = get_output(query2)


    # Read item user rating(updated)
    query3 = "SELECT r.item AS item, r.user AS user, r.rating AS rating\
            FROM ratings r\
            ORDER BY r.user ASC, r.item ASC"    
    
    # change Query
    # query3 = "SELECT r.item AS item, r.user AS user, IFNULL(r.rating,rt.avg_rating) AS rating\
    #         FROM ratings r\
    #         LEFT JOIN (\
    #             SELECT user, AVG(rating) AS avg_rating\
    #             FROM ratings\
    #             GROUP BY user\
    #         ) rt ON r.user = rt.user\
    #         ORDER BY r.user ASC, r.item ASC;"

    mat_rating = get_output(query3).pivot(index='item', columns='user', values='rating').astype(float)    
    
    # 1. Num_row / rec_num -> item 수 확인 가능 -> 예제에서는 292개의 user
    row_count = int((rs1.shape[0])/rec_num)

    # 2. 0으로 초기화된 size(292) x size(292) df만들고
    temp_df = pd.DataFrame(0, index=range(row_count), columns=range(row_count)).values[:, :].astype(float)
    
    # 3. user1과 유사한 rec_num개의 user2의 값(index)를 만든 df에 값 삽입(총 user수 x rec_num번)
    users = rs1.values[:,:].astype(float)
    for u in users :
        temp_df[int(u[0])][int(u[2])] = u[3]
    mat_user_sim = pd.DataFrame(temp_df).astype(float)
    
    
    # 4. 행렬곱 연산 (item x user rating 행렬 @ user x user similarity 행렬)
    mat_predict= mat_rating.dot(mat_user_sim.T) # need Transpose
    
    # 5. 구한 행렬로 가장 높은 평균 평점을 부여 받은 아이템 n개를 추천한다.
    sort_result = mat_predict[user].sort_values(ascending=False).head(rec_cnt)    
    sort_result_user = [user]*rec_cnt
    sort_result_indices = sort_result.index
    sort_result_predictions = sort_result.tolist()
    sample = list(zip(sort_result_user,sort_result_indices,sort_result_predictions))

    # do not change column names
    df = pd.DataFrame(sample, columns=["user", "item", "prediction"])
    # TODO end

    # Do not change this part
    with open("ubcf.txt", "w") as f:
        f.write(tabulate(df, headers=df.columns, tablefmt="psql", showindex=False))
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
        if len(argv) < 2:
            m = menu()
            if m == 0:
                # 수정할 필요 없는 함수입니다.
                # Upload prj.sql before this
                # If autocommit=False, always execute after making cursor
                get_dump(connection, "prj.sql")
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
            with open(argv[1], "r") as f:
                lines = f.readlines()
                for line in lines:
                    rec_args = list(map(float, line.split(",")))
                    if len(rec_args) > 1:
                        rec_args[1] = int(rec_args[1])
                    m = rec_args[0]
                    if m == 0:
                        get_dump(connection, "prj.sql")
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
                        print("Invalid menu option")


# DO NOT CHANGE
if __name__ == "__main__":
    execute(sys.argv)
