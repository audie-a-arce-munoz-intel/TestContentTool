# ----------------------------------------------------------------------------------------------------------------------
# Name:        Test Content Tool
# Purpose:     
# Python:      3.7
# Author:      aaarcemu
# Created:     10/27/2021
# Modified:    09/02/2022
# ----------------------------------------------------------------------------------------------------------------------

from datetime import datetime
import pathlib
from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename
import os
import re
from shutil import copyfile
import time
import zipfile
import filecmp
import glob
import shutil
import subprocess
from xml.dom import minidom
import xml.etree.ElementTree as ET
import getpass
import sys
import urllib.request
import re



try:
    from PyInstaller.utils.hooks import collect_submodules
    hiddenimports = collect_submodules('encodings')
except ImportError:
    pass

root = Tk()
root.style = ttk.Style(root)
root.style.configure('TLabel', font=('Helvetica', 12))
root.style.configure('TButton', font=('Helvetica', 12))
root.title('Test Content Tool')

mainframe = ttk.Notebook(root, padding='3 3 3 3')
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

checkoutframe = ttk.Frame(mainframe)
mainframe.add(checkoutframe, text='Content Check-out')

conversionframe = ttk.Frame(mainframe)
mainframe.add(conversionframe, text='Content Conversion')

checkinframe = ttk.Frame(mainframe)
mainframe.add(checkinframe, text='Content Check-in')

product_stepping =  StringVar()
parent_prod =  StringVar()
product_stepping.set(os.environ.get('TCG_PRODUCT'))

################################################################################################
##################################### CHECK OUT FRAME ########################################

cmd_checkout_to_execute = ''

def chk_tapOverwrite_def(*args):  
	if (chk_tapOverwrite.get() == 'No Overwrite'):
		print('TestContentTool -INFO-  |	No Overwrite Selected')
		disable_widget((tap_ovr_path,tapOverwrite_path_button,spf_overwite_path,spf_overwrite_path_button,))
		tapovrpath.set('')
		spfoverwrite.set('')
		enable_widget((start_co_button,source_combo))
	elif (chk_tapOverwrite.get() == 'from Check Out'):
		print('TestContentTool -INFO-  |	Content Check out will be overwritted')
		enable_widget((tap_ovr_path,tapOverwrite_path_button,spf_overwite_path,spf_overwrite_path_button,source_combo))
		disable_widget((start_co_button,spf_overwite_path,spf_overwrite_path_button))
		spfoverwrite.set('')
	elif (chk_tapOverwrite.get() == 'from SPF Folder'):
		print('TestContentTool -INFO-  |	Content from existing SPF folder will be overwritted')
		src_value.set('')
		tidtupcopath.set('')
		plistcopath.set('')
		outcopath.set('')
		enable_widget((tap_ovr_path,tapOverwrite_path_button,spf_overwite_path,spf_overwrite_path_button))
		disable_widget((out_path,out_path_button,plist_co_path,plist_co_path_button,tidtup_co_path,tidtup_co_path_button,source_combo))
	

def get_plist_checkout_file():  
	try:
		plistcopath.set(askopenfilename(filetypes=(('Plist files', '*.plist'), ("All files", "*.*"))))
	except Exception as er:
		writelog('get_tpname error: ' + repr(er))
	enable_widget((out_path,out_path_button))

def get_tidtup_checkout_file():  
	try:
		tidtupcopath.set(askopenfilename(filetypes=(('List files', '*.list'), ("All files", "*.*"))))
	except Exception as er:
		writelog('get_tpname error: ' + repr(er))
	enable_widget((out_path,out_path_button))
	
def get_outco_path():  
	try:
		outcopath.set(askdirectory())
	except Exception as er:
		writelog('get_tpname error: ' + repr(er))
	if (chk_tapOverwrite.get() != ''):
		enable_widget_single(start_co_button)

def get_spf_overwrite_path():  
	try:
		spfoverwrite.set(askdirectory())
		enable_widget_single(start_co_button)
	except Exception as er:
		writelog('get_tpname error: ' + repr(er))
	
def get_tapOverwrite_file_def():  
	try:
		tapovrpath.set(askopenfilename(filetypes=(('TXT files', '*.txt'), ("All files", "*.*"))))
		if (spfoverwrite.get() != ''):
			enable_widget_single(start_co_button)
		if (chk_tapOverwrite.get() == 'from Check Out'):
			enable_widget_single(start_co_button)
	except Exception as er:
		pass

def source_selected(*args): 
	if (source_combo.get() == "Plist"):
		print ('TestContentTool -INFO-  |	Content check out will be done using a plist reference')
		pl_exec.set('Tuple')
		enable_widget((plist_co_path, plist_co_path_button))
		disable_widget((tidtup_co_path, tidtup_co_path_button))
	else:
		enable_widget((tidtup_co_path, tidtup_co_path_button))
		disable_widget((plist_co_path, plist_co_path_button))
		if (source_combo.get()  == "TID"):
			print ('TestContentTool -INFO-  |	Content check out will be done using a TID list')
			pl_exec.set('TID')
		if (source_combo.get() == "Tuple"):
			print ('TestContentTool -INFO-  |	Content check out will be done using a Tuple list')
			pl_exec.set('Tuple')

def clear_co_def(*args):  
	widgets = (plist_co_path, plist_co_path_button, tidtup_co_path, tidtup_co_path_button,tapOverwrite_path_button,start_co_button,tap_ovr_path,out_path_button,out_path)
	variables = (src_value,chk_tapOverwrite,plistcopath,tidtupcopath,tapovrpath,pl_exec,outcopath,spfoverwrite)
	for var in variables:
		var.set('')
	disable_widget(widgets)

def plist_extraction_checkout():
	plistpath = plistcopath.get()
	print ('TestContentTool -INFO-  |	Getting content from plist path: ' + plistpath)
	cnt = 0
	total_patterns =0
	array_tuples = []
	array_TIDs = []
	array_SPFs = []
	with open(plistpath) as pp:
		for line in pp:
			if (re.match('Pat', line.strip())):
				pat_regex = re.findall('[0-9]+', line)
				array_tuples.append (pat_regex[0])
				array_TIDs.append (pat_regex[1])
				array_SPFs.append (re.search("x00_(.*?);",line).group(1))
				print("TestContentTool -INFO-  |	Cnt:{} | Tuple:{} | TID:{} | SPF name:{}".format(cnt, pat_regex[0], pat_regex[1], re.search("x00_(.*?);",line).group(1)))
				cnt+=1
		total_patterns = cnt
		print("TestContentTool -INFO-  |	Total Number of patterns: {}\n".format(total_patterns))
	while (cnt!=0):
		cnt=cnt-1
		print("TestContentTool -INFO-  |	Checking Out: {}/{} \n".format(total_patterns-cnt,total_patterns))
		os.system ('copy_trace.py -t '+array_tuples[cnt]+' -out '+ outcopath.get());
		os.system ('mv '+ outcopath.get()+'/*'+array_tuples[cnt]+'*/*.spf.gz '+outcopath.get()+'/'+array_SPFs[cnt]+'.spf.gz')
		os.system ('rm -r '+ outcopath.get()+'/*'+array_tuples[cnt]+'*')
		os.system ('gunzip -f '+ outcopath.get()+'/*.gz')

def tidtup_extraction_checkout():
	cnt = 0
	total_patterns =0
	array_tuples = []
	array_TIDs = []
	array_SPFs = []
	new_var_itppName = ''
	itpp_path = ''
	console_cmd = ''
	
	print ("TestContentTool -INFO-  |	Content Source path: " + tidtupcopath.get())
	with open(tidtupcopath.get()) as pp:
		for line in pp:
			if (source_combo.get()  == "TID"):
				print ("TestContentTool -INFO-  |	TID Number:" + line)
				array_TIDs.append(line.replace('\n',''))
			else:
				print ("TestContentTool -INFO-  |	Tuple Number:" + line)
				array_tuples.append(line.replace('\n',''))
			cnt+=1
		total_patterns = cnt
		print("TestContentTool -INFO-  |	Total Number of patterns: {}\n".format(total_patterns))
	while (cnt!=0):
		cnt=cnt-1
		print("TestContentTool -INFO-  |	Checking Out: {}/{} \n".format(total_patterns-cnt,total_patterns))
		if (source_combo.get()  == "TID"):
			print ("TestContentTool -INFO-  |	Checking out TID:" + array_TIDs[cnt])
			os.system ('vaultmgr -q test_id = '+  array_TIDs[cnt]+ ' -- -co_source '+ outcopath.get());
			os.system ('mv '+ outcopath.get()+'/'+array_TIDs[cnt]+'/*.spf '+outcopath.get())
			os.system ('rm -r '+ outcopath.get()+'/'+array_TIDs[cnt])
		if (source_combo.get() == "Tuple"):
			os.system ('copy_trace.py -t '+array_tuples[cnt]+' -out '+ outcopath.get());
			itpp_path = os.path.join(outcopath.get(),'/*',array_tuples[cnt],'*/')
			for itpp_name in glob.glob(outcopath.get()+'/*'+array_tuples[cnt]+'*/*'):
				if itpp_name.endswith(".itpp.gz.bz2"):	 
					new_var_itppName = itpp_name.replace('.itpp.gz.bz2','').split('x00_')[1]
			os.system ('mv '+ outcopath.get()+'/*'+array_tuples[cnt]+'*/*.spf.gz '+ outcopath.get()+'/'+ new_var_itppName +'.spf.gz')	
			os.system ('rm -r '+ outcopath.get()+'/*'+array_tuples[cnt]+'*_')
			os.system ('gunzip -f '+ outcopath.get()+'/'+new_var_itppName+'.spf.gz')
			
def reset_removal_checkout(*args): 
	print ("TestContentTool -INFO-  |	Removing reset from existing content")
	keyword = 'End Flow HVM_MAIN_RESET' 
	for spf_name in os.listdir(outcopath.get()):
		start_print = False
		cnt_start = 0
		if spf_name.endswith(".spf"):	
			with open(outcopath.get()+'/'+spf_name, 'r+') as fr:
				list_of_lines = fr.readlines()
			with open(outcopath.get()+'/'+spf_name, 'w+') as fw:
				for line in list_of_lines:
					if keyword in line.strip():
						start_print = True
					if start_print:
						if (cnt_start > 2): fw.write(line)
						else: cnt_start+=1;
		else:
			continue
		
def overwrite_tapnames(*args): 
	print("TestContentTool -INFO-  |	Overwritting content with new endpoint names...")	
	EP_new_list = []
	EP_old_list = []
	SPF_new_list = []
	SPF_old_list = []
	cnt_overwrite_spf = 0
	cnt_overwrite_tap = 0
	line_is_done=False
	new_file_name = ''
	old_file_name = ''
	folder2overwrite = ''
	
	if (chk_tapOverwrite.get() != 'from SPF Folder'):
		folder2overwrite = outcopath.get()
		print ("TestContentTool -INFO-  |	Using existing SPF Folder")
	else:
		folder2overwrite = spfoverwrite.get()
		print ("TestContentTool -INFO-  |	Overwriting from check out folder")
	
	print ("TestContentTool -INFO-  |	Content location to Overwrite:" + folder2overwrite)
	
	with open(tapovrpath.get()) as op:
		print ("TestContentTool -INFO-  |	Overwrite Setup Input File:" + tapovrpath.get())
		for line in op:
			if (re.match('TAP_EP_Replace', line.strip())):
				EP_old_list.append(re.split(',', line)[1])
				EP_new_list.append(re.split(',', line)[2])
				cnt_overwrite_tap+=1			
			if (re.match('SPF_Name_Replace', line.strip())):
				SPF_old_list.append(re.split(',', line)[1])
				SPF_new_list.append(re.split(',', line)[2])
				cnt_overwrite_spf+=1
	for spf_name in os.listdir(folder2overwrite):
		if spf_name.endswith(".spf"):	
			with open(folder2overwrite+'/'+spf_name, 'r+') as fr:
				list_of_lines = fr.readlines()
			with open(folder2overwrite+'/'+spf_name, 'w+') as fw:
				for line in list_of_lines:
					line_is_done=False
					for endpoint in EP_old_list:
						if (endpoint in line.strip() and line_is_done==False):
							fw.write(line.replace(endpoint, EP_new_list[EP_old_list.index(endpoint)]))
							line_is_done=True
					if (line_is_done==False):
						fw.write(line)
						
	#for SPF_name in os.listdir(folder2overwrite):
	#	old_file_name = SPF_name;
	#	for name_to_replace in SPF_old_list:
	for name_to_replace in SPF_old_list:
		for SPF_name in os.listdir(folder2overwrite):
			old_file_name = SPF_name;
			if (name_to_replace in SPF_name):
				new_file_name= SPF_name.replace(name_to_replace, SPF_new_list[SPF_old_list.index(name_to_replace)])
				print ("TestContentTool -INFO-  |	Updating File Name ->-> from {} to {}".format(SPF_name,new_file_name))
				os.rename (folder2overwrite+'/'+old_file_name,folder2overwrite+'/'+new_file_name)
				
def start_co_def(*args):  
	print('\n======================================================================================\n')
	print ("TestContentTool -INFO-  |	Running Content Check Out...")
	
	if (chk_tapOverwrite.get() != 'from SPF Folder'):
		if (source_combo.get() == "Plist"):
			plist_extraction_checkout()
			reset_removal_checkout()
		elif (source_combo.get() == "Tuple"):
			print ("TestContentTool -INFO-  |	Checkout based on tuples")
			tidtup_extraction_checkout()
			reset_removal_checkout()
		elif (source_combo.get() == "TID"):
			print ("TestContentTool -INFO-  |	Checkout based on tuples")
			tidtup_extraction_checkout()		
	if ((chk_tapOverwrite.get() == 'from Check Out') or ((chk_tapOverwrite.get() == 'from SPF Folder'))):
		overwrite_tapnames()
	print ("TestContentTool -INFO-  |	Check out is Done!")	
	os.system("rm *query*")
	print( "TestContentTool -EXIT- " + "%s"%datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + "\n")
	print('\n======================================================================================\n')
	exit()

src_value = StringVar()
src_value.set('')
chk_tapOverwrite = StringVar()
plistcopath = StringVar()
tidtupcopath = StringVar()
tapovrpath = StringVar()
spfoverwrite = StringVar()
outcopath = StringVar()
pl_exec = StringVar()
itpp_name = StringVar()
pl_exec.set('')

sep = ttk.Separator(checkoutframe, orient="horizontal")
sep.grid(column=1, row=3, sticky='we', columnspan=8)

ttk.Label(checkoutframe, text='Stepping:').grid(column=1, row=4, sticky=E)
ttk.Label(checkoutframe, textvariable=product_stepping, font='Helvetica 14 bold', foreground="blue").grid(column=2, row=4, sticky=W)

ttk.Label(checkoutframe, text='Check Out Source:').grid(column=1, row=5, sticky=E)
source_combo = ttk.Combobox(checkoutframe, textvariable=src_value, width=15)
source_combo['values'] = ("TID", "Tuple", "Plist")
source_combo.grid(column=2, row=5, sticky=W)
source_combo.bind('<<ComboboxSelected>>', source_selected)

