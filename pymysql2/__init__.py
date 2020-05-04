import pymysql,cgi,sys

if  sys.version_info < (3,0):
    import HTMLParser
else:
    import html.parser as HTMLParser

def escape_html(s):
 '''
   function to return escaped html string
 '''
 return cgi.escape(s,quote=True).replace(':','&#58;')

def unescape_html(s):
 '''
   function to return unescaped html string
 '''
 return HTMLParser.HTMLParser().unescape(s).encode("utf-8")

class session:
 def __init__(self,host,port,username,password,database):
    self.statement=None
    self.connection = pymysql.connect(host=host,port=port,user=username,password=password,database=database,autocommit=True)#,database=creds["database"])
    self.cursor = self.connection.cursor()
 def add_parentheses(self,s):
     return " ( "+s+" ) "
 def escape_str(self,s):
     return self.connection.escape(s)
 def dict_to_str(self,data,seperator=" , ",escape=True,in_seperator=" ",parentheses=False):
    if escape==True:
     s= '''{}'''.format(seperator).join(['%s{}%s'.format(in_seperator) % (key, self.escape_str(value)) for (key, value) in data.items()])
    else:
     s= '''{}'''.format(seperator).join(['%s{}%s'.format(in_seperator) % (key, value) for (key, value) in data.items()])
    if parentheses==True:
        s=self.add_parentheses(s)
    return s
 def get_colums_format(self,row):
     return ''' , '''.join('{}'.format(pymysql.escape_string(col)) for col in row.keys())
 def get_values_format(self,row):
     return ''' , '''.join(self.escape_str(row[col]) for col in row.keys())
 def close(self):
     self.cursor.close()
     self.connection.close()
     self.connection=None
     self.cursor=None
     self.statement=None
 def create_table(self,table,fields):
     self.statement='''create table if not exists {} ( {} )'''.format(pymysql.escape_string(table),self.dict_to_str(fields,escape=False))
     self.cursor.execute(self.statement)#,{"table":table})
 def rename_table(self,old,new):
     self.statement='''rename table {} to {}'''.format(pymysql.escape_string(old),new)#,pymysql.escape_string(new))
     self.cursor.execute(self.statement)#,{"table":table})
 def insert_into_table_format(self,table, row):
     cols = self.get_colums_format(row)
     vals = self.get_values_format(row)
     return '''insert into {} ( {} ) VALUES ( {} )'''.format(table, cols, vals)
 def insert_into_table(self,table,row):
     self.statement=self.insert_into_table_format(table,row)
     self.cursor.execute(self.statement)
 def reset_table(self,table):
     self.statement='''truncate table {}'''.format(pymysql.escape_string(table))
     self.cursor.execute(self.statement)#,self.escape_str(table))#,{"table":table})
 def drop_table(self,table):
     self.statement='''drop table if exists {}'''.format(pymysql.escape_string(table))
     self.cursor.execute(self.statement)
 def add_column_format(self,table,columns):
     return '''alter table {} add {}'''.format(pymysql.escape_string(table),self.dict_to_str(columns,escape=False))
 def add_column(table,columns):
     self.statement=self.add_column_format(table,columns)
     self.cursor.execute(self.statement)
 def drop_column_format(self,table,column):
     return '''alter table {} drop column {}'''.format(pymysql.escape_string(table),pymysql.escape_string(column))
 def drop_column(table,column):
     self.statement=self.drop_column_format(table,columns)
     self.cursor.execute(self.statement)
 def rename_column_format(self,table,old,new):
     return '''alter table {} change {} {}'''.format(pymysql.escape_string(table),pymysql.escape_string(old),self.dict_to_str(new,escape=False))
 def rename_column(self,table,old,new):
     self.statement=self.rename_column_format(table,old,new)
     self.cursor.execute(self.statement)
 def modify_column_format(self,table,column):
     return '''alter table {} modify {}'''.format(pymysql.escape_string(table),self.dict_to_str(column,escape=False))
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
      for x in conditions:
         if type(x) is dict:
             condition+=self.dict_to_str(x,seperator="  ",in_seperator=" = ")
         else:
             condition+=" {} ".format(pymysql.escape_string(str(x)))
     return """delete from {} {}""".format(table,condition)
 def update_table(self,table,rows, conditions):
     self.statement=self.update_column_format(table,rows, conditions)
     self.cursor.execute(self.statement)
 def update_table_format(self,table,rows, conditions):
     condition=" where "
     for x in conditions:
         if type(x) is dict:
             condition+=self.dict_to_str(x,seperator="  ",in_seperator=" = ")
         else:
             condition+=str(x)
     return """update {} set {} {}""".format(table,self.dict_to_str(rows,seperator=" , ",in_seperator=" = "),condition)#self.dict_to_str(condition,seperator=operator,in_seperator=" = "))
 def select_from_format(self,table,rows,conditions,extras):
     if extras:
         extra=extras
     else:
         extra=""
     row=" "
     for x in rows:
         if type(x) is tuple:
             row+=" ( "
             for i in x:
                 row+=" {} ,".format(pymysql.escape_string(i))
             if row.strip()[-1]==',':
                 row=row.strip()[:-1]
             row+=" ) "
         else:
             row+=" {} ".format(pymysql.escape_string(str(x)))
     condition=""
     if conditions:
      condition=" where "
      for x in conditions:
         if type(x) is dict:
             condition+=self.dict_to_str(x,seperator="  ",in_seperator=" = ")
         else:
             condition+=" {} ".format(pymysql.escape_string(str(x)))
     return """select {} from {} {} {}""".format(row,pymysql.escape_string(table),condition,pymysql.escape_string(extra))#self.dict_to_str(condition,seperator=operator,in_seperator=" = "))
 def select_from(self,table,rows,conditions,extras):
     self.statement=self.select_from_format(table,rows,conditions,extras)
     self.cursor.execute(self.statement)
     return self.cursor.fetchall()
 def execute(self,statement,return_result=True):
     self.cursor.execute(statement)
     if return_result==True:
         return self.cursor.fetchall()
