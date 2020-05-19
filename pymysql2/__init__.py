import pymysql,cgi,sys,threading,time,random

if  sys.version_info < (3,0):
    import HTMLParser
else:
    import html.parser as HTMLParser

def escape_html(s):
 '''
   function to return escaped html string
 '''
 return cgi.escape(s,quote=True)

def unescape_html(s,encoding="utf-8"):
 '''
   function to return unescaped html string
 '''
 return HTMLParser.HTMLParser().unescape(s).encode(encoding)

class session:
 def __init__(self,host,username,password,port=3306,database=None,timeout=5,charset='utf8',autocommit=True,ssl=None):
    self.statement=None
    self.connection = pymysql.connect(host=host,port=port,user=username,password=password,ssl=ssl,database=database,autocommit=autocommit,connect_timeout=timeout,charset=charset)
    self.cursor = self.connection.cursor()
 def reconnect(self):
    self.connection.ping(reconnect=True)
 def set_max_connections(self,*args):
     if args:
      self.statement='''set global max_connections = {}'''.format(pymysql.escape_string(str(int(args[0]))))
     else:
      self.statement='''set global max_connections = 151'''
     self.cursor.execute(self.statement)
 def get_max_connections(self):
     self.statement='''SHOW VARIABLES LIKE "max_connections"'''
     self.cursor.execute(self.statement)
     return int(self.cursor.fetchall()[0][1])
 def set_wait_timeout(self,*args):
     if args:
      self.statement='''set global wait_timeout = {}'''.format(pymysql.escape_string(str(int(args[0]))))
     else:
      self.statement='''set global wait_timeout = 28800'''
     self.cursor.execute(self.statement)
 def get_wait_timeout(self):
     self.statement='''SHOW VARIABLES LIKE "wait_timeout"'''
     self.cursor.execute(self.statement)
     return int(self.cursor.fetchall()[0][1])
 def set_interactive_timeout(self,*args):
     if args:
      self.statement='''set global interactive_timeout = {}'''.format(pymysql.escape_string(str(int(args[0]))))
     else:
      self.statement='''set global interactive_timeout = 28800'''
     self.cursor.execute(self.statement)
 def get_interactive_timeout(self):
     self.statement='''SHOW VARIABLES LIKE "interactive_timeout"'''
     self.cursor.execute(self.statement)
     return int(self.cursor.fetchall()[0][1])
 def set_parameter_value(self,params):
     self.statement='''set global {}'''.format(self.dict_to_str(params,escape=False))
     self.cursor.execute(self.statement)
 def get_parameter_value(self,name):
     self.statement='''SHOW VARIABLES LIKE {}'''.format(self.escape_str(name))
     self.cursor.execute(self.statement)
     return self.cursor.fetchall()
 def is_alive(self):
     return self.connection.open
 def add_parentheses(self,s):
     return " ( "+s+" ) "
 def escape_str(self,s):
     return self.connection.escape(s)
 def dict_to_str(self,data,seperator=' , ',escape=True,parentheses=False):
    if escape==True:
      s= '''{}'''.format(seperator).join(['%s %s' % (key, self.escape_str(value)) for (key, value) in data.items()])
    else:
      s= '''{}'''.format(seperator).join(['%s %s' % (key, value) for (key, value) in data.items()])
    if parentheses==True:
        s=self.add_parentheses(s)
    return s
 def get_colums_format(self,row):
     return ''' , '''.join('{}'.format(pymysql.escape_string(col)) for col in row.keys())
 def get_values_format(self,row):
     return ''' , '''.join(self.escape_str(row[col]) for col in row.keys())
 def close(self):
     self.cursor.close()
     if self.is_alive()==True:
      self.connection.close()
     self.connection=None
     self.cursor=None
     self.statement=None
 def current_version(self):
     self.statement='''select version()'''
     self.cursor.execute(self.statement)
     return self.cursor.fetchall()[0][0]
 def current_user(self):
     self.statement='''select CURRENT_USER()'''
     self.cursor.execute(self.statement)
     return self.cursor.fetchall()[0]
 def change_password(self,user=None,password=""):
     if not user:
         user=self.current_user()[0]
     self.statement='''alter user {} identified by {}'''.format(user,self.escape_str(password))
     self.cursor.execute(self.statement)
 def create_user(self,user,password):
     self.statement='''create user if not exists {} identified by {}'''.format(user,self.escape_str(password))
     self.cursor.execute(self.statement)
 def drop_user(self,user):
     self.statement='''drop user if exists {}'''.format(user)
     self.cursor.execute(self.statement)
 def set_privileges(self,user,priv,db):
     self.statement='''grant {} on {} to {}'''.format(priv,db,user)
     self.cursor.execute(self.statement)
     self.cursor.execute('flush privileges')
 def revoke_privileges(self,user,priv,db):
     self.statement='''revoke {} on {} from {}'''.format(priv,db,user)
     self.cursor.execute(self.statement)
     self.cursor.execute('flush privileges')
 def show_privileges(self,user):
     self.statement='''show grants for {}'''.format(user)
     self.cursor.execute(self.statement)
     return self.cursor.fetchall()
 def create_dbe(self,db):
     self.statement='''create database if not exists {}'''.format(db)
     self.cursor.execute(self.statement)
 def drop_db(self,db):
     self.statement='''drop database if exists {}'''.format(db)
     self.cursor.execute(self.statement)
 def use_db(self,db):
     self.statement='''use {}'''.format(db)
     self.cursor.execute(self.statement)
 def current_db(self):
     self.statement='''select database()'''
     self.cursor.execute(self.statement)
     return self.cursor.fetchall()[0][0]
 def show_dbs(self):
     self.statement='''show databases'''
     self.cursor.execute(self.statement)
     return self.cursor.fetchall()[0]
 def show_tables(self):
     self.statement='''show tables'''
     self.cursor.execute(self.statement)
     return self.cursor.fetchall()[0]
 def describe_table(self,name):
     self.statement='''describe {}'''.format(name)
     self.cursor.execute(self.statement)
     return self.cursor.fetchall()
 def create_table(self,table,fields):
     self.statement='''create table if not exists {} ( {} )'''.format(table,self.dict_to_str(fields,escape=False))
     self.cursor.execute(self.statement)#,{"table":table})
 def rename_table(self,old,new):
     self.statement='''rename table {} to {}'''.format(old,new)#,pymysql.escape_string(new))
     self.cursor.execute(self.statement)#,{"table":table})
 def insert_into_table_format(self,table, row):
     cols = self.get_colums_format(row)
     vals = self.get_values_format(row)
     return '''insert into {} ( {} ) VALUES ( {} )'''.format(table, cols, vals)
 def insert_into_table(self,table,row):
     self.statement=self.insert_into_table_format(table,row)
     self.cursor.execute(self.statement)
 def reset_table(self,table):
     self.statement='''truncate table {}'''.format(table)
     self.cursor.execute(self.statement)#,self.escape_str(table))#,{"table":table})
 def drop_table(self,table):
     self.statement='''drop table if exists {}'''.format(table)
     self.cursor.execute(self.statement)
 def add_column_format(self,table,columns):
     return '''alter table {} add {}'''.format(table,self.dict_to_str(columns,escape=False))
 def add_column(table,columns):
     self.statement=self.add_column_format(table,columns)
     self.cursor.execute(self.statement)
 def drop_column_format(self,table,column):
     return '''alter table {} drop column {}'''.format(table,column)
 def drop_column(table,column):
     self.statement=self.drop_column_format(table,columns)
     self.cursor.execute(self.statement)
 def rename_column_format(self,table,old,new):
     return '''alter table {} change {} {}'''.format(table,old,self.dict_to_str(new,escape=False))
 def rename_column(self,table,old,new):
     self.statement=self.rename_column_format(table,old,new)
     self.cursor.execute(self.statement)
 def modify_column_format(self,table,column):
     return '''alter table {} modify {}'''.format(table,self.dict_to_str(column,escape=False))
 def modify_column(self,table,old,new):
     self.statement=self.modify_column_format(table,old,new)
     self.cursor.execute(self.statement)
 def delete_record(self,table, conditions):
     self.statement=self.delete_record_format(table, conditions)
     self.cursor.execute(self.statement)
 def delete_record_format(self,table, conditions):
     condition=""
     if conditions:
       condition=" where "
       if len(conditions)<2:
          condition+=self.dict_to_str(conditions)
       else:
        for x in conditions:
         if type(x) is dict:
             condition+=self.dict_to_str(x)
         else:
             condition+=" {} ".format(str(x))
     return """delete from {} {}""".format(table,condition)
 def update_table(self,table,rows, conditions):
     self.statement=self.update_column_format(table,rows, conditions)
     self.cursor.execute(self.statement)
 def update_table_format(self,table,rows, conditions):
     row=""
     row+=self.dict_to_str(rows)
     condition=" where "
     if len(conditions)<2:
          condition+=self.dict_to_str(conditions)
     else:
       for x in conditions:
         if type(x) is dict:
             condition+=self.dict_to_str(x)
         else:
             condition+=" {} ".format(str(x))
     return """update {} set {} {}""".format(table,row,condition)#self.dict_to_str(condition,seperator=operator,in_seperator=" = "))
 def select_from_format(self,table,rows,conditions=None,extras=None):
     if extras:
         extra=extras
     else:
         extra=""
     condition=""
     if conditions:
       condition=" where "
       if len(conditions)<2:
          condition+=self.dict_to_str(conditions)
       else:
        for x in conditions:
         if type(x) is dict:
             condition+=self.dict_to_str(x)
         else:
             condition+=" {} ".format(str(x))
     return """select {} from {} {} {}""".format(rows,table,condition,extra)#self.dict_to_str(condition,seperator=operator,in_seperator=" = "))
 def select_from(self,table,rows,conditions=None,extras=None):
     self.statement=self.select_from_format(table,rows,conditions=conditions,extras=extras)
     self.cursor.execute(self.statement)
     return self.cursor.fetchall()
 def execute(self,statement,return_result=True):
     self.cursor.execute(statement)
     if return_result==True:
         return self.cursor.fetchall()