ttk.Label(checkoutframe, text='Plist Path:').grid(column=1, row=7, sticky=E)
plist_co_path = ttk.Entry(checkoutframe, width=90, textvariable=plistcopath, state='disable')
plist_co_path.grid(column=2, row=7, sticky=(W, W), columnspan=6)

plist_co_path_button = ttk.Button(checkoutframe, text='...', width=3, command=get_plist_checkout_file, state='disable')
plist_co_path_button.grid(column=8, row=7, sticky=W)

ttk.Label(checkoutframe, text='TID/Tuple List:').grid(column=1, row=8, sticky=E)
tidtup_co_path = ttk.Entry(checkoutframe, width=90, textvariable=tidtupcopath, state='disable')
tidtup_co_path.grid(column=2, row=8, sticky=(W, W), columnspan=6)

tidtup_co_path_button = ttk.Button(checkoutframe, text='...', width=3, command=get_tidtup_checkout_file, state='disable')
tidtup_co_path_button.grid(column=8, row=8, sticky=W)

ttk.Label(checkoutframe, text='Output Path:').grid(column=1, row=9, sticky=E)
out_path = ttk.Entry(checkoutframe, width=90, textvariable=outcopath, state='disable')
out_path.grid(column=2, row=9, sticky=(W, W), columnspan=6)

out_path_button = ttk.Button(checkoutframe, text='...',width=3, command=get_outco_path, state='disable')
out_path_button.grid(column=8, row=9, sticky=W)

ttk.Label(checkoutframe, text='TAP/SPF Name Overwrite').grid(column=1, row=14, sticky=E)
tapoverw_combo = ttk.Combobox(checkoutframe, textvariable=chk_tapOverwrite, width=15)
tapoverw_combo['values'] = ("No Overwrite", "from Check Out", "from SPF Folder")
tapoverw_combo.grid(column=2, row=14, sticky=W)
tapoverw_combo.bind('<<ComboboxSelected>>', chk_tapOverwrite_def)

ttk.Label(checkoutframe, text='Overwrite Setup File:').grid(column=1, row=15, sticky=E)
tap_ovr_path = ttk.Entry(checkoutframe, width=90, textvariable=tapovrpath, state='disable')
tap_ovr_path.grid(column=2, row=15, sticky=(W, W), columnspan=6)

tapOverwrite_path_button = ttk.Button(checkoutframe, text='...', width=3, command=get_tapOverwrite_file_def, state='disable')
tapOverwrite_path_button.grid(column=8, row=15, sticky=W)

ttk.Label(checkoutframe, text='SPF Path:').grid(column=1, row=16, sticky=E)
spf_overwite_path = ttk.Entry(checkoutframe, width=90, textvariable=spfoverwrite, state='disable')
spf_overwite_path.grid(column=2, row=16, sticky=(W, W), columnspan=6)

spf_overwrite_path_button = ttk.Button(checkoutframe, text='...', width=3, command=get_spf_overwrite_path, state='disable')
spf_overwrite_path_button.grid(column=8, row=16, sticky=W)

sep = ttk.Separator(checkoutframe, orient="horizontal")
sep.grid(column=1, row=18, sticky='we', columnspan=8)

sep = ttk.Separator(checkoutframe, orient="horizontal")
sep.grid(column=1, row=13, sticky='we', columnspan=8)

start_co_button = ttk.Button(checkoutframe, text='Start', width=6, command=start_co_def, state='disable')
start_co_button.grid(column=8, row=19, sticky=W)

clear_co_button = ttk.Button(checkoutframe, text='Clear', width=6, command=clear_co_def)
clear_co_button.grid(column=7, row=19,sticky=E)

################################################################################################
#####################################  CONVERSION FRAME ########################################

def chk_spf2itpp_def():  
	if (chk_spf2itpp.get() == '0'):
		enable_widget((check_espf2spf,check_ITPP2SPF))
		resource_value.set('')
		disable_widget_single(resource_combo)
		if (chk_espf2spf.get() == '0' and chk_itpp2spf.get() == '0'):
			disable_widget((resource_combo,nbqslot_combo,inconv_path,outconv_path,tapspec_path,stfspec_path,inconv_path_button,outconv_path_button,
			tapspec_path_button,stfspec_path_button,check_EXTRACOLL,start_conv_button))
	else:
		print('TestContentTool -INFO-  |	SPF TO ITPP Selected')
		enable_widget_single(resource_combo)
		disable_widget((check_espf2spf,check_ITPP2SPF))

def chk_itpp2spf_def():  
	if (chk_itpp2spf.get() == '0'):
		enable_widget((check_espf2spf,check_SPF2ITPP))
		resource_value.set('')
		disable_widget((resource_combo,tapspec_path_button,stfspec_path_button,tapspec_path,stfspec_path))
		if (chk_spf2itpp.get() == '0' and chk_espf2spf.get() == '0'):
			disable_widget((resource_combo,nbqslot_combo,inconv_path,outconv_path,tapspec_path,stfspec_path,inconv_path_button,outconv_path_button,
			tapspec_path_button,stfspec_path_button,check_EXTRACOLL,start_conv_button))
	else:
		print('TestContentTool -INFO-  |	ITPP TO SPF Selected')
		#enable_widget_single(resource_combo)
		resource_value.set('Local')
		enable_widget((outconv_path,inconv_path,inconv_path_button,outconv_path_button))
		disable_widget((check_espf2spf,check_SPF2ITPP))
		
def chk_espf2spf_def():  
	if (chk_espf2spf.get() == '0'):
		enable_widget((check_SPF2ITPP,check_ITPP2SPF))
		resource_value.set('')
		disable_widget_single(resource_combo)
		if (chk_spf2itpp.get() == '0' and chk_itpp2spf.get() == '0'):
			disable_widget((resource_combo,nbqslot_combo,inconv_path,outconv_path,tapspec_path,stfspec_path,inconv_path_button,outconv_path_button,
			tapspec_path_button,stfspec_path_button,check_EXTRACOLL,start_conv_button))
	else:
		print('TestContentTool -INFO-  |	ESPF TO ITPP/SPF Selected')
		enable_widget_single(resource_combo)
		disable_widget((check_SPF2ITPP,check_ITPP2SPF))
	
def resource_selected(*args): 
	print ('TestContentTool -INFO-  |	Resource selected:'+resource_value.get())
	if (resource_value.get() == "Netbatch"):
		enable_widget_single(nbqslot_combo)
	elif (resource_value.get() == "Local"):
		nbqslot_value.set('')
		if (chk_itpp2spf.get() == '0'):
			enable_widget((outconv_path,inconv_path,tapspec_path,stfspec_path,inconv_path_button,outconv_path_button,
					   tapspec_path_button,stfspec_path_button))
		else:
			enable_widget((outconv_path,inconv_path,inconv_path_button,outconv_path_button))
		disable_widget_single(nbqslot_combo)

def nbqslot_selected(*args): 
	print ('TestContentTool -INFO-  |	NB SLOT selected:'+nbqslot_value.get())
	enable_widget((outconv_path,inconv_path,tapspec_path,stfspec_path,inconv_path_button,outconv_path_button,
				   tapspec_path_button,stfspec_path_button))
	
def chk_extracoll_def():  
	if (chk_extracoll.get() == '0'):
		disable_widget((othercoll_path,othercoll_path_button))
	if (chk_extracoll.get() == '1'):
		print('TestContentTool -INFO-  |	Extra Collateral Requiered')
		enable_widget((othercoll_path,othercoll_path_button))
		othercollpath.set('')	
		
def get_inconv_path():  
	try:
		inconvpath.set(askdirectory())
	except Exception as er:
		writelog('get_tpname error: ' + repr(er))
	enable_widget_single(start_conv_button) 
		
def get_outconv_path():  
	try:
		outconvpath.set(askdirectory())
	except Exception as er:
		writelog('get_tpname error: ' + repr(er))
		
def get_tapspec_path():
	try:
		tapspecpath.set(askopenfilename(filetypes=(('XML files', '*.spfspec'), ("All files", "*.*"))))
	except Exception as er:
		writelog('get_tpname error: ' + repr(er))

def get_stfspec_path():
	try:
		stfspecpath.set(askopenfilename(filetypes=(('XML files', '*.spfspec'), ("All files", "*.*"))))
	except Exception as er:
		writelog('get_tpname error: ' + repr(er))
	enable_widget_single(check_EXTRACOLL)

def get_othercoll_path():
	try:
		othercollpath.set(askopenfilename(filetypes=(('XML files', '*.spfspec'), ("All files", "*.*"))))
	except Exception as er:
		pass

def clear_conv_def(*args):  
	widgets = (resource_combo,nbqslot_combo,inconv_path,outconv_path,tapspec_path,stfspec_path,inconv_path_button,outconv_path_button,tapspec_path_button,stfspec_path_button,check_EXTRACOLL,start_conv_button)
	variables = (chk_spf2itpp,chk_espf2spf,chk_itpp2spf,chk_extracoll,resource_value,nbqslot_value,inconvpath,outconvpath,modelpath,tapspecpath,stfspecpath)
	for var in variables:
		var.set('')
	disable_widget(widgets)
	othercollpath.set('Format: --templateFile <path>/test_spf.template')
	disable_widget((othercoll_path,othercoll_path_button))
	enable_widget((check_SPF2ITPP,check_espf2spf,check_ITPP2SPF))

def format_conversion(*args):  
	cnt_files_conv = 0
	num_files_spf = 0
	num_files_itpp = 0
	num_files_espf = 0
	
	for file in os.listdir(inconvpath.get()):
		if file.endswith(".spf"):
			num_files_spf += 1
		if file.endswith(".itpp"):
			num_files_itpp += 1
		if file.endswith(".espf"):
			num_files_espf += 1
	print ("TestContentTool -INFO-  |	 Total Number of Files received:\n 	SPF: {}\n	ITPP: {}\n	ESPF: {}\n".format(num_files_spf,num_files_itpp,num_files_espf))
	
	for input_name in os.listdir(inconvpath.get()):
		cnt_files_conv+=1
		if input_name.endswith(".spf"):
			print("TestContentTool -INFO-  |	Converting file "+inconvpath.get()+'/'+input_name+ ' to ITPP Format')
			itpp_name = input_name.replace('spf','itpp')
			if (nbqslot_value.get() == ''):
				if (chk_extracoll.get() == ''):
					print('TestContentTool -INFO-  |	Executing (no extra collaterals) ---> ----> /p/hdk/cad/spf/eng.2021.ww52a/bin/spf --tapSpecFile '+ tapspecpath.get() + ' --stfSpecFile '+ stfspecpath.get() + ' --testSeqFile ' + inconvpath.get()+'/'+input_name + ' --itppFile '+ outconvpath.get() + '/' + itpp_name +'\n')
					os.system('/p/hdk/cad/spf/eng.2021.ww52a/bin/spf --tapSpecFile '+ tapspecpath.get() + ' --stfSpecFile '+ stfspecpath.get() + ' --testSeqFile ' + inconvpath.get()+'/'+input_name + ' --itppFile '+ outconvpath.get()+'/'+itpp_name)
				else:
					print('TestContentTool -INFO-  |	Executing ---> ----> /p/hdk/cad/spf/eng.2021.ww52a/bin/spf --tapSpecFile '+ tapspecpath.get() + ' --stfSpecFile '+ stfspecpath.get() + ' --testSeqFile ' + inconvpath.get()+'/'+input_name + ' --itppFile '+ outconvpath.get() + '/' + itpp_name + othercoll_path.get() +'\n')
					os.system('/p/hdk/cad/spf/eng.2021.ww52a/bin/spf --tapSpecFile '+ tapspecpath.get() + ' --stfSpecFile '+ stfspecpath.get() + ' --testSeqFile ' + inconvpath.get()+'/'+input_name + ' --itppFile '+ outconvpath.get()+'/'+itpp_name + othercoll_path.get())
			else:
				if (chk_extracoll.get() == ''):
					print ('TestContentTool -INFO-  |	Executing (no extra collaterals) ---> ----> nbq -P sc_normal -C SLES11SP4&&128G -Q ' + nbqslot_combo.get() +' /p/hdk/cad/spf/eng.2021.ww52a/bin/spf --tapSpecFile '+ tapspecpath.get() + ' --stfSpecFile '+ stfspecpath.get() + ' --testSeqFile '+ inconvpath.get()+'/'+input_name + ' --itppFile ' + outconvpath.get()+'/'+itpp_name + othercollpath.get() +'\n')
					os.system ('nbq -P sc_normal -C "SLES11SP4&&96G" -Q' + nbqslot_combo.get() +' /p/hdk/cad/spf/eng.2021.ww52a/bin/spf --tapSpecFile '+ tapspecpath.get() + ' --stfSpecFile '+ stfspecpath.get() + ' --testSeqFile '+ inconvpath.get()+'/'+input_name + ' --itppFile ' + outconvpath.get()+'/'+itpp_name)
				else:
					print ('TestContentTool -INFO-  |	Executing ---> ----> nbq -P sc_normal -C SLES11SP4&&128G -Q ' + nbqslot_combo.get() +' /p/hdk/cad/spf/eng.2021.ww52a/bin/spf --tapSpecFile '+ tapspecpath.get() + ' --stfSpecFile '+ stfspecpath.get() + ' --testSeqFile '+ inconvpath.get()+'/'+input_name + ' --itppFile ' + outconvpath.get()+'/'+itpp_name + othercollpath.get() +'\n')
					os.system ('nbq -P sc_normal -C "SLES11SP4&&96G" -Q' + nbqslot_combo.get() +' /p/hdk/cad/spf/eng.2021.ww52a/bin/spf --tapSpecFile '+ tapspecpath.get() + ' --stfSpecFile '+ stfspecpath.get() + ' --testSeqFile '+ inconvpath.get()+'/'+input_name + ' --itppFile ' + outconvpath.get()+'/'+itpp_name + " " + othercoll_path.get())
		if input_name.endswith(".espf"):
			print("TestContentTool -INFO-  |	Converting file: "+inconvpath.get()+'/'+input_name+ ' to SPF Format')
			spf_new_name = input_name.replace('.espf','.spf')
			spf_name = input_name.replace('.espf','.itpp.spf')
			itpp_name = input_name.replace('.espf','.itpp')
			print ('TestContentTool -INFO-  |	Conversion using Local Resources')
			if (nbqslot_value.get() == ''):
				if (chk_extracoll.get() == ''):
					print ('TestContentTool -INFO-  |	Executing ---> ----> /p/hdk/cad/spf/eng.2021.ww52a/bin/spf_perl_pp --tapSpecFile '+ tapspecpath.get() + ' --stfSpecFile '+ stfspecpath.get() + ' --testSeqFile '+ inconvpath.get()+'/'+input_name  + ' --itppFile ' + outconvpath.get()+'/'+itpp_name + ' --keep')
					os.system ('/p/hdk/cad/spf/eng.2021.ww52a/bin/spf_perl_pp --tapSpecFile '+ tapspecpath.get() + ' --stfSpecFile '+ stfspecpath.get() + ' --testSeqFile '+ inconvpath.get()+'/'+input_name  + ' --itppFile ' + outconvpath.get()+'/'+itpp_name + ' --keep')
					os.system ('mv ' + outconvpath.get()+'/'+spf_name + ' ' + outconvpath.get()+'/'+spf_new_name)
				else:
					print ("TestContentTool -INFO-  |	Extra Collaterals added:" + othercoll_path.get() )
					print ('TestContentTool -INFO-  |	Executing ---> ----> /p/hdk/cad/spf/eng.2021.ww52a/bin/spf_perl_pp --tapSpecFile '+ tapspecpath.get() + ' --stfSpecFile '+ stfspecpath.get() + ' --testSeqFile '+ inconvpath.get()+'/'+input_name  + ' --itppFile ' + outconvpath.get()+'/'+itpp_name + " " +othercoll_path.get() + ' --keep')
					os.system ('/p/hdk/cad/spf/eng.2021.ww52a/bin/spf_perl_pp --tapSpecFile '+ tapspecpath.get() + ' --stfSpecFile '+ stfspecpath.get() + ' --testSeqFile '+ inconvpath.get()+'/'+input_name  + ' --itppFile ' + outconvpath.get()+'/'+ itpp_name + " " +othercoll_path.get() + ' --keep')
					os.system ('mv ' + outconvpath.get()+'/'+spf_name + ' ' + outconvpath.get()+'/'+spf_new_name)
			else:
				print ('TestContentTool -INFO-  |	Conversion using NB Resources')
				if (chk_extracoll.get() == ''):
					print ('TestContentTool -INFO-  |	Executing ---> ----> nbq -P sc_normal -C SLES11SP4&&128G -Q ' + nbqslot_combo.get() +' /p/hdk/cad/spf/eng.2021.ww52a/bin/spf_perl_pp --tapSpecFile '+ tapspecpath.get() + ' --stfSpecFile '+ stfspecpath.get() + ' --testSeqFile '+ inconvpath.get()+'/'+ input_name + ' --itppFile ' + outconvpath.get()+'/'+spf_name + ' --keep' +'\n')
					os.system ('nbq -P sc_normal -C "SLES11SP4&&96G" -Q' + nbqslot_combo.get() + ' /p/hdk/cad/spf/eng.2021.ww52a/bin/spf_perl_pp --tapSpecFile '+ tapspecpath.get() + ' --stfSpecFile '+ stfspecpath.get() + ' --testSeqFile '+ inconvpath.get()+'/'+input_name  + ' --itppFile ' + outconvpath.get()+'/'+itpp_name + ' --keep')
				else:
					print ('TestContentTool -INFO-  |	Executing ---> ----> nbq -P sc_normal -C SLES11SP4&&128G -Q ' + nbqslot_combo.get() +' /p/hdk/cad/spf/eng.2021.ww52a/bin/spf_perl_pp --tapSpecFile '+ tapspecpath.get() + ' --stfSpecFile '+ stfspecpath.get() + ' --testSeqFile '+ inconvpath.get()+'/'+ input_name + ' --itppFile ' + outconvpath.get()+'/'+itpp_name + ' --keep' +'\n')
					os.system ('nbq -P sc_normal -C "SLES11SP4&&96G" -Q' + nbqslot_combo.get() + ' /p/hdk/cad/spf/eng.2021.ww52a/bin/spf_perl_pp --tapSpecFile '+ tapspecpath.get() + ' --stfSpecFile '+ stfspecpath.get() + ' --testSeqFile '+ inconvpath.get()+'/'+input_name  + ' --itppFile ' + outconvpath.get()+'/'+itpp_name + " " + othercoll_path.get() + ' --keep')
		if input_name.endswith(".itpp"):
			print("TestContentTool -INFO-  |	Converting file: "+inconvpath.get()+'/'+input_name+ ' to SPF Format')
			spf_name = input_name.replace('itpp','spf')
			copyfile(inconvpath.get()+'/'+input_name,outconvpath.get()+'/'+spf_name)		
			with open(outconvpath.get()+'/'+spf_name, 'r+') as fr:
				list_of_lines = fr.readlines()
			with open(outconvpath.get()+'/'+spf_name, 'w+') as fw:
				for line in list_of_lines:
					if (line in ['\n', '\r\n']):
						fw.write("\n")
					else:
						fw.write("pass itpp \"" + line.strip() + '";\n')
						
	if (nbqslot_value.get() == ''):
		print("TestContentTool -INFO-  |	Total Files Processed: {}!!\n".format(cnt_files_conv))
		print("TestContentTool -INFO-  |	Content Conversion is Done!")
	else: 
		print("TestContentTool -INFO-  |	Jobs Submitted to NB queue!!\n")
	
	
