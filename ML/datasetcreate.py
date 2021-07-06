import subprocess 
#, "-o" ,"./outputs/51.out" ,"-g",
ans=[]
for i in range(998):
    try:
        prr="./c++programs/"+(str)(i)+".cpp"
        crr="./outputs/"+(str)(i)+".out"
        p1= subprocess.Popen(["g++","-g",prr,"-o" ,crr],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p1.wait()
        p2=subprocess.Popen([crr],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p2.wait()
        prr="./cores/core_"+(str)(i)+".out"
        crr="./coress/core_"+(str)(i)+".core"
        p3=subprocess.Popen(["cp",prr,crr],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p3.wait()
        print(i)

    except :
        ans.append(i)
        pass
        
print(ans)    

    
#p1= subprocess.Popen(["g++","-g","./c++programs/52.cpp","-o" ,"./outputs/52.out"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#p1.wait()
#print(p1.stderr.readlines())
#p2=subprocess.Popen(["./outputs/51.out"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#print(p2.stderr.readlines())
#p2.wait()

#p3=subprocess.Popen(["cp","/tmp/core_51.out","./core_51.core"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#p3.wait()