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
USER = "DS2024_0028"
PASSWD = "DS2024_0028"
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
    query=f"""select item, count(rating) as count
            from ratings 
            where rating is not null 
            group by item 
            having item >= 150 and item < 350
            order by count(rating) desc, item asc
            limit {rec_num}"""

    # do not change column names
    df=get_output(query)

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
    query=f"""
        select item, round(avg((rating-min_rating)/(max_rating-min_rating)),4) as avg_rating
        
        from ratings natural join
        (select user,max(rating) as max_rating,
            case
                when count(rating) = 1 then 0
                else min(rating)
            end as min_rating
        from ratings group by user) as min_max_table
        
        group by item
        
        having item >= 150 and item < 350
        
        order by avg_rating desc, item
        
        limit {rec_num}
        """

    # do not change column names
    df=get_output(query)
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
    query_sim="""
        select item_1, item_2, round(sim/sum(sim) over (partition by item_1),4) as normed_sim
        from item_similarity natural join
        (select item_1,item_2,row_number() over (partition by item_1 order by sim desc, item_2) as sim_ranking
        from item_similarity) as sim_ranking_table
        where sim_ranking_table.sim_ranking <= 5
        """
    df_similarity=get_output(query_sim)

    query_rating=f"""
        select user,item,
        case 
        when rating is null then round(avg(rating) over (partition by user),4)
        else round(rating,4)
        end as rating_null_filled
        from ratings
        """
    df_rating=get_output(query_rating)
    
    query_user_notrated=f"""
        select item
        from ratings
        where user={user} and rating is null
        """
    df_user_notrated=get_output(query_user_notrated)
    
    scores=[]
    unique_item=df_similarity.values[:,0][::5]
    df_rating_user=df_rating[df_rating['user']==user]
    for i_unique_item in unique_item:
        i_similarity=df_similarity[df_similarity['item_1']==i_unique_item]
        i_rating=df_rating_user[df_rating_user['item'].isin(i_similarity['item_2'])]
        i_score=i_similarity.values[:,-1].astype(float)*i_rating.values[:,-1].astype(float)
        scores.append(round(i_score.sum(),4))
    
    rank_dict={'item':unique_item,'scores':scores}
    df_rank=pd.DataFrame(rank_dict)
    df_rank=df_rank[df_rank['item'].isin(df_user_notrated['item'])]
    df_rank=df_rank.sort_values(by=['scores','item'],ascending=[False,True])

    df=df_rank[:rec_num]    
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
    query_sim="""
        select user_1, user_2, round(sim/sum(sim) over (partition by user_1),4) as normed_sim
        from user_similarity natural join
        (select user_1,user_2,row_number() over (partition by user_1 order by sim desc, user_2) as sim_ranking
        from user_similarity) as sim_ranking_table
        where sim_ranking_table.sim_ranking <= 5
        """
    df_similarity=get_output(query_sim)
    df_similarity_user=df_similarity[df_similarity['user_1']==user]

    query_rating=f"""
        select user,item,
        case 
        when rating is null then round(avg(rating) over (partition by user),4)
        else round(rating,4)
        end as rating_null_filled
        from ratings
        """
    df_rating=get_output(query_rating)
    
    query_user_notrated=f"""
        select item
        from ratings
        where user={user} and rating is null
        """
    df_user_notrated=get_output(query_user_notrated)
    
    scores=[]
    unique_item=df_rating[df_rating['user']==0]['item']
    for i_unique_item in unique_item:
        i_similarity=df_rating[df_rating['item']==i_unique_item]
        i_rating=i_similarity[i_similarity['user'].isin(df_similarity_user['user_2'])]
        i_score=df_similarity_user.values[:,-1].astype(float)*i_rating.values[:,-1].astype(float)
        scores.append(round(i_score.sum(),4))
        
    rank_dict={'item':unique_item,'scores':scores}
    df_rank=pd.DataFrame(rank_dict)
    df_rank=df_rank[df_rank['item'].isin(df_user_notrated['item'])]
    df_rank=df_rank.sort_values(by=['scores','item'],ascending=[False,True])
    print (df_rank.shape)
    df=df_rank[:rec_num]
    # TODO end

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