def env_conv_setup(*args):
	print('TestContentTool -INFO-  |	source /p/hdk/cad/spf/eng.2021.ww52a/bin/spf_setup_env')
	os.system ('source /p/hdk/cad/spf/eng.2021.ww52a/bin/spf_setup_env')

	
def start_conv_def(*args):  
	print('\n======================================================================================\n')
	print('TestContentTool -INFO-  |	Running conversion...')
	#env_conv_setup()
	format_conversion()
	os.system("rm *query*")
	print( "TestContentTool -EXIT- " + "%s"%datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + "\n")
	print('\n======================================================================================\n')
	exit()
		
chk_spf2itpp = StringVar()
chk_espf2spf = StringVar()
chk_itpp2spf = StringVar()
chk_spf2itpp.set('0')
chk_espf2spf.set('0')
chk_itpp2spf.set('0')

chk_extracoll = StringVar()
resource_value = StringVar()
nbqslot_value = StringVar()
inconvpath = StringVar()
outconvpath = StringVar()
modelpath = StringVar()
tapspecpath = StringVar()
stfspecpath = StringVar()
othercollpath = StringVar()
othercollpath.set('Format: --templateFile <path>/test_spf.template')

sep = ttk.Separator(conversionframe, orient="horizontal")
sep.grid(column=1, row=2, sticky='we', columnspan=8)

ttk.Label(conversionframe, text='Conversion').grid(column=1, row=4, sticky=E)

sepv = ttk.Separator(conversionframe, orient="vertical")
sepv.grid(column=2, row=3, sticky='ns', rowspan=3)

check_SPF2ITPP = ttk.Checkbutton(conversionframe, text='SPF->ITPP', variable=chk_spf2itpp, command=chk_spf2itpp_def, onvalue='1', offvalue='0')
check_SPF2ITPP.grid(column=3, row=3, sticky=W)

check_espf2spf = ttk.Checkbutton(conversionframe, text='ESPF->SPF', variable=chk_espf2spf, command=chk_espf2spf_def, onvalue='1', offvalue='0')
check_espf2spf.grid(column=3, row=4, sticky=W)

check_ITPP2SPF = ttk.Checkbutton(conversionframe, text='ITPP->SPF', variable=chk_itpp2spf, command=chk_itpp2spf_def, onvalue='1', offvalue='0')
check_ITPP2SPF.grid(column=3, row=5, sticky=W)

sep = ttk.Separator(conversionframe, orient="horizontal")
sep.grid(column=1, row=6, sticky='we', columnspan=8)

ttk.Label(conversionframe, text='Run Resources:').grid(column=1, row=7, sticky=E)
resource_combo = ttk.Combobox(conversionframe, textvariable=resource_value, width=15, state='disable')
resource_combo['values'] = ("Netbatch", "Local")
resource_combo.grid(column=2, row=7, sticky=W)
resource_combo.bind('<<ComboboxSelected>>', resource_selected)

ttk.Label(conversionframe, text='NB QSLOT:').grid(column=4, row=7, sticky=E)
nbqslot_combo = ttk.Combobox(conversionframe, textvariable=nbqslot_value, width=15, state='disable')
nbqslot_combo['values'] = ("/MVE/ATV/CLK", "/MVE/ATV/MIO","/MVE/ATV/PTI", "/MVE/ATV/SIO","/MVE/ATV/FUSE", "/MVE/ATV/HTD", "/MVE/PQV/DTV/scan", "/MVE/PQV/DTV/array", "/MVE/PQV/DTV/functional")
nbqslot_combo.grid(column=5, row=7, sticky=W)
nbqslot_combo.bind('<<ComboboxSelected>>', nbqslot_selected)

ttk.Label(conversionframe, text='Input Path:').grid(column=1, row=8, sticky=E)
inconv_path = ttk.Entry(conversionframe, width=90, textvariable=inconvpath, state='disable')
inconv_path.grid(column=2, row=8, sticky=(W, W), columnspan=6)
inconv_path_button = ttk.Button(conversionframe, text='...',width=3, command=get_inconv_path, state='disable')
inconv_path_button.grid(column=8, row=8, sticky=W)

ttk.Label(conversionframe, text='Output Path:').grid(column=1, row=9, sticky=E)
outconv_path = ttk.Entry(conversionframe, width=90, textvariable=outconvpath, state='disable')
outconv_path.grid(column=2, row=9, sticky=(W, W), columnspan=6)
outconv_path_button = ttk.Button(conversionframe, text='...',width=3, command=get_outconv_path, state='disable')
outconv_path_button.grid(column=8, row=9, sticky=W)

ttk.Label(conversionframe, text='TAP SPEC Path:').grid(column=1, row=10, sticky=E)
tapspec_path = ttk.Entry(conversionframe, width=90, textvariable=tapspecpath, state='disable')
tapspec_path.grid(column=2, row=10, sticky=(W, W), columnspan=6)
tapspec_path_button = ttk.Button(conversionframe, text='...',width=3, command=get_tapspec_path, state='disable')
tapspec_path_button.grid(column=8, row=10, sticky=W)

ttk.Label(conversionframe, text='STF SPEC Path:').grid(column=1, row=11, sticky=E)
stfspec_path = ttk.Entry(conversionframe, width=90, textvariable=stfspecpath, state='disable')
stfspec_path.grid(column=2, row=11, sticky=(W, W), columnspan=6)
stfspec_path_button = ttk.Button(conversionframe, text='...',width=3, command=get_stfspec_path, state='disable')
stfspec_path_button.grid(column=8, row=11, sticky=W)

check_EXTRACOLL = ttk.Checkbutton(conversionframe, text='Additional Inputs?', variable=chk_extracoll, command=chk_extracoll_def, onvalue='1', offvalue='0', state='disable')
check_EXTRACOLL.grid(column=2, row=12, sticky=W)

ttk.Label(conversionframe, text='++ Collaterals:').grid(column=1, row=13, sticky=E)
othercoll_path = ttk.Entry(conversionframe, width=90, textvariable=othercollpath, state='disable')
othercoll_path.grid(column=2, row=13, sticky=(W, W), columnspan=6)
othercoll_path_button = ttk.Button(conversionframe, text='...',width=3, command=get_othercoll_path, state='disable')
othercoll_path_button.grid(column=8, row=13, sticky=W)

sep = ttk.Separator(conversionframe, orient="horizontal")
sep.grid(column=1, row=15, sticky='we', columnspan=8)

start_conv_button = ttk.Button(conversionframe, text='Start', width=6, command=start_conv_def, state='disable')
start_conv_button.grid(column=8, row=16, sticky=W)

clear_conv_button = ttk.Button(conversionframe, text='Clear', width=6, command=clear_conv_def)
clear_conv_button.grid(column=7, row=16,sticky=E)


##############################################################################################
##################################### checkin FRAME #######################################
##############################################################################################




all_modules = []
all_parentProd = []

if (product_stepping.get() in ( "spr_a0", "spr_b0", "spr_c0", "spr_d0", "spr_e0", "spr_e1", "spr_e3")):
	all_parentProd = ["spr_a0", "spr_b0", "spr_c0", "spr_d0", "spr_e0", "spr_e1", "spr_e3"]
	os.system("linus_qry -q lineitem.prd=spr lineitem.step=u0 -- -pl owner -- > linus_query_modules.txt")
elif (product_stepping.get() in ( "spr_r0", "spr_s0")): 
	all_parentProd = ["spr_r0", "spr_s0"]
	os.system("linus_qry -q lineitem.prd=spr lineitem.step=u0 -- -pl owner -- > linus_query_modules.txt")
elif (product_stepping.get() == "spr_u0"): 
	all_parentProd = ["spr_u0"]
	os.system("linus_qry -q lineitem.prd=spr lineitem.step=u0 -- -pl owner -- > linus_query_modules.txt")
elif (product_stepping.get() == "spr_u1"): 
	all_parentProd = ["spr_u0","spr_u1"]
	os.system("linus_qry -q lineitem.prd=spr lineitem.step=u1 -- -pl owner -- > linus_query_modules.txt")
else:
	all_parentProd = ["spr_l0"]
	os.system("linus_qry -q lineitem.prd=spr lineitem.step=l0 -- -pl owner -- > linus_query_modules.txt")

all_lineitems = []	


def modify_linus_file(fname):
	temp_list = []
	with open(fname, 'r') as file:
		lines = file.readlines()

	with open(fname, 'w') as file:
		for line in lines:
			try:
				temp_list = line.split()
				if not 'linus_qry' in temp_list:
					file.write(temp_list[0]+'\n')
			except Exception as er:
				pass

def get_intent_file(fname):
	temp_list = []
	with open(fname, 'r') as file:
		lines = file.readlines()
		for line in lines:
			if "intent :" in line:
				return line
		
def get_path_file(fname):
	temp_list = []
	with open(fname, 'r') as file:
		lines = file.readlines()
		for line in lines:
			if "path :" in line:
				return line
				
modify_linus_file('linus_query_modules.txt')	
			
with open('linus_query_modules.txt') as inFile_mod:
	all_modules = [line for line in inFile_mod]
	for i in range (len(all_modules)):
		all_modules[i] = all_modules[i].replace('\n','')


def disable_widget(dis_widget):  
    try:
        for dwg in dis_widget:
            dwg['state'] = 'disable'
    except Exception as er:
        print('TestContentTool -INFO-  |	disable_widget error: ', er)

def disable_widget_single(dis_widget):  
	try:
		dis_widget['state'] = 'disable'
	except Exception as er:
		print('TestContentTool -INFO-  |	disable_widget error: ', er)

def enable_widget(en_widget): 
	try:
		for dwg in en_widget:
			dwg['state'] = 'normal'
	except Exception as er:
		print('TestContentTool -INFO-  |	enable_widget error: ', er)

def enable_widget_single(en_widget): 
	try:
		en_widget['state'] = 'normal'
	except Exception as er:
		print('TestContentTool -INFO-  |	enable_widget error: ', er)

def get_spf_path(): 
	print("TestContentTool -INFO-  |	Setting SPF path")
	try:
		spfpath.set(askdirectory())
		if (chk_vcf.get() == '1' and vcfVrev_value.get() != '' and vcfVectype_value.get() != '' and vcfVmode_value.get() != '' and chk_pcar.get() == '0'):
			enable_widget_single(start_button)
		elif (chk_pcar.get() == '1' and re_plist.get() != '' and PCARsetup_value.get() != '' and setuppath.get() != ''):
			enable_widget_single(start_button)
		elif (chk_vcf.get() == '0' and chk_pcar.get() == '0'):
			enable_widget_single(start_button)
	except Exception as er:
		writelog('get_tpname error: ' + repr(er))

