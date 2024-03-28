import usercode1
import usercode2

def run_test(tc=1,step_user=100,max_user=292,rec_num=453):
    with open('testresult.txt','w') as init:
        init.write("################################\n")
        init.write("########   Test Start   ########\n")
        init.write("################################\n")

    for uid in range(0,max_user,step_user):
        
        with open('testresult.txt','a') as rs:
            rs.write(f'# uid: {uid} / rec_num: {rec_num} / result: ')
            err_cnt=0

            usercode1.popularity_based_count(False,rec_num)
            with open("pbc.txt") as f:
                pbc1 = f.readlines()

            usercode2.popularity_based_count(False,rec_num)
            with open("pbc.txt") as f:
                pbc2 = f.readlines()
            err_flag=0
            for i in range(len(pbc1)):
                if(len(pbc1) != len(pbc2)):
                    err_cnt +=1
                    if(err_flag==0):
                        rs.write("|pbc - Fail|")
                        err_flag=1
                        rs.write(" pbc length diff.")
                    break
                elif(pbc1[i] != pbc2[i]):
                    err_cnt +=1
                    if(err_flag==0):
                        rs.write("\n|pbc - Fail|\n")
                        err_flag=1
                    rs.write('------------------------------------------------------------------------\n')
                    rs.write('code1: '+pbc1[i])
                    rs.write('code2: '+pbc2[i])
            
            if(tc>1):
                usercode1.popularity_based_rating(False,rec_num)
                with open("pbr.txt") as f:
                    pbr1 = f.readlines()
                usercode2.popularity_based_count(False,rec_num)
                with open("pbr.txt") as f:
                    pbr2 = f.readlines()
                err_flag=0
                for i in range(len(pbr1)):
                    if(len(pbr1) != len(pbr2)):
                        err_cnt +=1
                        if(err_flag==0):
                            rs.write("|pbr - Fail|")
                            err_flag=1
                            rs.write(" pbr length diff.")
                        break
                    elif(pbr1[i] != pbr2[i]):
                        err_cnt +=1
                        if(err_flag==0):
                            rs.write("\n|pbr - Fail|\n")
                            err_flag=1
                        rs.write('------------------------------------------------------------------------\n')
                        rs.write('code1: '+pbr1[i])
                        rs.write('code2: '+pbr2[i])

            if(tc>2):
                usercode1.ibcf(False,uid,rec_num)
                with open("ibcf.txt") as f:
                    ibcf1 = f.readlines()
                usercode2.ibcf(False,uid,rec_num)
                with open("ibcf.txt") as f:
                    ibcf2 = f.readlines()    
                err_flag=0
                for i in range(len(ibcf1)):
                    if(len(ibcf1) != len(ibcf2)):
                        err_cnt +=1
                        if(err_flag==0):
                            rs.write("|ibcf - Fail|")
                            err_flag=1
                            rs.write(" ibcf length diff.")                        
                        break
                    elif(ibcf1[i] != ibcf2[i]):
                        err_cnt +=1
                        if(err_flag==0):
                            rs.write("\n|ibcf - Fail|\n")
                            err_flag=1
                        rs.write('------------------------------------------------------------------------\n')
                        rs.write('code1: '+ibcf1[i])
                        rs.write('code2: '+ibcf2[i])

            if(tc>3):
                usercode1.ubcf(False,uid,rec_num)
                with open("ubcf.txt") as f:
                    ubcf1 = f.readlines()  
                usercode2.ubcf(False,uid,rec_num)
                with open("ubcf.txt") as f:
                    ubcf2 = f.readlines()  
                err_flag = 0      
                for i in range(len(ubcf1)):
                    if(len(ubcf1) != len(ubcf2)):
                        err_cnt +=1                        
                        if(err_flag==0):
                            rs.write("|ubcf - Fail|")
                            err_flag=1
                            rs.write(" ubcf length diff.")                        
                        break
                    elif(ubcf1[i] != ubcf2[i]):
                        err_cnt +=1
                        if(err_flag==0):
                            err_flag=1
                            rs.write("\n|ubcf - Fail|\n")
                        rs.write('------------------------------------------------------------------------\n')
                        rs.write('code1: '+ubcf1[i])
                        rs.write('code2: '+ubcf2[i])

            if err_cnt==0:
                rs.write("All Pass")
            rs.write("\n")
    with open('testresult.txt','a') as init:
        init.write("################################\n")
        init.write("#########   Test End   #########\n")
        init.write("################################\n")

        
# 1. Prepare your code (code1, code2)
# 2. Rename file usercode1.py, usercode2.py
# 3. Place all file in same director (testcode.py, usercode1.py, usercode2.py)
# 4. Set test Parameter                      
if __name__ == "__main__":
    tc = 4 #tc is test function number(1 is only pbc)
    step_user = 11    
    # step_rec_num = 453
    max_user=292
    max_item=453
    run_test(tc,step_user,max_user,max_item)