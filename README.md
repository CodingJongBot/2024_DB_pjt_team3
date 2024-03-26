## Check List
1. 같은 input값 넣어서 다른 사람들 결과랑 비교
2. SQL query Logic 문제 없는지
3. SQL query후 결과가 원하는 형태로 정렬되어 결과에 영향을 안 미치는지


#명세서 확인 후 아래 내용 반영 필요 (너무 다름)
-algo 1-1,1-2
1) Popularity 계산은 모든 아이템을 이용하되, 최종 추천은 번호가 150 이상 350 미만인 item중에서 입력된 개수만큼 선택 
2) 계산은 소수점 아래 4자리까지 반올림한다. *SQL: ROUND(x, 4) 

-algo 2, 3
1) 유사도 계산에 쓰이는 이웃 유저 혹은 아이템의 수 K는 5로 계산 (k fix)
2) 추천 대상 사용자는 단일 사용자로 가정
3) IBCF, UBCF 계산은 모든 아이템을 이용하되, 최종 추천 시 추천 대상 사용자가 이미 평점을 기록한 아이템은 추천 대상에서 제외 
->이미 존재한 값은 빼야함.
4) 계산은 소수점 아래 4자리까지 반올림한다. *SQL: ROUND(x, 4) 
5) 출력 순서: prediction기준 내림차순, prediction 값이 동일한 아이템이 있을 경우 item 번호가 작은 것부터 오름차순 출력




*Test - Algo2 행렬곱까지 단일 Query(속도문제)

SELECT que2.user as sol_user, que1.it1 as sol_item, SUM(que1.cal_sim * que2.cal_rating) AS sol_predict
FROM (SELECT im.item_1 as it1,
            IFNULL(sb2.norm_sim,0) as cal_sim,
            im.item_2 as it2
    FROM item_similarity AS im
    LEFT JOIN(
        SELECT sb.item_1,
                sb.sim,
                sb.item_2,
                ROUND(sb.sim/SUM(sb.sim) OVER (PARTITION BY item_1),4) AS norm_sim
        FROM (
            SELECT item_1,
                    sim,
                    item_2,
                    ROW_NUMBER() OVER (PARTITION BY item_1 ORDER BY sim DESC, item_2 ASC) AS raking
            FROM item_similarity
            ) AS sb
        WHERE sb.raking <= 5
    ) AS sb2 ON im.item_1 = sb2.item_1 and im.item_2 = sb2.item_2) AS que1
JOIN (
        SELECT r.item AS item, r.user AS user, r.rating AS rating, IFNULL(r.rating,rt.avg_rating) AS cal_rating
        FROM ratings r
        LEFT JOIN (
            SELECT item, AVG(rating) AS avg_rating
            FROM ratings
            GROUP BY item
        ) rt ON r.item = rt.item
        ORDER BY r.user ASC, r.item ASC) AS que2
ON que1.it2 = que2.item
GROUP BY que1.it1,que2.user;