def get_tid_file():
	print("TestContentTool -INFO-  |	Getting TID path")
	try:
		tidpath.set(askopenfilename(filetypes=(('XML files', '*.list'), ("All files", "*.*"))))
		if (chk_vcf.get() == '1' and vcfVrev_value.get() != '' and vcfVectype_value.get() != '' and vcfVmode_value.get() != ''):
			enable_widget_single(start_button)
		elif (chk_pcar.get() == '1' and re_plist.get() != '0' and PCARsetup_value.get() != ''):
			enable_widget_single(start_button)
		elif (chk_vcf.get() == '0' and chk_pcar.get() == '0'):
			enable_widget_single(start_button)
			
	except Exception as er:
		writelog('get_tpname error: ' + repr(er))

def get_tuple_file(): 
	tuplepath.set(askopenfilename(filetypes=(('List files', '*.list'), ("All files", "*.*"))))
	if (chk_vcf.get() == '1' and vcfVrev_value.get() != '' and vcfVectype_value.get() != '' and vcfVmode_value.get() != ''):
		enable_widget_single(start_button)

def get_setup_file(): 
	print("TestContentTool -INFO-  |	Getting Setup path")
	setuppath.set(askopenfilename(filetypes=(('XML files', '*.xml'), ("All files", "*.*"))))
	if (chk_vcf.get() == '1' and vcfVrev_value.get() != '' and vcfVectype_value.get() != '' and vcfVmode_value.get() != ''):
		enable_widget_single(start_button)
	elif (chk_pcar.get() == '1' and PCARsetup_value.get() != ''):
		enable_widget_single(start_button)
	elif (chk_pcar.get() == '0'):
		enable_widget_single(start_button)
	elif (chk_clone_gen.get() == '1'):
		enable_widget_single(start_button)

def get_pcar3_file(): 
	print("TestContentTool -INFO-  |	Getting .pcar path")
	pcar3path.set(askopenfilename(filetypes=((',pcar files', '*.pcar'), ("All files", "*.*"))))
	if (chk_pcar.get() == '1'):
		enable_widget_single(start_button)
			
def get_plist_file():  
	plistpath.set(askopenfilename(filetypes=(('Plist files', '*.plist'), ("All files", "*.*"))))
	if (chk_vcf.get() == '1' and vcfVrev_value.get() != '' and vcfVectype_value.get() != '' and vcfVmode_value.get() != ''):
		enable_widget_single(start_button)

def plist_reuse_format_def():
	if (re_plist.get() == '0'):
		print("TestContentTool -INFO-  |	Plist Reuse Desactivated")
		disable_widget((plist_path,plist_path_button))
		plistpath.set('')
		enable_widget_single(setup_plist)
	else:
		print("TestContentTool -INFO-  |	Plist Reuse Activated")
		enable_widget((plist_path,plist_path_button,PCARsetup_combo))
		disable_widget_single(setup_plist)	
	
	if (setuppath.get() != ''):
		enable_widget_single(start_button)
		
def display_PCARsetup(*args):
	if (PCARsetup_value.get() == 'clone file'):
		print("TestContentTool -INFO-  |	Plist Setup Desactivated")
		enable_widget((setup_path,setup_path_button,PCARsetup_combo))
		if (TIDsrc_value.get() != 'from plist'):
			disable_widget((plist_path,plist_path_button,pcar3_path,pcar3_path_button))
			setuppath.set('')
	elif (PCARsetup_value.get() == 'plist file'):
		print("TestContentTool -INFO-  |	Plist Setup Activated")
		disable_widget((setup_path,setup_path_button,pcar3_path,pcar3_path_button))
		enable_widget((plist_path,plist_path_button))
	elif (PCARsetup_value.get() == 'clone+ref'):
		print("TestContentTool -INFO-  |	PCAR will be generated based on clone structure and reference input")
		disable_widget((pcar3_path,pcar3_path_button))
		enable_widget((plist_path,plist_path_button,setup_path,setup_path_button))
	else:
		print("TestContentTool -INFO-  |	Plist Generation from .pcar")
		disable_widget((pcar3_path,pcar3_path_button))
		enable_widget((pcar3_path,pcar3_path_button))		
	if (setuppath.get() != ''):
		enable_widget_single(start_button)
	
def display_TIDsrc(*args):
	print("TestContentTool -INFO-  |	TID SRC:")
	if (TIDsrc_value.get() == 'from plist'):
		print('TestContentTool -INFO-  |	from plist')
		disable_widget((tid_path,tid_path_button))
		if(PCARsetup_value.get() != 'plist'):
			enable_widget((plist_path,plist_path_button))
		tidpath.set('')
	else:
		print('TestContentTool -INFO-  |	from list')
		enable_widget((tid_path,tid_path_button))
		if(PCARsetup_value.get() != 'from plist'):
			disable_widget((plist_path,plist_path_button))

def display_lineitem(*args): 
	print("TestContentTool -INFO-  |	LineItem Selected: " + li_value.get())

def chk_clone_generation():
	newSetupOut = "clone_out.xml"
	try:
		os.mknod("setup_out.xml")
	except:
		print("")
	if (chk_clone_gen.get() == '1'):
		enable_widget((plist_path,plist_path_button,setup_path,setup_path_button))
	else:
		disable_widget((plist_path,plist_path_button,setup_path,setup_path_button))
		
def setup_generation():
	status = 0
	rundir = ""
	print ("TestContentTool -INFO-  |	Building setup file from plist")
	globalPlist_key = ''	
	list_PList_key = []
	list_patterns_key = []
	list_PostBurst_key = []
	list_PreBurst_key = []
	dictPlist = {}
	dictIntent = {}
	plist_postBurst = ''
	plist_preBurst = ''
	cnt_max_size = 0
	intent = ''
	
	with open(plistpath.get()) as plistfile:
		for line in plistfile:
			if (re.match('GlobalPList', line.strip())):
				line = line.lstrip()
				tempList = line.split(" ")
				globalPlist_key = tempList[1].strip()
				dictPlist[globalPlist_key] = {}
				dictPlist[globalPlist_key]["pats"] = []
				dictPlist[globalPlist_key]["spf"] = []
				dictPlist[globalPlist_key]["PostBurst"] = []
				dictPlist[globalPlist_key]["PreBurst"] = []
				dictPlist[globalPlist_key]["PList"] = []
				dictPlist[globalPlist_key]["Burst"] = []
				print ("TestContentTool -INFO-  |	Processing GlobalPList: " + globalPlist_key)
				print ("--------------------------------------------------------------------------")
				if "Burst" in line:
					if "PreBurst" in line:
						regexp = re.search('PreBurstPList\s\w+',line)
						dictPlist[globalPlist_key]["Burst"] = 'YES'
						dictPlist[globalPlist_key]['PreBurst'].append(regexp.group(0))
					else:
						dictPlist[globalPlist_key]['PreBurst'].append('nopre')
					if "PostBurst" in line:
						dictPlist[globalPlist_key]["Burst"] = 'YES'
						regexp = re.search('PostBurstPList\s\w+',line)
						dictPlist[globalPlist_key]['PostBurst'].append(regexp.group(0))
					else:
						dictPlist[globalPlist_key]['PostBurst'].append('nopost')
				else:
					dictPlist[globalPlist_key]["Burst"] = 'NO'	
			if (re.match('Pat', line.strip())):
				tid_regex = re.findall('[0-9]+', line)
				spf_name = re.search("x00_(.*?);",line).group(1)
				dictPlist[globalPlist_key]["pats"].append(tid_regex[1])
				dictPlist[globalPlist_key]["spf"].append(spf_name)
				print ("TestContentTool -INFO-  |	TID from input:" + tid_regex[1] + " | SPF Name from input: "+ spf_name)

			if (re.match("PList", line.strip())):
				dictPlist[globalPlist_key]["PList"].append(line.split()[1].replace(';',''))
						
	print("TestContentTool -INFO-  |	All Plist data migrated to Setup File")
	for plist in dictPlist.keys():
		for PList in dictPlist[plist]["PList"]:
			print("TestContentTool -INFO-  |	PL: " +PList)
			for pattern in dictPlist[plist]["pats"]:
				print("TestContentTool -INFO-  |	TID: " + pattern)
	print ("--------------------------------------------------------")
	
	SetupFromPlist = WriteSetupFromPlist (dictPlist)
	print ("TestContentTool -INFO-  |	Plist Clone is done")
	os.system("rm *query*")
	print( "TestContentTool -EXIT- " + "%s"%datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + "\n")
	print('\n======================================================================================\n')
	exit()
	
def module_selected(*args): 
	module_found = ''
	print("TestContentTool -INFO-  |	Module Selected: " + mod_value.get())
	enable_widget((check_VAULT,check_ITRACE,check_VCF,check_PCAR,check_Clone,lineitem_combo))
	module_found = mod_value.get()
	module_found = module_found.replace('\n','')
	
	if (product_stepping.get() == "spr_u0"): 
		prod = "spr"
		step = "u0"
	elif (product_stepping.get() == "spr_u1"): 
		prod = "spr"
		step = "u1"
	elif (product_stepping.get() == "spr_l0"): 
		prod = "spr"
		step = "l0"
	
	os.system("linus_qry -q lineitem.prd="+ prod + " lineitem.step=" +step+ " lineitem.owner="+module_found+ " -- -pl name -- > linus_query_li.txt")
	modify_linus_file('linus_query_li.txt')
	with open('linus_query_li.txt') as inFile_li:
		all_lineitems = [line for line in inFile_li]
		for i in range (len(all_lineitems)):
			all_lineitems[i] = all_lineitems[i].replace('\n','')
	lineitem_combo['values'] = tuple(all_lineitems)

def parent_selected(*args): 

	print("TestContentTool -INFO-  |	Parent Prod Selected: " + parent_value.get())
	parent_prod = parent_value.get()

	
def start_def(): 
	print('\n======================================================================================\n')
	print( " *** Running Content Check-in " + "%s"%datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + "\n")
	if (chk_clone_gen.get() == '1'):
		setup_generation()
	elif (chk_itrace.get() == '1') or (chk_vault.get() == '1') or (chk_vcf.get() == '1') or (chk_pcar.get() == '1'):
		print( " *** ")
		TVPV_Execution_Split()
	else:
		print ('TestContentTool -INFO-  |	No valid Selection')

	os.system("rm *query*")
	print( "TestContentTool -EXIT- " + "%s"%datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + "\n")
	print('\n======================================================================================\n')
	exit()

def chk_vault_def():  
	if (chk_vault.get() == '0'):
		print('TestContentTool -INFO-  |	Vault Step Deselected')
		chk_vault.set('0')
		disable_widget((spf_path,spf_path_button,parent_combo))
		spfpath.set('')
		li_value.set('')
		parent_value.set('')
		if(chk_itrace.get() == '1'):
			enable_widget_single(TIDsrc_combo)
			disable_widget((spf_path,spf_path_button))
			spfpath.set('')
		else:
			disable_widget((spf_path,spf_path_button))
			spfpath.set('')
			if(chk_vcf.get() == '1'):
				enable_widget((vcfVmode_combo, vcfVectype_combo,vcfVrev_combo))
				enable_widget((tuple_path,tuple_path_button))
			elif (chk_pcar.get() == '0'):
				enable_widget_single(check_Clone)
	else:
		disable_widget_single(check_Clone)
		chk_vault.set('1')
		if(chk_itrace.get() == '1'):
			disable_widget((tid_path,tuple_path))
			tidpath.set('')
		else:
			if(chk_vcf.get() == '1'):
				enable_widget((vcfVmode_combo, vcfVectype_combo,vcfVrev_combo))
				chk_itrace.set('1')
				disable_widget((tuple_path,tuple_path_button))
				tuplepath.set('')
		print('TestContentTool -INFO-  |	Vault Step Selected')
		disable_widget_single(TIDsrc_combo)
		TIDsrc_value.set('')
		enable_widget((spf_path,spf_path_button,parent_combo))

def chk_itrace_def():  
	print('TestContentTool -INFO-  |	iTrace Step Selected')
	if (chk_itrace.get() == '0'):
		re_tid.set('')
		TIDsrc_value.set('')
		disable_widget((TIDsrc_combo,plist_path,plist_path_button,tid_path))
		plistpath.set('')
		tidpath.set('')
		if ((chk_vault.get() == '0') and (chk_vcf.get() == '1')):
			enable_widget((tuple_path,tuple_path_button))
			enable_widget((vcfVmode_combo, vcfVectype_combo,vcfVrev_combo))
		if ((chk_vault.get() == '1') and (chk_vcf.get() == '1')):
			chk_itrace.set('1')
		if ((chk_vault.get() == '0') and (chk_vcf.get() == '0') and (chk_pcar.get() == '0')):
			enable_widget_single(check_Clone)
	else:
		disable_widget_single(check_Clone)
		if (chk_vault.get() == '0'):
			enable_widget_single(TIDsrc_combo)
			disable_widget((tuple_path,tuple_path_button))
			tuplepath.set('')
	
def chk_vcf_def():  
	print('TestContentTool -INFO-  |	VCF Step Selected')
	enable_widget((vcfVmode_combo, vcfVectype_combo,vcfVrev_combo))
	if (chk_vault.get() == '0'):
		vcfVmode_value.set('')
		vcfVectype_value.set('')
		vcfVrev_value.set('')
		if (chk_itrace.get() == '0'):
			enable_widget((tuple_path,tuple_path_button))

			disable_widget((spf_path,spf_path_button))
			spfpath.set('')
			if ((chk_vcf.get() == '0') and (chk_pcar.get() == '0')):
				enable_widget_single(check_Clone)
		else:
			enable_widget((tid_path,tid_path_button))
			disable_widget((tuple_path,tuple_path_button))
			tuplepath.set('')
			if (chk_vcf.get() == '1'):
				enable_widget((vcfVmode_combo, vcfVectype_combo,vcfVrev_combo))
				if (TIDsrc_value.get() == 'from list'):
					enable_widget((tid_path,tid_path_button))
					disable_widget_single(vcf_path)
				else:
					enable_widget((plist_path,plist_path_button))
					disable_widget_single(tuple_path)
	else:
		if (chk_itrace.get() == '0'):
			chk_itrace.set('1')
			
	if ((chk_vcf.get() == '0') or (chk_vcf.get() == '')):
		disable_widget((vcfVmode_combo, vcfVectype_combo,vcfVrev_combo))
		disable_widget((tuple_path,tuple_path_button))
		tuplepath.set('')
	else: disable_widget_single(check_Clone)

def chk_pcar_def():  
	print('TestContentTool -INFO-  |	PCAR3 Step Selected')
	if (chk_pcar.get() == '0'):
		re_plist.set('')
		PCARsetup_value.set('')
		disable_widget((PCARsetup_combo,setup_path,setup_path_button,vcfVmode_combo,vcfVectype_combo,vcfVrev_combo))
		setuppath.set('')
		pcar3path.set('')
		if ((chk_vault.get() == '0') and (chk_vcf.get() == '0') and (chk_itrace.get() == '0')):
			enable_widget_single(check_Clone)
	else:
		disable_widget_single(check_Clone)
		enable_widget_single(PCARsetup_combo)
		enable_widget((vcfVmode_combo, vcfVectype_combo,vcfVrev_combo))

