#!/usr/bin/python
# -*- utf-8 -*-

import re
import sys
from subprocess import Popen,PIPE

with open(sys.argv[1]) as f_des:
   for li in f_des:
      li=li.rstrip('\n')
      desc=re.sub('.*:::','',li)
      p1=Popen(['./translate.sh',desc,'en','zh_CN'],stdout=PIPE)
      resu=p1.communicate()[0]
      new_li=li+':::'+resu+'\n'
      with open('description_translated','a+') as f_trsl:
         print(new_li)
         f_trsl.write(new_li)
         

