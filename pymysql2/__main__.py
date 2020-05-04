import sys
if  sys.version_info < (3,0):
    input=raw_input
from pymysql2.__init__ import session
l=sys.argv
if len(l)<5:
    print("""

Usage:

xmysql host:port username password database [commands...]

Examples:

xmysql localhost:3306 root "" test

xmysql localhost root root test "select username,password from users"

""")
    sys.exit()
if ":" in l[1]:  
  host=l[1].split(':')[0]
  port=int(l[1].split(':')[1])
else:
    host=l[1]
    port=3306
username=l[2]
password=l[3]
database=l[4]
commands=[]
if len(l)>5:
  for x in range(5,len(l)):
    commands.append(l[x])
def run():
 try:
  s=session(host,port,username,password,database)
  if len(commands)>0:
      for i in commands:
        try:
          r=s.execute(i)
          for x in r:
             print(x)
        except Exception as xc:
          print(xc)
      s.close()
      sys.exit()
  else:
   while True:
    try:
      cmd=input("mysql> ")
      if (cmd.lower().strip()in ["exit","quit"]):
        s.close()
        sys.exit()
      r=s.execute(cmd)
      for x in r:
          print(x)
    except KeyboardInterrupt:
        s.close()
        sys.exit()
    except Exception as e:
        print(e)
 except Exception as ex:
  print(ex)
  sys.exit()

run()