def display_vcfVrev (*args):  
	print ("TestContentTool -INFO-  |	VREV: " + vcfVrev_value.get() )
	if (chk_vcf.get() == '1' and vcfVrev_value.get() != '' and vcfVectype_value.get() != '' and vcfVmode_value.get() != '' and tuplepath.get() != ''):
			enable_widget_single(start_button)
			
def display_vcfVmode (*args): 
	print ("TestContentTool -INFO-  |	VMode: " + vcfVmode_value.get() )
	if (chk_vcf.get() == '1' and vcfVrev_value.get() != '' and vcfVectype_value.get() != '' and vcfVmode_value.get() != '' and tuplepath.get() != ''):
			enable_widget_single(start_button)
			
def display_vcfVectype (*args):  
	print ("TestContentTool -INFO-  |	VecType: " + vcfVectype_value.get() )
	if (chk_vcf.get() == '1' and vcfVrev_value.get() != '' and vcfVectype_value.get() != '' and vcfVmode_value.get() != '' and tuplepath.get() != ''):
			enable_widget_single(start_button)			
			
def clear_def(*args):  
	widgets = (lineitem_combo, vcfVmode_combo, vcfVectype_combo,vcfVrev_combo, PCARsetup_combo, TIDsrc_combo, check_VAULT, check_VCF, check_ITRACE, check_PCAR, start_button, spf_path, spf_path_button, tid_path, tid_path_button, 
		      tuple_path, tuple_path_button, pcar3_path, pcar3_path_button, setup_path, setup_path_button, plist_path, plist_path_button)
	variables = (vcfVrev_value, vcfVectype_value, vcfVmode_value, re_plist, mod_value, PCARsetup_value, re_tid, TIDsrc_value, li_value, spfpath, tidpath, tuplepath, setuppath, pcar3path, plistpath)
	chk_variables = (chk_vcf, chk_itrace, chk_pcar,chk_vault)
	for var in variables:
		var.set('')
	for var in chk_variables:
		var.set('0')
	disable_widget(widgets)


re_plist = StringVar()
re_plist.set('0')
PCARsetup_value = StringVar()
PCARsetup_value.set('')
TIDsrc_value = StringVar()
TIDsrc_value.set('')
re_tid = StringVar()
re_tid.set('0')
chk_vcf = StringVar()
chk_vcf.set('0')
chk_itrace = StringVar()
chk_itrace.set('0')
chk_pcar = StringVar()
chk_pcar.set('0')
chk_clone_gen = StringVar()
chk_clone_gen.set('0')
li_value = StringVar()
mod_value = StringVar()
parent_value = StringVar()
tp_val = IntVar()
chk_vcfval = IntVar()
li_value.set('')
mod_value.set('')
parent_value.set('')
chk_vault = StringVar()
chk_vault.set('0')
spfpath = StringVar()
tidpath = StringVar()
plistpath = StringVar()
setuppath = StringVar()
pcar3path = StringVar()
tuplepath = StringVar()
vcfVrev_value= StringVar()
vcfVectype_value= StringVar()
vcfVmode_value= StringVar()
vcfVrev_value.set('')
vcfVectype_value.set('')
vcfVmode_value.set('')

test_type = StringVar()
owner = StringVar()
attribute = StringVar()
tag = StringVar()
preBurstPlist = StringVar()
postBurstPlist = StringVar()
test_type.set('')
owner.set('')
attribute.set('')
tag.set('')
preBurstPlist.set('') 
postBurstPlist.set('')

sep = ttk.Separator(checkinframe, orient="horizontal")
sep.grid(column=1, row=0, sticky='we', columnspan=10)

ttk.Label(checkinframe, text='Stepping:').grid(column=1, row=1, sticky=E)
ttk.Label(checkinframe, textvariable=product_stepping, font='Helvetica 14 bold', foreground="blue").grid(column=2, row=1, sticky=W,columnspan=2)

sep = ttk.Separator(checkinframe, orient="horizontal")
sep.grid(column=1, row=2, sticky='we', columnspan=10)

ttk.Label(checkinframe, text='Steps to').grid(column=1, row=4, sticky=E)
ttk.Label(checkinframe, text='  Run   ').grid(column=1, row=5, sticky=E)
sepv = ttk.Separator(checkinframe, orient="vertical")
sepv.grid(column=2, row=3, sticky='ns', rowspan=4)

sep = ttk.Separator(checkinframe, orient="horizontal")
sep.grid(column=1, row=7, sticky='we', columnspan=10)

check_VAULT = ttk.Checkbutton(checkinframe, text='Vault', variable=chk_vault, command=chk_vault_def, onvalue='1', offvalue='0', state='disable')
check_VAULT.grid(column=3, row=3, sticky=W)
check_ITRACE = ttk.Checkbutton(checkinframe, text='iTRACE', variable=chk_itrace, command=chk_itrace_def, onvalue='1', offvalue='0', state='disable')
check_ITRACE.grid(column=3, row=4, sticky=W)
check_VCF = ttk.Checkbutton(checkinframe, text='VCF', variable=chk_vcf, command=chk_vcf_def, onvalue='1', offvalue='0', state='disable')
check_VCF.grid(column=3, row=5, sticky=W)
check_PCAR = ttk.Checkbutton(checkinframe, text='Plist Gen', variable=chk_pcar, command=chk_pcar_def, onvalue='1', offvalue='0', state='disable')
check_PCAR.grid(column=3, row=6, sticky=W)

check_Clone = ttk.Checkbutton(checkinframe, text='Plist Clone', variable=chk_clone_gen, command=chk_clone_generation, onvalue='1', offvalue='0')
check_Clone.grid(column=7, row=6, sticky=W)

ttk.Label(checkinframe, text='PCAR Source:').grid(column=4, row=6, sticky=E)
PCARsetup_combo = ttk.Combobox(checkinframe, textvariable=PCARsetup_value, width=8, state='disable')
PCARsetup_combo['values'] =  (".pcar file", "clone file", "clone+ref",)
PCARsetup_combo.grid(column=5, row=6, sticky=W)
PCARsetup_combo.bind('<<ComboboxSelected>>', display_PCARsetup)

ttk.Label(checkinframe, text='TID Source:').grid(column=4, row=4, sticky=E)
TIDsrc_combo = ttk.Combobox(checkinframe, textvariable=TIDsrc_value, width=8, state='disable')
TIDsrc_combo['values'] =  ("from list", "from plist")
TIDsrc_combo.grid(column=5, row=4, sticky=W)
TIDsrc_combo.bind('<<ComboboxSelected>>', display_TIDsrc)

ttk.Label(checkinframe, text='VRev:').grid(column=4, row=5, sticky=E)
vcfVrev_combo = ttk.Combobox(checkinframe, textvariable=vcfVrev_value, width=8, state='disable')
vcfVrev_combo['values'] =  ("vrevSU1P", "vrevSU2P", "vrevSL0P")
vcfVrev_combo.grid(column=5, row=5, sticky=W)
vcfVrev_combo.bind('<<ComboboxSelected>>', display_vcfVrev)

ttk.Label(checkinframe, text='Vectype:').grid(column=6, row=5, sticky=E)
vcfVectype_combo = ttk.Combobox(checkinframe, textvariable=vcfVectype_value, width=16, state='disable')
vcfVectype_combo['values'] = ("hvm400", "hvm400RPT", "hvm400t12", "hvm400t25", "hvm400t50", "flat400", "hvm400x8", "mio", "hvm200","hvm200RPT","hvm200utc","hvm200RPTutc","hvm200x8utc","flat200","shops", "hvm200t100hbi", "hbishops", "hvm200t100hbimio")
vcfVectype_combo.grid(column=7, row=5, sticky=W)
vcfVectype_combo.bind('<<ComboboxSelected>>', display_vcfVectype)

ttk.Label(checkinframe, text='Mode:').grid(column=8, row=5, sticky=E)
vcfVmode_combo = ttk.Combobox(checkinframe, textvariable=vcfVmode_value, width=8, state='disable')
vcfVmode_combo['values'] =  ("hdmt2", "hdmt2hbi")
vcfVmode_combo.grid(column=9, row=5, sticky=W)
vcfVmode_combo.bind('<<ComboboxSelected>>', display_vcfVmode)

ttk.Label(checkinframe, text='Module:').grid(column=4, row=1, sticky=E)
module_combo = ttk.Combobox(checkinframe, textvariable=mod_value, width=8)
module_combo['values'] = tuple(all_modules)
module_combo.grid(column=5, row=1, sticky=W)
module_combo.bind('<<ComboboxSelected>>', module_selected)

ttk.Label(checkinframe, text='Parent Prod:').grid(column=4, row=3, sticky=E)
parent_combo = ttk.Combobox(checkinframe, textvariable=parent_value, width=8, state='disable')
parent_combo['values'] = tuple(all_parentProd)
parent_combo.grid(column=5, row=3, sticky=W)
parent_combo.bind('<<ComboboxSelected>>', parent_selected)

ttk.Label(checkinframe, text='Lineitem:').grid(column=6, row=1, sticky=E)
lineitem_combo = ttk.Combobox(checkinframe, textvariable=li_value, width=30, state='disable')
lineitem_combo['values'] = tuple(all_lineitems)
lineitem_combo.grid(column=7, row=1, sticky=W,columnspan=3)
lineitem_combo.bind('<<ComboboxSelected>>', display_lineitem)

ttk.Label(checkinframe, text='SPF Path:').grid(column=1, row=8, sticky=E)
spf_path = ttk.Entry(checkinframe, width=95, textvariable=spfpath, state='disable')
spf_path.grid(column=2, row=8, sticky=(W, W), columnspan=8)
spf_path_button = ttk.Button(checkinframe, text='...',width=3, command=get_spf_path, state='disable')
spf_path_button.grid(column=10, row=8, sticky=W)

ttk.Label(checkinframe, text='TID List:').grid(column=1, row=9, sticky=E)
tid_path = ttk.Entry(checkinframe, width=95, textvariable=tidpath, state='disable')
tid_path.grid(column=2, row=9, sticky=(W, W), columnspan=8)
tid_path_button = ttk.Button(checkinframe, text='...', width=3, command=get_tid_file, state='disable')
tid_path_button.grid(column=10, row=9, sticky=W)

ttk.Label(checkinframe, text='Tuple List:').grid(column=1, row=10, sticky=E)
tuple_path = ttk.Entry(checkinframe, width=95, textvariable=tuplepath, state='disable')
tuple_path.grid(column=2, row=10, sticky=(W, W), columnspan=8)
tuple_path_button = ttk.Button(checkinframe, text='...', width=3, command=get_tuple_file, state='disable')
tuple_path_button.grid(column=10, row=10, sticky=W)

ttk.Label(checkinframe, text='Clone File:').grid(column=1, row=13, sticky=E)
setup_path = ttk.Entry(checkinframe, width=95, textvariable=setuppath, state='disable')
setup_path.grid(column=2, row=13, sticky=(W, W), columnspan=8)
setup_path_button = ttk.Button(checkinframe, text='...', width=3, command=get_setup_file, state='disable')
setup_path_button.grid(column=10, row=13, sticky=W)

ttk.Label(checkinframe, text='.pcar File:').grid(column=1, row=12, sticky=E)
pcar3_path = ttk.Entry(checkinframe, width=95, textvariable=pcar3path, state='disable')
pcar3_path.grid(column=2, row=12, sticky=(W, W), columnspan=8)
pcar3_path_button = ttk.Button(checkinframe, text='...', width=3, command=get_pcar3_file, state='disable')
pcar3_path_button.grid(column=10, row=12, sticky=W)

ttk.Label(checkinframe, text='Plist/TST File:').grid(column=1, row=11, sticky=W)
plist_path = ttk.Entry(checkinframe, width=95, textvariable=plistpath, state='disable')
plist_path.grid(column=2, row=11, sticky=(W, W), columnspan=9)
plist_path_button = ttk.Button(checkinframe, text='...', width=3, command=get_plist_file, state='disable')
plist_path_button.grid(column=10, row=11, sticky=W)

sep = ttk.Separator(checkinframe, orient="horizontal")
sep.grid(column=1, row=15, sticky='we', columnspan=10)

start_button = ttk.Button(checkinframe, text='Start', width=6, command=start_def, state='disable')
start_button.grid(column=10, row=16, sticky=W)

clear_button = ttk.Button(checkinframe, text='Clear', width=6, command=clear_def)
clear_button.grid(column=9, row=16,sticky=E)

product = product_stepping.get()
parent_prod = parent_value.get()

def CheckinLog(message, new=0):
    if new == 1:
        f = open("checkin_log.txt", "w+")
    else:    
        f = open("checkin_log.txt", "a+")
    f.write("\n" + message)
    f.close()

def WriteTIDList(TID_List):
	print("TestContentTool -INFO-  |	Printing TID list file")
	f = open("TID.list", "w+")
	for i in TID_List:
		f.write(i+"\n")
	f.close()

def WriteTupleList(tuple_List):
	print("TestContentTool -INFO-  |	Printing tuple list file")
	f = open("TUPLE.list", "w+")
	for i in tuple_List:
		try:
			f.write(i+"\n")
		except: 
			print("TestContentTool -INFO-  |	Not able to write tuples")
	f.close()
	
def TID_plist_extraction(tidFile, plistpath):
	print ('TestContentTool -INFO-  |	Plist path' + plistpath)
	cnt = 0
	total_patterns =0
	array_tuples = []
	array_TIDs = []
	array_SPFs = []
	with open(plistpath) as pp:
		for line in pp:
			if (re.match('Pat', line.strip())):
				pat_regex = re.findall('[0-9]+', line)
				array_TIDs.append (pat_regex[1])
				print("TestContentTool -INFO-  |	Cnt:{} | TID:{} ".format(cnt, pat_regex[1]))
				cnt+=1
		total_patterns = cnt
		print("TestContentTool -INFO-  |	Total Number of patterns: {}\n".format(total_patterns))
	with open(tidFile, 'w') as f:
		for TID in array_TIDs:
			f.write("%s\n" % TID)
	return array_TIDs

