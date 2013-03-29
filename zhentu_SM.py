##!/usr/bin/gksu /usr/bin/python3
# -*- encoding:utf-8 -*-
from gi.repository import Gtk
from subprocess import Popen,PIPE,getstatusoutput
import os
import re
import gettext
import sys
class  Sm_win(Gtk.Window):
   def __init__(self):
      with open('/etc/release','r') as f_re:
         this_issue=f_re.readline()
      gettext.install('zhentu_SM','./locale/')
      #gettext.bindtextdomain('zhentu_SM', './locale/')
      #gettext.textdomain('zhentu_SM')
      #_ = gettext.gettext
      Gtk.Window.__init__(self, title=_("zhentu software manager v0.1 for ")+this_issue)
      str_dbg=_("zhentu software manager v0.1 for ")
      print(str_dbg.encode('utf-8'))
      print("朕兔软件管理器 v0.1, 发行:".encode('utf-8'))
      self.connect("delete-event", self.sm_Win_quit)
      self.set_border_width(10)
      self.set_default_size(800,800)
      self.set_resizable(True)
      vb_main=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
      self.add(vb_main)
      vb_tree=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
      vb_main.pack_start(vb_tree, True, True, 10)
      vb_operate=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
      vb_main.pack_start(vb_operate,True, True, 10)
      vb_operate.set_homogeneous(False)
    
      self.model_flag=[True,True] # Display installed and uninstall
      self.portage_model_all=Gtk.TreeStore(str) 
      self.portage_model_installed=Gtk.TreeStore(str) 
      self.portage_model_uninstalled=Gtk.TreeStore(str) 
      self.portdir='/usr/portage/'
      self.model_init(self.portage_model_all,self.portage_model_installed,self.portage_model_uninstalled)
      self.portage_view=Gtk.TreeView(self.portage_model_installed)
      select = self.portage_view.get_selection()
      select.connect("changed", self.on_tree_selection_changed)
      renderer = Gtk.CellRendererText()
      column = Gtk.TreeViewColumn(_("   software   "), renderer, text=0)
      self.portage_view.append_column(column)
      scrolled = Gtk.ScrolledWindow()
      scrolled.set_hexpand(False)
      scrolled.set_vexpand(True)
      scrolled.set_min_content_width(200)
      scrolled.add(self.portage_view)
      vb_tree.pack_start(scrolled,True, True, 0)
      b_tree_but=Gtk.Box()
      sel_installed=Gtk.RadioButton.new_with_label_from_widget(None,_('Installed'))
      sel_installed.connect("toggled", self.change_view_model,'installed')
      sel_uninstalled=Gtk.RadioButton.new_with_label_from_widget(sel_installed,_('UnInstalled'))
      sel_uninstalled.connect("toggled", self.change_view_model,'uninstalled')
      sel_all=Gtk.RadioButton.new_with_label_from_widget(sel_installed,_('All'))
      sel_all.connect("toggled", self.change_view_model,'all')
      b_tree_but.pack_start(sel_installed,False, True, 0)
      b_tree_but.pack_start(sel_uninstalled,False, True, 0)
      b_tree_but.pack_start(sel_all,False, True, 0)
      vb_tree.pack_end(b_tree_but,False, True, 0)
      info_view = Gtk.TextView()
      self.info_buffer = info_view.get_buffer()
      self.info_buffer.set_text(_("Software Info shows here"))
      scro_softinfo = Gtk.ScrolledWindow()
      scro_softinfo.set_hexpand(False)
      scro_softinfo.set_vexpand(True)
      scro_softinfo.set_min_content_width(200)
      scro_softinfo.add(info_view)
      vb_operate.pack_start(scro_softinfo,True, True, 0)

      self.pkg=''
      self.pkg_iter=None

      vb_but=Gtk.Box()
      vb_operate.pack_start(vb_but,False, True, 0)
      but_install=Gtk.Button.new_with_label(_("Install/Update"))
      vb_but.pack_start(but_install,True, False, 5) 
      but_install.connect('clicked',self.on_clicked_install)
      but_remove=Gtk.Button(_("Remove"))
      vb_but.pack_start(but_remove,True, True, 5) 
      but_remove.connect('clicked',self.on_clicked_uninstall)
      but_kernel=Gtk.Button(_("Update Kernel"))
      vb_but.pack_start(but_kernel,True, True, 5) 
      but_portage=Gtk.Button(_("Update Portage"))
      vb_but.pack_start(but_portage,True, True, 5) 
      but_portage=Gtk.Button(_("Repair Dependency"))
      vb_but.pack_start(but_portage,True, True, 5) 
      
      emerge_view = Gtk.TextView()
      self.emerge_buffer = emerge_view.get_buffer()
      self.emerge_buffer.set_text(_("emerge info shows here"))
      scro_emergeinfo = Gtk.ScrolledWindow()
      scro_emergeinfo.set_hexpand(False)
      scro_emergeinfo.set_vexpand(True)
      scro_emergeinfo.set_min_content_width(200)
      scro_emergeinfo.add(emerge_view)
      vb_operate.pack_start(scro_emergeinfo,True, True, 0)
   
   def sm_Win_quit(self, win, event):
      Gtk.main_quit()
   
   def model_init(self, model_all, model_installed, model_uninstalled):
      p1 = Popen(["qlist", "-IC"], stdout=PIPE)
      installed=p1.communicate()[0].decode('utf-8').splitlines()   #Popen返还的是byte str,所以需要decode。分成list是因为list的count()比str的count()更精确
      li=os.listdir(self.portdir)
      li.sort()
      for cate in li:
         if cate =='distfiles' or cate =='eclass' or cate =='licenses' or cate =='metadata' or cate =='profiles' or cate =='scripts':
            continue
         if os.path.isdir(self.portdir+cate) == True:
            iter_p_all=model_all.append(None,[cate])
            iter_p_installed=model_installed.append(None,[cate])
            iter_p_uninstalled=model_uninstalled.append(None,[cate])
            for soft in os.listdir(self.portdir+cate):
               if os.path.isdir(self.portdir+cate+'/'+soft)== False:
                  continue
               model_all.append(iter_p_all,[soft])
               if installed.count(cate+'/'+soft) == 0:
                  model_uninstalled.append(iter_p_uninstalled,[soft])
               else:   
                  model_installed.append(iter_p_installed,[soft])
   def model_update(self,model_reduce,model_increase):
      cate=re.sub('/.*','',self.pkg)
      soft=re.sub('.*/','',self.pkg)
      iter_now=model_increase.get_iter_first()
      while iter_now != None:
         if model_increase[iter_now][0] == cate:
            break
         iter_now=model_increase.iter_next(iter_now)   
      model_reduce.remove(self.pkg_iter)
      model_increase.append(iter_now,[soft])   
      
   def  change_view_model(self, button, name):
       if button.get_active():
          if name =='all':
             self.portage_view.set_model(self.portage_model_all)
          elif name =='installed':
             self.portage_view.set_model(self.portage_model_installed)
          elif name == 'uninstalled':
             self.portage_view.set_model(self.portage_model_uninstalled)

   def get_overlay():
      p1 = Popen(["emerge", "--info"], stdout=PIPE)
      p2 = Popen(["grep", "PORTDIR_OVERLAY"], stdin=p1.stdout, stdout=PIPE)
      li_overlay = p2.communicate()[0].lstrip("PORTDIR_OVERLAY=\"").rstrip("\"\n").split(' ')
      return li_overlay
   def show_cate_info(self,cate):
      info=_('\nCategory Explanation:\n\n')    
      with open('./translating/cate_description/description_translated') as f_desc:
         for line in f_desc:
            if re.search(cate+':::',line) == None:
               continue
            else:   
               if re.search('zh_CN',os.environ['LANG']) == None:
                  info=info+line.split(':::')[1]
               else:
                  info=info+line.split(':::')[2]
      if info == '\nCategory Explanation:\n\n':
         with open(self.portdir+'/'+cate+'/metadata.xml') as f_meta:
           while re.search('<longdescription lang="en">',f_meta.readline())==None:
              continue
           line=f_meta.readline()
           if re.search('</longdescription>',line) != None:
              print('metadata.xml of '+cate+' has no english disciption')
           else:   
              while re.search('</longdescription>',line) == None:
                 line=line.lstrip()
                 info=info+line
                 line=f_meta.readline()
      self.info_buffer.set_text(info)  
   
   def parser(self, line):
      space_head=len(line)-len(line.lstrip())
      li=line.lstrip()
      if re.search(': ',li) == None:
         key=''
         value=li.lstrip().rstrip()
      else:
         key=re.sub(':.*','',li)
         value=re.sub('.*'+key+':','',li).lstrip()
      return space_head,key,value   
   def show_soft_info(self,cate,soft):
      p1=Popen(['eix','-ne',cate+'/'+soft],stdout=PIPE) # eix noclolor exactly verbose
      info=_('Software Explanation:\n')
      info_raw=p1.communicate()[0].decode('utf-8').splitlines()
      head_spaces=' '*5
      info=info+head_spaces+_('Name: ')+cate+'/'+soft+'\n'
      space_head_old=space_head_now=0
      if re.search('zh_CN',os.environ['LANG']) == None:
         env_lang='en'
      else:
         env_lang='zh'
      for li in info_raw[1:]:
         space_head_now,key,value=self.parser(li)
         if key == 'Homepage':
            info=info+head_spaces+_('Homepage:\n')
            info=info+head_spaces*2+value+'\n'
         elif key == 'Description':
            info=info+head_spaces+_('Description:\n')
            if env_lang =='en':
               info=info+head_spaces*2+value+'\n'
            else:
               with open('translating/description_translated') as f_trans:
                  trans_zh=''
                  for li in f_trans:
                     if li.startswith(cate+'/'+soft) == True:
                        #print(value,li)
                        if re.search(re.escape(value),li) != None:
                          #print('OK:  translation for '+cate+'/'+soft)
                          trans_zh=li.split(':::')[2]
                          break
                  if trans_zh == '':
                     print('Error: No translation for '+cate+'/'+soft)
               info=info+head_spaces*2+trans_zh+'\n'
         elif key == 'Installed versions':
            info=info+head_spaces+_('Installed:\n')
            info=info+head_spaces*2+re.sub('\(.*','',value)+'\n'   #value可能包含KEYWORDS和RESTRICT,man 5 ebuild: Masking,RESTRICT,
         elif key == 'Available versions':
            print(value) 
      self.info_buffer.set_text(info)
      
   def on_tree_selection_changed(self,selection):
      model, iter_now = selection.get_selected()
      if iter_now != None:
         iter_par=model.iter_parent(iter_now)
         soft =''
         if iter_par == None :
            cate=model[iter_now][0]
            self.show_cate_info(cate)
         else:
            cate=model[iter_par][0]
            soft=model[iter_now][0]
            self.show_soft_info(cate,soft)
         if soft != '':  
            self.pkg=cate+'/'+soft       
            self.pkg_iter=iter_now

   def on_clicked_install(self,butname,):
      print('on_clicked_install')
      print(self.pkg)
      
