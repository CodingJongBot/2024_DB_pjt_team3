import usercode1
import usercode2

def run_test(step_user=100,step_rec_num=100,tc=1):
    with open('testresult.txt','w') as init:
        init.write("################################\n")
        init.write("########   Test Start   ########\n")
        init.write("################################\n")

    for uid in range(0,292,step_user):
        for rec_num in range(0,453,step_rec_num):
            with open('testresult.txt','a') as rs:
                rs.write(f'uid: {uid} / rec_num: {rec_num} / result: ')
                err_cnt=0

                usercode1.popularity_based_count(False,rec_num)
                with open("pbc.txt") as f:
                    pbc1 = f.read()
                usercode2.popularity_based_count(False,rec_num)
                with open("pbc.txt") as f:
                    pbc2 = f.read()
                if(pbc1 != pbc2):
                    err_cnt +=1
                    rs.write("|pbc - Fail|")
                
                if(tc>1):
                    usercode1.popularity_based_rating(False,rec_num)
                    with open("pbr.txt") as f:
                        pbr1 = f.read()
                    usercode2.popularity_based_count(False,rec_num)
                    with open("pbr.txt") as f:
                        pbr2 = f.read()
                    if(pbr1 != pbr2):
                        err_cnt +=1
                        rs.write("|pbr - Fail|")

                if(tc>2):
                    usercode1.ibcf(False,uid,rec_num)
                    with open("ibcf.txt") as f:
                        ibcf1 = f.read()
                    usercode2.ibcf(False,uid,rec_num)
                    with open("ibcf.txt") as f:
                        ibcf2 = f.read()    
                    if(ibcf1 != ibcf2):
                        err_cnt +=1
                        rs.write("|ibcf - Fail|")
                if(tc>3):
                    usercode1.ubcf(False,uid,rec_num)
                    with open("ibcf.txt") as f:
                        ubcf1 = f.read()  
                    usercode2.ubcf(False,uid,rec_num)
                    with open("ibcf.txt") as f:
                        ubcf2 = f.read()    
                    if(ubcf1 != ubcf2):
                        err_cnt +=1
                        rs.write("|ubcf - Fail|")
                if err_cnt==0:
                    rs.write("All Pass")
                rs.write("\n")

# 1. Prepare your code (code1, code2)
# 2. Rename file usercode1.py, usercode2.py
# 3. Place all file in same director (testcode.py, usercode1.py, usercode2.py)
# 4. Set test Parameter                      
if __name__ == "__main__":
    step_user = 100
    step_rec_num = 200
    tc = 2 #tc is test function number(1 is only pbc)
    run_test(step_user,step_rec_num,tc)