def linus_query ():
	linus_tag =  StringVar()
	linus_testtype =  StringVar()
	linus_attribute =  StringVar()
	prod =  StringVar()
	step =  StringVar()
	
	if (product_stepping.get() == "spr_u0"): 
		prod = "spr"
		step = "u0"
	elif (product_stepping.get() == "spr_u1"): 
		prod = "spr"
		step = "u1"
	elif (product_stepping.get() == "spr_l0"): 
		prod = "spr"
		step = "l0"
		
	os.system("linus_qry -q lineitem.name="+ li_value.get() +" lineitem.prd="+prod+ " lineitem.step="+step +" lineitem.owner="+ mod_value.get() +" -- -pl tag -- > linus_query_tag.txt")
	modify_linus_file('linus_query_tag.txt')
	with open('linus_query_tag.txt') as file_tag:
		linus_tag = file_tag.readline().replace('\n','')
		
	os.system("linus_qry -q lineitem.name="+ li_value.get() +" lineitem.prd="+prod+ " lineitem.step="+step +" lineitem.owner="+ mod_value.get() +" -- -pl testtype -- > linus_query_tt.txt")
	modify_linus_file('linus_query_tt.txt')	
	with open('linus_query_tt.txt') as file_type:
		linus_testtype = file_type.readline().replace('\n','')
	
	os.system("linus_qry -q lineitem.name="+ li_value.get() +" lineitem.prd="+ prod+ " lineitem.step="+step + " lineitem.owner="+ mod_value.get() +" -- -pl attributes -- > linus_query_a.txt")
	modify_linus_file('linus_query_a.txt')	
	with open('linus_query_a.txt') as file_attr:
		linus_attribute = file_attr.readline().replace('\n','')
		
	return linus_tag,linus_testtype,linus_attribute
	
def TVPV_Execution_Split ():
	dictConfig = {}
	dictPattern = {}
	turnin_file = 'turnin.list'
	owner = ''
	linus_tag =  StringVar()
	linus_testtype =  StringVar()
	linus_attribute =  StringVar()
	itracecount = 0
	tuplescount = 0
	TID_List = []
	tempList = []
	tuplesList = []
	tidnumberline = []
	dictSetup = {}
	dictPat = {}
	itrace_file = 'itrace_list.txt'
	itrace_file_plist = 'itrace_list_from_plist.txt'
	vcf_file    = 'vcf_list.txt'
	vcfcount = 0
	exist_TID = ''
	status = 0
	spf_processed = 0
	TID = None
	rtn = 0
	vaultlogstr = ""
	num_files_spf = 0
	spf_list = []
	
	linus_tag, linus_testtype, linus_attribute = linus_query()
	
	dictConfig = {'testtype':'', 'owner':'', 'attribute':'', 'lineitem':'', 'tag':'', 'vrev':'', 'vectype':'', 'mode':'', 'spfarea' :'' , 'vaultarea':'', 
	               'patsarea':'', 'pcar':'', 'dirtag':'','itracework':'','localtidfile':'', 'localtiddb':'', 'preburstplist':'', 'postburstplist':''}
	
	owner = mod_value.get()
	owner = owner[1:]
	
	dictConfig['module']     =  mod_value.get()
	dictConfig['testtype']   =	linus_testtype
	dictConfig['owner']      =	owner
	dictConfig['attribute']  =	linus_attribute
	dictConfig['tag']        =	linus_tag
	dictConfig['lineitem']   =  li_value.get()
	dictConfig['vrev']       =	vcfVrev_value.get()
	dictConfig['vectype']    =	vcfVectype_value.get()
	dictConfig['mode']       =	vcfVmode_value.get()
	dictConfig['spfarea']    =   spfpath.get() 
	dictConfig['vaultarea']  =   os.getcwd()+('/vault_co')
	dictConfig['patsarea']   =   os.getcwd()+('/patarea')
	dictConfig['pcar']       =   os.getcwd()+ '/'+ mod_value.get()+'.pcar'
	dictConfig['dirtag']     =   "itrace_{}".format(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))          
	dictConfig['itracework'] =   os.getcwd()+('/itrace')
	dictConfig['vaultdeposit'] =  os.getcwd()+('/vaultdeposit')
					
	CleanUpArea(dictConfig) #clean up dir
	
	############################# VAULT #############################					
	if(chk_vault.get() == '1'):	
		print ("TestContentTool -INFO-  |	Running Vault...")
	
		for file in os.listdir(spfpath.get()):
			if file.endswith(".spf"):
				num_files_spf += 1
		print ("TestContentTool -INFO-  |	Total SPF found: " + str(num_files_spf))	
		
		for spf_name in os.listdir(spfpath.get()):
			if spf_name.endswith(".spf"):
				print ("TestContentTool -INFO-  |	Searching for test records  for: " + spf_name +"...")
				query_name = os.path.basename(spf_name).split('.')[0]
				TID, rtn = GetTidVault(query_name)
				if (TID == None):
					print ("TestContentTool -INFO-  |	Previous TID does not exist for " + spf_name)
					WriteDepositFile_Vault (turnin_file, spf_name, dictConfig["testtype"], dictConfig["owner"], dictConfig["attribute"], dictConfig["tag"])
					print ("TestContentTool -INFO-  |	Running Vault Deposit ...")
					result, vaultlogstr = RunVaultDeposit(turnin_file)
					while (result == 0):
						print ("TestContentTool -INFO-  |	Vault Deposit Issue, retry!!")
						result, vaultlogstr = RunVaultDeposit(turnin_file)
					print ("TestContentTool -INFO-  |	Vault Deposit Complete!!")	
					tempList = vaultlogstr.split("\n")
					for line in tempList:
						if ("new test_id:" in line):
							tidnumberline = line.split(" ")
							TID_List.append(tidnumberline[6])
							itracecount += 1
							print("TestContentTool -INFO-  |	NEW TID: " +  tidnumberline[6])
							WriteTIDList(TID_List)
				else:
					print ("TestContentTool -INFO-  |	Previous TID found: " + TID)	
					print ("TestContentTool -INFO-  |	Running Vault Check-out ...")		
					RunVaultCheckout(TID, dictConfig['vaultarea'])
					vaultpath = os.path.join(dictConfig['vaultarea'], TID)
					files = [f for f in os.listdir(vaultpath) if os.path.isfile(os.path.join(vaultpath, f))]
					for file in files:
						vaultfile = os.path.join(vaultpath, file)
						sourcefile = os.path.join(spfpath.get(), spf_name)
					print ("vault" + vaultfile + "SPF source" + sourcefile)	
					if filecmp.cmp(sourcefile, vaultfile, shallow=True):
						print ("TestContentTool -INFO-  |	Same Content, no updates on TID:" + TID)
						TID_List.append(TID)
						itracecount += 1
						WriteTIDList(TID_List)
					else:
						print ("TestContentTool -INFO-  |	Updating TID: " + TID )
						shutil.copy(sourcefile, vaultfile)
						result, vaultlogstr = RunVaultCheckin(TID, dictConfig['vaultarea'])
						TID_List.append(TID)
						WriteTIDList(TID_List)
		WriteTIDList(TID_List)
		print ("TestContentTool -INFO-  |	 Summary of TID numbers is placed into TID.list file")
		
	############################ ITRACE ###############################
	if(chk_itrace.get() == '1'):
		print ("TestContentTool -INFO-  |	Running Itrace...")
		
		if (TIDsrc_value.get() == ''):
			if (itracecount > 0):
				print ("TestContentTool -INFO-  |	Running Itrace from previous Vault Output")
				for element in TID_List:
					print ("TestContentTool -INFO-  |	Processing TID: " + element)
				status, tuplescount = RunItrace("TID.list", dictConfig['dirtag'], dictConfig['lineitem'])
		elif (TIDsrc_value.get() == 'from list'):
				print ("TestContentTool -INFO-  |	Running iTrace based on input list: " + tidpath.get())
				with open(tidpath.get()) as iTracesource:
					for line in iTracesource:
						print ("TestContentTool -INFO-  |	Processing TID: " + line.strip())
						TID_List.append(line)
				status, tuplescount = RunItrace(tidpath.get(), dictConfig['dirtag'], dictConfig['lineitem'])
		elif (TIDsrc_value.get() == 'from plist'):
				print ("TestContentTool -INFO-  |	Running iTrace based on plist")
				TID_List = TID_plist_extraction(itrace_file_plist, plistpath.get())
				for element in TID_List:
					print ("TestContentTool -INFO-  |	Processing TID: " + element)
				status, tuplescount = RunItrace(itrace_file_plist, dictConfig['dirtag'], dictConfig['lineitem'])
		else:
			print("TestContentTool -INFO-  |	ITRACE: No Pattern To Run!")	
	
		if (status == 1): 
			print("TestContentTool -INFO-  |	Waiting for tuples to be refresh ...")
			time.sleep(60)
			print("TestContentTool -INFO-  |	Waiting for tuples to be refresh ...")
			time.sleep(60)
			print("TestContentTool -INFO-  |	Waiting for tuples to be refresh ...")
			time.sleep(60)
			tuplesList = get_tupleList(TID_List)
			WriteTupleList(tuplesList)
					
		print("TestContentTool -INFO-  |	ITRACE Complete!!! TUPLES.list and TID.list files generated")
	
	
	#########################  VCF ##########################
	if(chk_vcf.get() == '1'):	
		if (tuplepath.get()==''):
			#vcfcount = WriteVcfFile(vcf_file, dictPattern)
			if (tuplescount > 0 ):
				print ("TestContentTool -INFO-  |	Runnning VCF from previous iTrace result")
				with open("TUPLE.list") as vcfsource:
					for line in vcfsource:
						print ("TestContentTool -INFO-  |	Processing Tuple: " + line.strip())
				status, rtn = RunVcf("TUPLE.list", vcfVrev_value.get(), vcfVectype_value.get(), vcfVmode_value.get())				
			else:
				print("TestContentTool -INFO-  |	VCF: No Pattern To Run!")
		else:
			print ("TestContentTool -INFO-  |	Running VCF from list with tuples")
			print("TestContentTool -INFO-  |	Tuple List: " + tuplepath.get() + "  |	vrev: " + vcfVrev_value.get() + " |	vectype: " + vcfVectype_value.get() + " |	mode: " + vcfVmode_value.get())
			with open(tuplepath.get()) as vcfsource:
					for line in vcfsource:
						print ("TestContentTool -INFO-  |	Processing Tuple: " + line.strip())
			status, rtn = RunVcf(tuplepath.get(), vcfVrev_value.get(), vcfVectype_value.get(), vcfVmode_value.get())
		print ("TestContentTool -INFO-  |	VCF is Complete!! Check results on Rundir Folder")

	######################## GEN PLIST #####################
	if (chk_pcar.get() == '1'):
		if (chk_vcf.get() == '1'):
			time.sleep(60)
			time.sleep(60)
		xmlTree = None
		if((plistpath.get() != '') and (setuppath.get() == '')):
			print ("TestContentTool -INFO-  |	 Generating .pcar from exisiting plist")
			print("TestContentTool -INFO-  |	  Plist Path: " + plistpath.get())
			with open(plistpath.get()) as plistfile:
				for line in plistfile:
					if (re.match('GlobalPList', line.strip())):
						tempList = line.split(" ")
						globalPlist_key = tempList[1].strip()
						dictPlist[globalPlist_key] = {}
						dictPlist[globalPlist_key]["pats"] = []
						dictPlist[globalPlist_key]["PostBurst"] = []
						dictPlist[globalPlist_key]["PreBurst"] = []
						dictPlist[globalPlist_key]["PList"] = []
						dictPlist[globalPlist_key]["Flat"] = []
						print ("TestContentTool -INFO-  |	 GP: " + globalPlist_key)
						list_globalPlist_key.append (globalPlist_key)
						tempDict = {globalPlist_key:[]}
						if "Flatten" in line:
							dictPlist[globalPlist_key]["Flat"] = 'YES'
						else:
							dictPlist[globalPlist_key]["Flat"] = 'NO'
							plist_preBurst = tempList[3]
							plist_preBurst=re.sub('\[', '', plist_preBurst) 
							plist_preBurst=re.sub('\]', '', plist_preBurst) 
							plist_postBurst = tempList[5]
							plist_postBurst=re.sub('\[', '', plist_postBurst) 
							plist_postBurst=re.sub('\]', '', plist_postBurst)
							dictPlist[globalPlist_key]['PostBurst'].append(plist_postBurst)
							dictPlist[globalPlist_key]['PreBurst'].append(plist_preBurst)
					if (re.match('Pat', line.strip())):
						pat_regex = re.findall('[0-9]+', line)
						print ("TestContentTool -INFO-  |	TID:" + pat_regex[1])
						dictPlist[globalPlist_key]["pats"].append(pat_regex[1])
						cnt_max_size += 1
					if (re.match("PList", line.strip())):
						dictPlist[globalPlist_key]["PList"].append(line.split()[1].replace(';',''))
								
			print("TestContentTool -INFO-  |	  Plist data migrated to Setup File")
			for plist in dictPlist.keys():
				print("TestContentTool -INFO-  |	GlobalP: " + plist)
				for PList in dictPlist[plist]["PList"]:
					print("TestContentTool -INFO-  |	PL: " +PList)
					for pattern in dictPlist[plist]["pats"]:
						print("TestContentTool -INFO-  |	TID: " + pattern)
			print ("TestContentTool -INFO-  |	 ***************************")
			
			pcarFromPlist = WritePcarFromPlist (dictConfig, dictPlist)
		elif ((setuppath.get() != '') and (plistpath.get() == '')):
			print ("TestContentTool -INFO-  |	 Generating .pcar from setup File: "+ setuppath.get())
			xmlTree = ET.parse(setuppath.get()).getroot()
	
			setupName = xmlTree.attrib ['name']
			dictConfig['setup'] = setupName
			for module in xmlTree:
				if module.tag == "module": 
					moduleName = module.attrib['name']
				dictSetup = {}
				dictSetup["intent"] = []
				for globalplist_or_intent in module:
					if globalplist_or_intent.tag == "global_plist":
						globalPlistName = globalplist_or_intent.attrib["name"]
						dictSetup[globalPlistName] = {}
						dictSetup[globalPlistName]["preburst"] = ''
						dictSetup[globalPlistName]["postburst"] = ''
						dictSetup[globalPlistName]["preburstplist"] = ''
						dictSetup[globalPlistName]["postburstplist"] = ''
						dictSetup[globalPlistName]["PList"] = []
						dictSetup[globalPlistName]["Pats"] = []
						for pat_plist in globalplist_or_intent:
							if pat_plist.tag == "PList":
								dictSetup[globalPlistName]["PList"].append(pat_plist.attrib['name'])
							if pat_plist.tag == "pat":
								dictSetup[globalPlistName]["Pats"].append(pat_plist.attrib['name'])
								dictPat[pat_plist.attrib['name']] = ""
							if pat_plist.tag == "preburstplist":
								dictSetup[globalPlistName]["preburstplist"] = pat_plist.attrib['name']
								print(dictSetup[globalPlistName]["preburstplist"])
							if pat_plist.tag == "postburstplist":
								dictSetup[globalPlistName]["postburstplist"] = pat_plist.attrib['name']	
							print ("TestContentTool -INFO-  | element: " + pat_plist.attrib['name'])
					elif globalplist_or_intent.tag == "intent":
						intentName = globalplist_or_intent.attrib["name"]
						for pat_plist in globalplist_or_intent:
							if pat_plist.tag == "pat":
								print ("TestContentTool -INFO-  | INTENT TO ADD")
			pcar = WritePcarFromSetup (dictConfig, dictSetup, dictPat)
		elif ((plistpath.get() != '') and (setuppath.get() != '')):
			print ("TestContentTool -INFO-  |	 Generating .pcar. Setup-up: "+ setuppath.get() + " Reference TST:"+ plistpath.get())
			xmlTree = ET.parse(setuppath.get()).getroot()
			setupName = xmlTree.attrib ['name']
			dictConfig['setup'] = setupName
			for module in xmlTree:
				if module.tag == "module": 
					moduleName = module.attrib['name']
				dictSetup = {}
				dictSetup["intent"] = []
				for globalplist_or_intent in module:
					if globalplist_or_intent.tag == "global_plist":
						globalPlistName = globalplist_or_intent.attrib["name"]
						dictSetup[globalPlistName] = {}
						dictSetup[globalPlistName]["preburst"] = ''
						dictSetup[globalPlistName]["postburst"] = ''
						dictSetup[globalPlistName]["preburstplist"] = ''
						dictSetup[globalPlistName]["postburstplist"] = ''
						dictSetup[globalPlistName]["PList"] = []
						dictSetup[globalPlistName]["Pats"] = []
						for pat_plist in globalplist_or_intent:
							if pat_plist.tag == "PList":
								dictSetup[globalPlistName]["PList"].append(pat_plist.attrib['name'])
							if pat_plist.tag == "pat":
								dictSetup[globalPlistName]["Pats"].append(pat_plist.attrib['name'])
								dictPat[pat_plist.attrib['name']] = ""
							if pat_plist.tag == "preburstplist":
								dictSetup[globalPlistName]["preburstplist"] = pat_plist.attrib['name']
								print(dictSetup[globalPlistName]["preburstplist"])
							if pat_plist.tag == "postburstplist":
								dictSetup[globalPlistName]["postburstplist"] = pat_plist.attrib['name']	
							print ("TestContentTool -INFO-  | element: " + pat_plist.attrib['name'])
					elif globalplist_or_intent.tag == "intent":
						intentName = globalplist_or_intent.attrib["name"]
						for pat_plist in globalplist_or_intent:
							if pat_plist.tag == "pat":
								print ("TestContentTool -INFO-  | INTENT TO ADD")
			#.pcar update
			pcar = WritePcarFromTST (dictConfig, dictSetup, dictPat)
		
		print("TestContentTool -INFO-  |	.pcar file Updated: " + dictConfig["pcar"])
	
		print ("TestContentTool -INFO-  |	Generating plist")
		if (PCARsetup_value.get() == ".pcar file"):
			print ("TestContentTool -INFO-  |	Using .pcar: " + pcar3path.get())
			rtn = RunPlistGen(pcar3path.get(), vcfVmode_value.get(), vcfVectype_value.get(), vcfVrev_value.get())
		else:
			rtn = RunPlistGen(dictConfig["pcar"], vcfVmode_value.get(), vcfVectype_value.get(), vcfVrev_value.get())
			
		print("TestContentTool -INFO-  |	Plist Generation is Complete")
		rtnlist = rtn.split("\n")
	
		for line in rtnlist:
			s = line
			#print ("TestContentTool -INFO-  |	 rtn line" + line)
			if (re.search('Status:  Clean', s)):
				print ("TestContentTool -INFO-  |	Success -> Plist Generated")
				status = 1    
			if (re.search('Status:  Empty', s)):
				print ("TestContentTool -INFO-  |	Success -> Plist Generated")
				status = 1    
			if (re.search('Rundir:', s)):
				rundir = s
		
		if (status == 0):
			print ("TestContentTool -INFO-  |	 Failed to generate plists, please try again")
			print("TestContentTool -INFO-  |	[ERROR] Failed to generate plists, please try again!")
			print("TestContentTool -INFO-  |	  PCAR Complete!!")		
	