#     The following USE changes are necessary to proceed:
#     #required by dev-texlive/texlive-xetex-2011, required by dev-texlive/texlive-xetex (argument)
#     =app-text/texlive-core-2011-r6 xetex
          
#
#     The following keyword changes are necessary to proceed:
#     #required by app-vim/notes (argument)
#     =app-vim/notes-0.16.17 ~x86
#     #required by app-vim/notes-0.16.17, required by app-vim/notes (argument)
#     =app-vim/xolox-misc-20111124 ~x86
#
#     ACCEPT_KEYWORDS='x86' emerge -avt app-vim/notes
      cmd_re=getstatusoutput('emerge '+self.pkg)
      print('emerge '+self.pkg)
      if cmd_re[0] == 0:
          print(self.pkg+' is installed')
          self.model_update(self.portage_model_uninstalled,self.portage_model_installed)
      else :
          print(cmd_re[1].splitlines())
   def on_clicked_uninstall(self,butname):
      print('on_clicked_uninstall')
      cmd_re=getstatusoutput('emerge -C '+self.pkg)
      if cmd_re[0] == 0:
          print('removed')
          self.model_update(self.portage_model_installed,self.portage_model_uninstalled)
      else:
         print('do nothing')
      
win = Sm_win()
win.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
win.show_all()
Gtk.main()
      
            