def infos(host="localhost",username="root",password="",port=3306,timeout=5,ssl=None,database=None,autocommit=True,charset='utf8',size=10,max_connections=30,keep_alive=True,check_interval=60,waiting=True):#this function takes those values and return a dict which contains all necessary information to create a telnet session using those following class
  return {"host":host,"username":username,"password":password,"port":port,"timeout":timeout,"ssl":ssl,"database":database,"autocommit":autocommit,"charset":charset,"size":size,"max_connections":max_connections,"keep_alive":keep_alive,"check_interval":check_interval,"waiting":waiting}

class pool:
 def __init__(self,info):#this function takes a list ("hosts" parameter) each element as a dict created by the function "dict_host" and use the information stored on it to create a session object for each ip
  self.pool=[]
  self.check_running=False
  self.used=0
  self.size=0
  self.infos=info
  self.rec=0
  self.stop_conn_check=False
  self.alive=self.infos["keep_alive"]
  self.check_interval=self.infos["check_interval"]
  self.th=None
  if self.infos["size"]>self.infos["max_connections"]:
      self.infos["max_connections"]=self.infos["size"]
  for x in range(self.infos["size"]):
    t=threading.Thread(target=self.connect_to_host)#we are using threads to speed things up and connect to all hosts in a very short time (few seconds)
    t.start()
    time.sleep(0.001)
  while (self.size<self.infos["size"]):# and (self.size<self.infos["max_connections"] ):
      time.sleep(.01)
  if self.alive==True:
    self.start_check()
 def connect_to_host(self):#connect to a single host it takes the "host_dict" 's returned value and save the ip and the session on the "self.sessions" variable 
  try:
   t=session(self.infos["host"],self.infos["username"],self.infos["password"],timeout=self.infos["timeout"],ssl=self.infos["ssl"],database=self.infos["database"],port=self.infos["port"],autocommit=self.infos["autocommit"],charset=self.infos["charset"])
   self.pool.append(t)
  except Exception as e:
   pass
  self.size+=1
 def get_connection(self,timeout=5):
  if len(self.pool)==0:
      if self.size==self.infos["max_connections"]:
        if self.infos["waiting"]==False:
            raise Exception("Maximum number of connections has been reached")
        else:
         ti=time.time()
         while(len(self.pool)==0):
              if int(time.time()-ti)==timeout:
                  raise Exception("Timed out")
              time.sleep(0.1)
         x=random.choice(self.pool)
         if x.is_alive()==False:
             x.reconnect()
         self.pool.remove(x)
         self.used+=1
         return x
      else:
          self.connect_to_host()
          x=random.choice(self.pool)
          if x.is_alive()==False:
             x.reconnect()
          self.pool.remove(x)
          self.used+=1
          return x
  else:
      x=random.choice(self.pool)
      if x.is_alive()==False:
             x.reconnect()
      self.pool.remove(x)
      self.used+=1
      return x
 def start_check(self):
     if self.check_running==False:
      self.th=threading.Thread(target=self.keep_alive).start()
 def stop_check(self):
     self.check_running=False
     self.stop_conn_check=True
     del self.th
 def keep_alive(self):
    self.stop_conn_check=False
    while True:
     if self.stop_conn_check==True:
         break
     self.reconnect_all()
     ti=time.time()
     while True:
         if int(time.time()-ti)==self.check_interval:
             break
         if self.pool==None:
             self.stop_conn_check=True
             break
         if self.stop_conn_check==True:
             break
         time.sleep(0.01)
 def reconnect_all(self):
    if self.pool:
      if len(self.pool)>0:
       self.rec=0
       for x in self.pool:
         threading.Thread(target=self.reconnect_one,args=(x,)).start()
       while (self.rec<len(self.pool)):
          time.sleep(0.01)
 def reconnect_one(self,con):
     con.reconnect()
     self.rec+=1
 def close_connection(self,con):
     self.pool.append(con)
     self.size+=1
     self.used-=1
 def kill_connection(self,con):
     con.close()
     del con
     self.size-=1
 def destroy(self):
     for x in self.pool:
         x.close()
         self.pool.remove(x)
         del x
     self.pool=None
     self.used=None
     self.size=None
     self.infos=None
     self.rec=None
     self.stop_check()
     self.check_interval=None
     self.stop_conn_check=None