def get_tupleList (TID_List):
	status = 0
	rtn = ""
	tupleList = []
	for TID in TID_List:
		print ("TestContentTool -INFO-  |	TID:" + TID)
		tuple, rtn = GetTuple(TID)
		print ("TestContentTool -INFO-  |	Tuple:" + str(tuple))
		tupleList.append(tuple)
	return tupleList

def GetTidVault (testname):
	rtn = ""
	tid = None
    
	try:
		print ("TestContentTool -INFO-  |	Getting TID: " + '-proj: '+ product + ' -parent_prod: ' + parent_value.get() + '  |  Testname: ' + testname )
		#if (product !=  parent_value.get()):
		rtn = subprocess.check_output(['vaultmgr', '-proj', product, '-q','owner = ', mod_value.get()[1:], 'parent_product = ', parent_value.get(), "path = %" + product + "%" + testname + "/" + testname + ".spf", '--', '-pr', 'test_id', '--'])
		#elif
			#rtn = subprocess.check_output(['vaultmgr', '-proj', product, '-q','owner = ', mod_value.get()[1:], "path = %" + product + "%" + testname + "/" + testname + ".spf", '--', '-pr', 'test_id', '--'])
		
		rtn = rtn.decode('utf-8')
		print ("TestContentTool -INFO-  |	 vaultmgr" + rtn)
		regEx = re.search(r'test_id\s+:\s+(\S+)', rtn)
		if regEx != None:
			tid = regEx.group(1)
	except subprocess.CalledProcessError as e:
		rtn = "[ERROR]" + e.output
		tid = None
	return tid, rtn

def GetTuple (tid):
	rtn = ""
	tuple = ""
	
	try:
		o_trace_find = subprocess.Popen(['finder.py', '-tid', tid, '-bottom', '1'],stdout = subprocess.PIPE)
		s_trace_find_out, s_trace_find_error = o_trace_find.communicate('encode'.encode)
		s_trace_find_out = s_trace_find_out.decode()
		if re.search('([dg][\d]{7}V)', s_trace_find_out):
			status = 1
			tuple = s_trace_find_out
			pattern = tuple.split('/')[-1]
			pobj = pattern.split(':')[0]
			regEx = re.compile(r'[dg]([\d]{7})')
			tuple = regEx.search(tuple).group()
		else:
			tuple = None
		
		if (tuple != None):
			print ("TestContentTool -INFO-  |	Tuple found: " + tuple)
			print ("TestContentTool -INFO-  |	Source Path: " + s_trace_find_out)
			status = 0
			rtn = str(s_trace_find_out)
	except subprocess.CalledProcessError as e:
		tuple = None
		rtn = "[ERROR]" + e.output
		status = 0
	return tuple, rtn

def UpdateIntent (tid, intent):
	rtn = ""
	try:
		rtn = subprocess.check_output(['vaultmgr', '-proj', product, '-q', "test_id = ", tid, "-q-", '-pr', 'all', '-pr-', '-r', 'intent', intent, '-r-'])
		rtn = rtn.decode('utf-8')
	except subprocess.CalledProcessError as e:
		rtn = "[ERROR]" + e.output
		tid = None
	return rtn
	
def GetIntent (tid):
	intent = ''	
	print ("TestContentTool -INFO-  |	 GettingIntent..." + ' tid: ' + tid)		
	os.system("vaultmgr -proj " + product + " -q test_id = " + tid + " -- -pr intent -- > vault_query_intent.txt")
	intent = get_intent_file('vault_query_intent.txt')
	intent = (intent.replace('\n',''))	
	intent = (intent.replace('intent :',''))
	return intent

def GetSpfName (tid):
	spf_name = ''
	path_list = []
	print ("TestContentTool -INFO-  |	 Getting SPF Name for TID: " + tid)		
	os.system("vaultmgr -proj " + product + " -q test_id = " + tid + " -- -pr path -- > vault_query_path.txt")
	path_name = ((get_path_file('vault_query_path.txt')).replace('\n','')).replace('path :','')
	path_list = (os.path.splitext(path_name)[0]).split("/")
	spf_name = path_list.pop()
	print ("TestContentTool -INFO-  |	 SPF Name:" + spf_name + "\n")
	return spf_name	
	
def RunVaultCheckout (tid, vaultarea):
	status = 0
	rtn = ""
    
	try:
		if (product ==  parent_value.get()):
			rtn = subprocess.check_output(['vaultmgr', '-proj', product, '-q', "test_id=" + tid, '--', '-co_source', vaultarea, '-m', "\"test\""])
		else: 
			rtn = subprocess.check_output(['vaultmgr', '-proj', parent_value.get(), '-q', "test_id=" + tid, '--', '-co_source', vaultarea, '-m', "\"test\""])
		rtn = rtn.decode('utf-8')
		status = 1
	except:
		print("CheckOut failed")

def RunVaultCheckin (tid, vaultarea):
	status = 0
	rtn = ""   
	ciarea = os.path.join(vaultarea, tid)
	try:
		rtn = subprocess.check_output(['vaultmgr', '-proj', product, '-q', "test_id="+tid, '--', '-ci_source', ciarea, '-m', "\"test\""])
		status = 1
	except subprocess.CalledProcessError as e:
		rtn = "[ERROR]" + e.output
		status = 0   
 #   print ("TestContentTool -INFO-  |	  RunVaultCheckin TID:" + str(tid) + " status:" + str(status))
	return status, rtn

def WriteDepositFile_Vault (turninFile, spf2deposit, testtype, owner, attribute, tag):
	print ('TestContentTool -INFO-  |	Writing Deposit Vault ...')
	now = datetime.now()
	status = 0
	tid = ''
	
	with open(turninFile, 'w') as f:
		f.write('# HEADER CREATION NOTE: the twg.testtype, twg.attributes, twg.tag and owner fields require a value. Other fields can be left blank'+ '\n')
		f.write('# simulation list file generated '+ str(now) + '\n')
		f.write('## twg.testtype'       + ' ' + testtype + '\n')
		f.write('## twg.owner'          + ' ' + owner + '\n')
		f.write('## twg.parent_product' + ' ' + parent_value.get() + '\n')
		f.write('## twg.attributes'     + ' ' + attribute + '\n')
		f.write('## twg.tag'            + ' ' + tag + '\n')
		f.write('## twg.parent_testid\n')
		f.write('## twg.directives\n')
		f.write('## twg.notes\n\n')
		f.write('################################################\n')
		f.write('# PLACE YOUR TESTLIST BELOW THIS LINE\n')
		f.write('################################################\n')
	
		depositpath = os.path.join(os.getcwd()+('/patarea'), spf2deposit.replace('.spf',''))
		spfvaultpath = os.path.join(spfpath.get(),spf2deposit)
		print ("TestContentTool -INFO-  |	Deposit File path:" + depositpath + "  |  SPF path:" + spfvaultpath)
		if not (os.path.exists(depositpath)):
			os.mkdir(depositpath)
			shutil.copy(spfvaultpath, depositpath)   
			f.write(depositpath +'/' + spf2deposit + '\n')
			status = status + 1
		f.close()
	print ("TestContentTool -INFO-  |	WriteDepositFile turninFile:" + str(turninFile) + " Total:" + str(status))
	return status

def RunVaultDeposit (turninFile):
	status = 0
	rtn = ""
    
	try:
		rtn = subprocess.check_output(['vaultdeposit', '-proj', product, '-turnin', turninFile, '-skip_existing'])
		rtn = rtn.decode('utf-8')
		status = 1
	except:
		status = 0
	return status, rtn

def RunItrace (tidFile, dirtag, lineitem):
	status = 0
	passcount = 0
	failcount = 0
	rtn = ""
	
	try:
		print ("TestContentTool -INFO-  |	Running Itrace - Installing... ")
		rtn = subprocess.check_output(['iTrace_manager', '-tid_file', tidFile, '-install', '-tag', dirtag, '-lineitem', lineitem])
		print ("TestContentTool -INFO-  |	Running Itrace - Launching... ")
		rtn = subprocess.check_output(['iTrace_manager', '-tid_file', tidFile, '-launch',  '-tag', dirtag, '-lineitem', lineitem])
		rtn = rtn.decode('utf-8')
		status = 1
	except subprocess.CalledProcessError as e:
		rtn = e.output
		status = 0
	
	if status == 1:
		isItraceInProgress = 1
		while (isItraceInProgress):
			try:
				rtn = subprocess.check_output(['iTrace_status', '-tag', dirtag, '-gettids'])
				rtn = rtn.decode('utf-8')
			except subprocess.CalledProcessError:
				rtn = e.output
				isItraceInProgress = 0
				status = 0
				break
			
			regEx = re.search(r'SUMMARY', rtn)    
			if regEx != None:
				total = 0
				passcount = 0
				failcount = 0
				regEx = re.search(r'ALL\[(\d+)\]', rtn)
				if regEx != None:
					total = int(regEx.group(1))
				regEx = re.search(r'PASS\[(\d+)\]', rtn)
				if regEx != None:
					passcount = int(regEx.group(1))
				regEx = re.search(r'FAIL\[(\d+)\]', rtn)
				if regEx != None:
					failcount = int(regEx.group(1))
				if (total == (passcount + failcount)) and ( total != 0):
					isItraceInProgress = 0
					rtn = "iTrace_status: total=" + str(total) + " pass=" + str(passcount) + " fail=" + str(failcount) + "\n"
					#rtn = rtn.decode('utf-8')
					status = 1
				print ("TestContentTool -INFO-  |	Running Itrace: totalcount: " + str(total) + " passcount: " + str(passcount) + " failcount: " + str(failcount))
			time.sleep(50)

	return status, total

def WriteVcfFile (vcfFile, dictPattern):
	status = 0
	rtn = ""
	tupleList = []
	for pattern in dictPattern.keys():
		if dictPattern[pattern]['isItrace'] == 1 and dictPattern[pattern]['tid'] != None:
			tuple, rtn = GetTuple(dictPattern[pattern]['tid'])
			if tuple != None:
				dictPattern[pattern]['tuple'] = tuple
				print ("TestContentTool -INFO-  |	  WriteVcfFile - new tuple:" + tuple)
			else:
				print("TestContentTool -INFO-  |	[ERROR] WriteVcfFile: Failed to get new tuple - " + pattern + "\n" + rtn)
		if dictPattern[pattern]['isVCF'] == 1:
			if dictPattern[pattern]['tid'] != None and dictPattern[pattern]['tuple'] != None:
				tupleList.append(dictPattern[pattern]['tuple'])
			else:
				print ("TestContentTool -INFO-  |	  WriteVcfFile vcfFile:" + " skip pattern: " + pattern + " as tid or tuple is None")
	#pattern in dictPattern.keys()
	
	with open(vcfFile, "w") as f:
		for tuple in tupleList:
			if tuple != None:
				f.write (tuple + '\n')
				status += 1
	f.close()
	
	print ("TestContentTool -INFO-  |	  WriteVcfFile vcfFile:" + str(vcfFile) + " Total:" + str(status))
	return status

def RunVcf (vcfFile, vrev, vectype, mode):
	status = 0
	rtn = ""
	
	try:
		rtn = subprocess.check_output(['vcf', '-list', vcfFile, '-mode', mode, '-vectype', vectype, '-vrev', vrev, '-target', 'central', '-nbclass', 'mem32g'])   
		rtn = rtn.decode('utf-8')
		subprocess.check_output(['ls', '-ltr'])
		status = 1
	except subprocess.CalledProcessError as e:
		rtn = e.output
		status = 0

	return status, rtn

