##!/usr/bin/gksu /usr/bin/python2
# -*-encoding:utf-8 -*-
from gi.repository import Gtk
from subprocess import Popen,PIPE
import os
import re

class  sm_win(Gtk.Window):
   def __init__(self):
      with open('/etc/release','r') as f_re:
         this_issue=f_re.readline()
      Gtk.Window.__init__(self, title="zhentu software manager v0.1 for "+this_issue)

      self.connect("delete-event", self.sm_Win_quit)
      
      self.set_border_width(10)
      self.set_default_size(500,800)
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
      column = Gtk.TreeViewColumn("   software   ", renderer, text=0)
      self.portage_view.append_column(column)
      scrolled = Gtk.ScrolledWindow()
      scrolled.set_hexpand(False)
      scrolled.set_vexpand(True)
      scrolled.set_min_content_width(200)
      scrolled.add(self.portage_view)
      vb_tree.pack_start(scrolled,True, True, 0)
      b_tree_but=Gtk.Box()
      sel_installed=Gtk.RadioButton.new_with_label_from_widget(None,'Installed')
      sel_installed.connect("toggled", self.change_view_model,'installed')
      sel_uninstalled=Gtk.RadioButton.new_with_label_from_widget(sel_installed,'UnInstalled')
      sel_uninstalled.connect("toggled", self.change_view_model,'uninstalled')
      sel_all=Gtk.RadioButton.new_with_label_from_widget(sel_installed,'All')
      sel_all.connect("toggled", self.change_view_model,'all')
      b_tree_but.pack_start(sel_installed,False, True, 0)
      b_tree_but.pack_start(sel_uninstalled,False, True, 0)
      b_tree_but.pack_start(sel_all,False, True, 0)
      vb_tree.pack_end(b_tree_but,False, True, 0)

      info_view = Gtk.TextView()
      self.info_buffer = info_view.get_buffer()
      self.info_buffer.set_text("Software Info shows here")
      scro_softinfo = Gtk.ScrolledWindow()
      scro_softinfo.set_hexpand(False)
      scro_softinfo.set_vexpand(True)
      scro_softinfo.set_min_content_width(200)
      scro_softinfo.add(info_view)
      vb_operate.pack_start(scro_softinfo,True, True, 0)

      vb_but=Gtk.Box()
      vb_operate.pack_start(vb_but,False, True, 0)
      but_install=Gtk.Button.new_with_label("Install")
      vb_but.pack_start(but_install,True, False, 5) 
      but_remove=Gtk.Button("Remove")
      vb_but.pack_start(but_remove,True, True, 5) 
      but_kernel=Gtk.Button("Update Kernel")
      vb_but.pack_start(but_kernel,True, True, 5) 
      but_portage=Gtk.Button("Update Portage")
      vb_but.pack_start(but_portage,True, True, 5) 
      
      emerge_view = Gtk.TextView()
      self.emerge_buffer = emerge_view.get_buffer()
      self.emerge_buffer.set_text("emerge info shows here")
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
      installed=p1.communicate()[0].split('\n')
      installed
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
      with open(self.portdir+'/'+cate+'/metadata.xml') as f_meta:
        while re.search('<longdescription lang="en">',f_meta.readline())==None:
           continue
        line=f_meta.readline()
        if re.search('</longdescription>',line) != None:
           print 'metadata.xml of '+cate+' has no english disciption'
        else:   
           info='Category Explanation:\n\n '    
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
      p1=Popen(['eix','-nev',cate+'/'+soft],stdout=PIPE) # eix noclolor exactly verbose
      info='Software Explanation:\n'
      info_raw=p1.communicate()[0].splitlines()
      head_spaces=' '*5
      info=info+head_spaces+'Name: '+cate+'/'+soft+'\n'
      space_head_old=space_head_now=0
      for li in info_raw[1:]:
         space_head_now,key,value=self.parser(li)
         if key == 'Homepage':
            info=info+head_spaces+'Homepage:\n'.ljust(5)
            info=info+head_spaces*2+value+'\n'
         elif key == 'Description':
            info=info+head_spaces+'Description:\n'.ljust(5)
            if re.search('zh_CN',os.environ['LANG']) == None:
               info=info+head_spaces*2+value+'\n'
            else:
               with open('translating/description_translated') as f_trans:
                  trans_zh=''
                  for li in f_trans:
                     if li.startswith(cate+'/'+soft) == True:
                        print(value,li)
                        if re.search(re.escape(value),li) != None:
                          print('OK:  translation for '+cate+'/'+soft)
                          trans_zh=li.split(':::')[2]
                          break
                  if trans_zh == '':
                     print('Error: No translation for '+cate+'/'+soft)
               info=info+head_spaces*2+trans_zh+'\n'
      self.info_buffer.set_text(info)
      
   def on_tree_selection_changed(self,selection):
      model, iter_now = selection.get_selected()
      if iter_now != None:
         iter_par=model.iter_parent(iter_now)
         if iter_par == None :
            cate=model[iter_now][0]
            self.show_cate_info(cate)
         else:
            cate=model[iter_par][0]
            soft=model[iter_now][0]
            self.show_soft_info(cate,soft)

win = sm_win()
win.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
win.show_all()
Gtk.main()
      
            
