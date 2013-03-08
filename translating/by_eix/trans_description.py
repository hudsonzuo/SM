#!/usr/bin/python
# -*- utf-8 -*-

import re
import sys
from subprocess import Popen,PIPE

with open(sys.argv[1]) as f_des:
   for li in f_des:
      if re.search('Description:',li) == None:
         name=re.sub('^.* ','',li).rstrip('\n')
         continue
      li=li.rstrip('\n')
      desc=re.sub(' *Description: *','',li).rstrip('\n')
      resu=''
      with open('description_translated_old') as f_old:
         for li_old in f_old:
            if re.search(re.escape(desc),li_old) != None:
               resu=re.sub('.*:::.*:::','',li_old)
               break
      if resu == '':         
         p1=Popen(['./translate.sh',desc,'en','zh_CN'],stdout=PIPE)
         resu=p1.communicate()[0]
      new_li=name+':::'+desc+':::'+resu+'\n'
      with open('description_translated','a+') as f_trsl:
         f_trsl.write(new_li)
         