def WriteSetupFromPlist( dictPlist):
	status = 0
	cnt = 0
	pat_string = ""
	module = mod_value.get()
	SetupFile = setuppath.get()
	SetupLine = ""
	
	SetupLine += '<setup name = "SPREE">' + '\n'
	SetupLine += '	<module name = \"' + module + '">' + '\n'
	
	for plistname in dictPlist.keys():
		pat_string = ''
		cnt = 0	
		SetupLine += "		<global_plist name = \"" + plistname + "\">" + "\n"
		if (dictPlist[plistname]["Burst"] == 'YES'):
			if (dictPlist[plistname]["PreBurst"][0] != 'nopre') :
				SetupLine += "			<preburstplist name = \"" + dictPlist[plistname]["PreBurst"][0] + "\"></preburstplist>" + "\n"
			if (dictPlist[plistname]["PostBurst"][0] != 'nopost') :
				SetupLine += "			<postburstplist name = \"" + dictPlist[plistname]["PostBurst"][0] +  "\"></postburstplist>" + "\n"
	
		for PList in dictPlist[plistname]["PList"]:
			SetupLine += "   			<PList name = \"" + PList + "\" />\n"
			
		for pattern in dictPlist[plistname]["spf"]:  	
			SetupLine += "  	 	 	<pat name = \"" + pattern + "\" />\n"
		
		SetupLine += "		</global_plist>\n"
		
	SetupLine += "    </module>" + "\n"
	SetupLine += "</setup>" + "\n"
	
	with open(SetupFile, "w+") as f:
		f.write(SetupLine)
	f.close()
	print ("TestContentTool -INFO-  |	Clone strcuture generated: " + SetupFile)
	return status

def WritePcarFromPlist(dictConfig, dictPlist):
	status = ''
	cnt = 0
	pat_string = ""
	module = dictConfig['module']
	pcarFile = dictConfig['pcar'] 
	pcarLine = ""
	
	pcarLine += '#!/usr/intel/pkgs/python/2.7.5/bin/python' + '\n'
	pcarLine += 'from veplib.pcar3 import PlistFile, Plb, Pats, Tids, QueryTid, pcar3, Amble, Comment, RefPlb, NameFilter' + '\n'
	pcarLine += "level0 = PlistFile(\'" + module + ".plist" + "\')" + '\n'
	
	for plistname in dictPlist.keys():
		pat_string = ''
		cnt = 0	
		if (dictPlist[plistname]["Flat"] == "YES"):
			pcarLine += "level1 = level0.add(Plb(\"" + plistname + "\"" + ", preburst=None, postburst=None" + "))" + "\n"
		else:
			print (dictPlist[plistname]["PreBurst"])
			pcarLine += "level1 = level0.add(Plb(\"" + plistname + "\"" + ", preburstplist=\"" + dictPlist[plistname]["PreBurst"][0] + "\", postburstplist=\"" + dictPlist[plistname]["PostBurst"][0] + "\"" + "))" + "\n"
		for PList in dictPlist[plistname]["PList"]:
			pcarLine += "level2 = level1.add(RefPlb(" + PList +"))\n"
			
		for pattern in dictPlist[plistname]["pats"]:
			if (cnt ==0):
				pat_string +=  pattern
				cnt = 1
			else:	
				pat_string +=  ',' + pattern  	
		pcarLine += "level2 = level1.add(Pats(Tids([" + pat_string + "])))\n"	
		pcarLine += "\n"            
	
	pcarLine += "if __name__ == \'__main__\':" + "\n"
	pcarLine += "    pcar3.process()" + "\n"
	pcarLine += "    print(\"Summary\")" + "\n"
	pcarLine += "    pcar3.report(detail=False)" + "\n"
	pcarLine += "    print(pcar3.gen_plist_preview())" + "\n"
	
	with open(pcarFile, "w+") as f:
		f.write(pcarLine)
	f.close()
	
	return status

def WritePcarFromTST(dictConfig, dictSetup, dictTID):
	status = ''
	cnt = 0
	tmp_List = []
	pat_string = ""
	module = dictConfig['module']
	pcarFile = dictConfig['pcar'] 
	pcarLine = ""
	pcarLine += '#!/usr/intel/pkgs/python/2.7.5/bin/python' + '\n'
	pcarLine += 'from veplib.pcar3 import PlistFile, Plb, Pats, Tids, QueryTid, pcar3, Amble, Comment, RefPlb, NameFilter' + '\n'
	pcarLine += "level0 = PlistFile(\'" + module + ".plist" + "\')" + '\n'
	var_postBst_str = ''
	var_preBst_str = ''
	rtn = 0	
	pat_processed = 0
	TID = None
	pat_list = []	
	total_pat = len(dictTID)
	cnt_SPF_ref = 0
	dictTST = {}
	SPFName = ''

	
	with open(plistpath.get()) as op:
		print ("TestContentTool -INFO-  |	Opening Reference TST plist:" + tapovrpath.get())
		for line in op:
			if (re.match('Pat', line.strip())):
				pat_regex = re.findall('[0-9]+', line)
				TIDtst = pat_regex[1]
				SPFName = re.search("x00_(.*?);",line).group(1)
				dictTST[SPFName] = TIDtst
				cnt_SPF_ref+=1	
				print("TestContentTool -INFO-  |	Parsing Reference Plist: Cnt:{} | Tuple:{} | TID:{} | SPF name:{}".format(cnt_SPF_ref, pat_regex[0], pat_regex[1], re.search("00_(.*?);",line).group(1)))		
		
	for globalPlist_intent in dictSetup:
		if(globalPlist_intent != "intent"):
			pat_string = ''
			cnt = 0	
			try:
				var_postBst_str = str(dictSetup[globalPlist_intent]["postburstplist"].split(" ")[1])
			except:
				var_postBst_str = ''
			try:
				var_preBst_str = str(dictSetup[globalPlist_intent]["preburstplist"].split(" ")[1])
			except:
				var_preBst_str = ''
				
			if ((var_preBst_str == '') and (var_postBst_str == '')):
				pcarLine += "level1 = level0.add(Plb(\"" + globalPlist_intent + "\"" + ", preburst= " + "None, " + "postburst = " + "None"  + "))" + "\n"
			elif ((var_preBst_str != '') and (var_postBst_str == '')):
				pcarLine += "level1 = level0.add(Plb(\"" + globalPlist_intent + "\"" + ", preburstplist=\"" + var_preBst_str + "\", preburst = None, postburst = None))" + "\n"
			elif ((var_preBst_str == '') and (var_postBst_str != '')):
				pcarLine += "level1 = level0.add(Plb(\"" + globalPlist_intent + "\"" + ", postburstplist=\"" + var_postBst_str + "\", preburst = None, postburst = None))" + "\n"
			else: 
				pcarLine += "level1 = level0.add(Plb(\"" + globalPlist_intent + "\"" + ", preburstplist=\"" + var_preBst_str + "\"," + "postburstplist=\"" + var_postBst_str + "\", preburst = None, postburst = None ))" + "\n"
		
			for PList in dictSetup[globalPlist_intent]["PList"]:
				if (PList != ''):
					pcarLine += "level2 = level1.add(RefPlb(\"" + PList +"\"))\n"
			
			for pattern in dictSetup[globalPlist_intent]["Pats"]:
				print ("TestContentTool -INFO-  |	(" + str(pat_processed) + "/" + str(total_pat) + ") Getting TID associated to " + pattern + " ...")
				if pattern in pat_list:
					TID = dictTID[pattern]
				else:	
					pat_list.append(pattern)
					try:
						TID = dictTST[pattern]
					except:
						TID = 'None'
					try:
						dictTID[pattern] = TID
					except: 
						pass
				if (cnt ==0):
					pat_string +=  str(TID)
					cnt = 1
				else:	
					pat_string +=  ', ' + str(TID)  
				pat_processed += 1
			pcarLine += "level2 = level1.add(Pats(Tids([" + pat_string + "])))\n"
	
	pcarLine += "\n"            
	pcarLine += "if __name__ == \'__main__\':" + "\n"
	pcarLine += "    pcar3.process()" + "\n"
	pcarLine += "    print(\"Summary\")" + "\n"
	pcarLine += "    pcar3.report(detail=False)" + "\n"
	pcarLine += "    print(pcar3.gen_plist_preview())" + "\n"
	
	with open(pcarFile, "w+") as f:
		f.write(pcarLine)
	f.close()
	
	return status
	
def WritePcarFromSetup(dictConfig, dictSetup, dictTID):
	status = ''
	cnt = 0
	tmp_List = []
	pat_string = ""
	module = dictConfig['module']
	pcarFile = dictConfig['pcar'] 
	pcarLine = ""
	pcarLine += '#!/usr/intel/pkgs/python/2.7.5/bin/python' + '\n'
	pcarLine += 'from veplib.pcar3 import PlistFile, Plb, Pats, Tids, QueryTid, pcar3, Amble, Comment, RefPlb, NameFilter' + '\n'
	pcarLine += "level0 = PlistFile(\'" + module + ".plist" + "\')" + '\n'
	var_postBst_str = ''
	var_preBst_str = ''
	rtn = 0	
	pat_processed = 0
	TID = None
	pat_list = []
	
	total_pat = len(dictTID)

	for globalPlist_intent in dictSetup:
		if(globalPlist_intent != "intent"):
			pat_string = ''
			cnt = 0	
			try:
				var_postBst_str = str(dictSetup[globalPlist_intent]["postburstplist"].split(" ")[1])
			except:
				var_postBst_str = ''
			try:
				var_preBst_str = str(dictSetup[globalPlist_intent]["preburstplist"].split(" ")[1])
			except:
				var_preBst_str = ''
				
			if ((var_preBst_str == '') and (var_postBst_str == '')):
				pcarLine += "level1 = level0.add(Plb(\"" + globalPlist_intent + "\"" + ", preburst= " + "None, " + "postburst = " + "None"  + "))" + "\n"
			elif ((var_preBst_str != '') and (var_postBst_str == '')):
				pcarLine += "level1 = level0.add(Plb(\"" + globalPlist_intent + "\"" + ", preburstplist=\"" + var_preBst_str + "\", preburst = None, postburst = None))" + "\n"
			elif ((var_preBst_str == '') and (var_postBst_str != '')):
				pcarLine += "level1 = level0.add(Plb(\"" + globalPlist_intent + "\"" + ", postburstplist=\"" + var_postBst_str + "\", preburst = None, postburst = None))" + "\n"
			else: 
				pcarLine += "level1 = level0.add(Plb(\"" + globalPlist_intent + "\"" + ", preburstplist=\"" + var_preBst_str + "\"," + "postburstplist=\"" + var_postBst_str + "\", preburst = None, postburst = None ))" + "\n"
		
			for PList in dictSetup[globalPlist_intent]["PList"]:
				if (PList != ''):
					pcarLine += "level2 = level1.add(RefPlb(\"" + PList +"\"))\n"
			
			for pattern in dictSetup[globalPlist_intent]["Pats"]:
				print ("TestContentTool -INFO-  |	(" + str(pat_processed) + "/" + str(total_pat) + ") Getting TID associated to " + pattern + " ...")
				if pattern in pat_list:
					TID = dictTID[pattern]
				else:	
					pat_list.append(pattern)
					TID, rtn = GetTidVault(pattern)
					dictTID[pattern] = TID
				if (cnt ==0):
					pat_string +=  str(TID)
					cnt = 1
				else:	
					pat_string +=  ', ' + str(TID)  
				pat_processed += 1
			pcarLine += "level2 = level1.add(Pats(Tids([" + pat_string + "])))\n"
	
	pcarLine += "\n"            
	pcarLine += "if __name__ == \'__main__\':" + "\n"
	pcarLine += "    pcar3.process()" + "\n"
	pcarLine += "    print(\"Summary\")" + "\n"
	pcarLine += "    pcar3.report(detail=False)" + "\n"
	pcarLine += "    print(pcar3.gen_plist_preview())" + "\n"
	
	with open(pcarFile, "w+") as f:
		f.write(pcarLine)
	f.close()
	
	return status
	
def RunPlistGen(pcar, mode, vectype, vrev):
	searchResult = 0
	s = 'encode'
	print ("TestContentTool -INFO-  |	VREV: " + vrev + " |	VMODE: "  + mode  + " |	VECTYPE: "  + vectype)
	o_trace_find = subprocess.Popen(['vcf', '-mode', mode, '-vectype', vectype, '-vrev', vrev, '-p3', pcar, '-nbclass', 'mem32g'],stdout = subprocess.PIPE) 
	s_trace_find_out, s_trace_find_error = o_trace_find.communicate(s.encode)
	s_trace_find_out = s_trace_find_out.decode()
	return s_trace_find_out

def CleanUpArea(dictConfig):
    if os.path.isdir(dictConfig['patsarea']): 
        shutil.rmtree(dictConfig['patsarea'])
    os.mkdir(dictConfig['patsarea'])
    
    if os.path.isdir(dictConfig['vaultarea']): 
        shutil.rmtree(dictConfig['vaultarea'])
    os.mkdir(dictConfig['vaultarea'])
    
    if os.path.isdir(dictConfig['itracework']): 
        itracestatusPath  = os.path.join(os.path.join(dictConfig['itracework'], "iTrace_status"), dictConfig['dirtag'])
        itracemanagerPath = os.path.join(os.path.join(dictConfig['itracework'], "iTrace_manager"), dictConfig['dirtag'])
        if os.path.isdir(itracestatusPath): 
            shutil.rmtree(itracestatusPath)
        if os.path.isdir(itracemanagerPath): 
            shutil.rmtree(itracemanagerPath)


#############################################################################################

def about_def():
	message = "\n\n"
	message += "===================================================================================================\n"
	message += "===================================   Test Content Tool 1.0   =====================================\n"
	message += "===================================================================================================\n\n"
	message += "Description\n"
	message += "	Automated solution for content extraction, conversion and generation for PDE Content Teams\n\n\n"
	message += "Tool Utilities \n\n"
	message += "	1.Content Check-Out: \n"
	message += "	Content Migration and Reutilization from previous stepping/project \n\n"
	message += "	2.Content Conversion:\n"
	message += "	Content Format Conversion (SPF, eSPF, ITPP)\n\n"
	message += "	3.Content Check-In:\n"
	message += "	Execution of TVPV Flow Steps (vault+iTrace+VCF) and PCAR3 to build production lists\n\n\n"
	message += "Refer to User Guide for all details -> \n\n"
	message += "\n\n"
	print(message)

def support_def():
	print("Support: audie.a.arce.munoz@intel.com")
			
			
# create a menubar
menubar = Menu(root)
root.config(menu=menubar)

# create the Help menu
help_menu = Menu( menubar,tearoff=0)

help_menu.add_command(label='About', command=about_def)
help_menu.add_command(label='Support', command=support_def)

			
# add the Help menu to the menubar
menubar.add_cascade( label="Help", menu=help_menu)


for child in checkinframe.winfo_children():
    child.grid_configure(padx=5, pady=5)
	
for child in checkoutframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

for child in conversionframe.winfo_children():
    child.grid_configure(padx=5, pady=5)
	
root.mainloop()
