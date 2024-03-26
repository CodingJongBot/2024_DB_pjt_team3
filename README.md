## Check List
1. 각 Algorithm Test 할때마다 (0) Initialize 해주는지 -> initialize는 보장하지 않음. + DB Table을 건드려서 value를 바꾸면 안됨
2. 3,4번 알고리즘에서 rec_num, rec_cnt 정확한 의미 확인 -> 질문 했음
3. 같은 input값 넣어서 다른 사람들 결과랑 비교
4. SQL query Logic 문제 없는지
5. SQL query후 결과가 원하는 형태로 정렬되어 결과에 영향을 안 미치는지
6. input되는 Similarity 값 항상 정방행렬인지 (아니라면 index swap해서 입력) -> symmetric하지 않음. 즉 user[0] -> user[2] sim 값과, user[2] -> user[0]의 값은 다를 수 있음.
