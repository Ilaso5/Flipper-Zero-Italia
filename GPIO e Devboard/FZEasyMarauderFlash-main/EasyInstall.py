#!/bin/python3
import os
import platform
from git import Repo
import glob
import time
import shutil
import serial.tools.list_ports
import requests
import json
import esptool
from colorama import Fore, Back, Style

OPENASCII=Fore.GREEN+'''
#########################################
#    Questo script vi aiuterà 		#
#    ad installare o aggiornare		#
#    il vostro esp32 !!   		#
#########################################
'''+Style.RESET_ALL

print(OPENASCII)
print("Assicurati che il tuo devboard ESP32 o WiFi sia collegato!")
BR=str("115200")

def checkforserialport():
	global serialport
	serialport=''
	vids=['303A','10C4','1A86']
	com_port=None
	ports=list(serial.tools.list_ports.comports())
	for vid in vids:
		for port in ports:
			if vid in port.hwid:
				serialport=port.device
				device=vid
	if serialport=='':
		print(Fore.RED+"Non è stato rilevato alcun dispositivo ESP32."+Style.RESET_ALL)
		print(Fore.RED+"Collegare un devboard WiFi Flipper o un chip ESP32 e riprovare"+Style.RESET_ALL)
		choose_fw()
	if device=='':
		return
	elif device=='303A':
		print(Fore.BLUE+"Molto probabilmente stai usando un Flipper Zero WiFi Devboard o un ESP32-S2"+Style.RESET_ALL)
	elif device=='10C4':
		print(Fore.BLUE+"Molto probabilmente stai usando un ESP32-WROOM, un ESP32-S2-WROVER o un ESP32-S3-WROOM"+Style.RESET_ALL)
	elif device=='1A86':
		print(Fore.MAGENTA+"Molto probabilmente stai usando un chip ESP32 non ufficiale! Il successo non è garantito!"+Style.RESET_ALL)

	return

def checkforextrabins():
	extraesp32binsrepo="https://github.com/UberGuidoZ/Marauder_BINs.git"
	global extraesp32bins
	extraesp32bins=("Extra_ESP32_Bins")
	global scorpbins
	scorpbins=(extraesp32bins+"/Marauder/WROOM")
	if os.path.exists(extraesp32bins):
		print("The extra ESP32 bins folder exists!")
	else:
		print("The extra ESP32 bins folder does not exist!")
		print("That's okay, downloading them now...")
		Repo.clone_from(extraesp32binsrepo, extraesp32bins)
	return

def choose_fw():
	choices='''
//======================================================\\\ 
|| Opzioni:						||
|| 1) Installa Marauder su WiFi Devboard o ESP32-S2	||
|| 2) Salva Impostazioni WiFi di Flipper Blackmagic 	||
|| 3) Installa Flipper Blackmagic			||
|| 4) Installa Marauder su ESP32-WROOM			||
|| 5) Installa Marauder su ESP32-S3			||
|| 6) Aggiorna tutti i file				||
|| 7) Esci						||
\\\======================================================//
'''
	global chip
	print(choices)
	fwchoice=int(input("Inserisci il numero relativo alla tua scelta: "))
	if fwchoice==1:
		print("Hai scelto di installare Marauder su WiFi Devboard o ESP32-S2")
		chip="esp32s2"
		checkforserialport()
		flash_esp32marauder()
	elif fwchoice==2:
		print("Hai scelto di salvare Impostazioni WiFi di Flipper Blackmagic ")
		chip="esp32s2"
		checkforserialport()
		save_flipperbmsettings()
	elif fwchoice==3:
		print("Hai scelto di installare Flipper Blackmagic")
		chip="esp32s2"
		checkforserialport()
		flash_flipperbm()
	elif fwchoice==4:
		print("Hai scelto di installare Marauder su ESP32-WROOM")
		chip="esp32"
		checkforserialport()
		flash_esp32wroom()
	elif fwchoice==5:
		print("Hai scelto di installare Marauder su ESP32-S3")
		chip="esp32s3"
		checkforserialport()
		flash_esp32s3()
	elif fwchoice==6:
		print("Hai scelto di aggiornare tutti i file")
		update_option()
	elif fwchoice==7:
		print("Hai scelto di uscire")
		print("Uscita in corso!")
		exit()
	else:
		print(Fore.RED+"Scelta non valida!"+Style.RESET_ALL)
		exit()
	return

def erase_esp32fw():
	global serialport
	print("Erasing firmware...")
	esptool.main(['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'no_reset', 'erase_region', '0x9000', '0x6000'])
	print("Firmware erased!")
	print("Waiting 5 seconds...")
	time.sleep(5)
	return

def checkforesp32marauder():
	print("Checking for Marauder releases")
	if os.path.exists("ESP32Marauder/releases"):
		print("Great, you have the Marauder releases folder!")
	else:
		print("Marauder releases folder does not exist, but that's okay, downloading them now...")
		os.makedirs('ESP32Marauder/releases')
		marauderapi="https://api.github.com/repos/justcallmekoko/ESP32Marauder/releases/latest"
		response=requests.get(marauderapi)
		jsondata=response.json()
		assetdls=range(0,7)
		for assetdl in assetdls:
			marauderasset=jsondata['assets'][assetdl]['browser_download_url']
			if marauderasset.find('/'):
				filename=(marauderasset.rsplit('/', 1)[1])
			downloadfile=requests.get(marauderasset, allow_redirects=True)
			open('ESP32Marauder/releases/'+filename, 'wb').write(downloadfile.content)
	esp32marauderfwc=('ESP32Marauder/releases/esp32_marauder_v*_flipper.bin')
	if not glob.glob(esp32marauderfwc):
		print("No ESP32 Marauder Flipper firmware exists somehow!")
	global esp32marauderfw
	for esp32marauderfw in glob.glob(esp32marauderfwc):
		if os.path.exists(esp32marauderfw):
			print("ESP32 Marauder firmware exists at", esp32marauderfw)
	return

def checkfors3bin():
	esp32s3fwc=('ESP32Marauder/releases/esp32_marauder_v*_mutliboardS3.bin')
	if not glob.glob(esp32s3fwc):
		print("mutliboards3 bin does not exist!")
	global esp32s3fw
	for esp32s3fw in glob.glob(esp32s3fwc):
		if os.path.exists(esp32s3fw):
			print("ESP32-S3 firmware bin exists at", esp32s3fw)
		else:
			print("Somehow, the mutliboardS3.bin file does not exist!")
	return

def checkforoldhardwarebin():
	espoldhardwarefwc=('ESP32Marauder/releases/esp32_marauder_v*_old_hardware.bin')
	if not glob.glob(espoldhardwarefwc):
		print("old_hardware bin does not exist!")
	global espoldhardwarefw
	for espoldhardwarefw in glob.glob(espoldhardwarefwc):
		if os.path.exists(espoldhardwarefw):
			print("Old Hardware bin exists at", espoldhardwarefw)
		else:
			print("Somehow, the old_hardware.bin file does not exist!")
	return

def prereqcheck():
	print("Checking for prerequisites...")
	checkforextrabins()
	checkforesp32marauder()
	checkfors3bin()
	checkforoldhardwarebin()
	return

def flash_esp32marauder():
	global serialport
	erase_esp32fw()
	print("Flashing ESP32 Marauder Firmware on a WiFi Devboard or ESP32-S2...")
	esptool.main(['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'no_reset', 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', '4MB', '0x1000', extraesp32bins+'/Marauder/bootloader.bin', '0x8000', extraesp32bins+'/Marauder/partitions.bin', '0x10000', esp32marauderfw])
	print(Fore.GREEN+"ESP32-S2 has been flashed with Marauder!"+Style.RESET_ALL)
	return

def flash_esp32wroom():
	global serialport
	print("Flashing ESP32 Marauder Firmware onto ESP32-WROOM...")
	erase_esp32fw()
	esptool.main(['-p', serialport, '-b', BR, '--before', 'default_reset', '--after', 'hard_reset', '-c', chip, 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', '2MB', '0x8000', scorpbins+'/partitions.bin', '0x1000', scorpbins+'/bootloader.bin', '0x10000', espoldhardwarefw])
	print(Fore.GREEN+"ESP32-WROOM has been flashed with Marauder!"+Style.RESET_ALL)
	return

def save_flipperbmsettings():
	global serialport
	print("Saving Flipper Blackmagic WiFi Settings to Extra_ESP32_Bins/Blackmagic/nvs.bin")
	esptool.main(['-p', serialport, '-b', BR, '-c', chip, '-a', 'no_reset', 'read_flash', '0x9000', '0x6000', extraesp32bins+'/Blackmagic/nvs.bin'])
	print(Fore.GREEN+"Flipper Blackmagic Wifi Settings have been saved to ", extraesp32bins+"/Blackmagic/nvs.bin!"+Style.RESET_ALL)
	return

def flash_flipperbm():
	if os.path.exists(extraesp32bins+"/Blackmagic/nvs.bin"):
		print("Flashing Flipper Blackmagic with WiFi Settings restore")
		erase_esp32fw()
		esptool.main(['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'no_reset', 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', '4MB', '0x1000', extraesp32bins+'/Blackmagic/bootloader.bin', '0x8000', extraesp32bins+'/Blackmagic/partition-table.bin', '0x9000', extraesp32bins+'/Blackmagic/nvs.bin', '0x10000', extraesp32bins+'/Blackmagic/blackmagic.bin'])
		print(Fore.GREEN+"Flipper Blackmagic has been flashed with the WiFi Settings restored"+Style.RESET_ALL)
	else:
		print("Flashing Flipper Blackmagic without WiFi Settings restore")
		erase_esp32fw()
		esptool.main(['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'no_reset', 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', '4MB', '0x1000', extraesp32bins+'/Blackmagic/bootloader.bin', '0x8000', extraesp32bins+'/Blackmagic/partition-table.bin', '0x10000', extraesp32bins+'/Blackmagic/blackmagic.bin'])
		print(Fore.GREEN+"Flipper Blackmagic has been flashed without WiFi Settings restored"+Style.RESET_ALL)
	return

def flash_esp32s3():
	global serialport
	erase_esp32fw()
	print("Flashing ESP32 Marauder Firmware onto ESP32-S3...")
	esptool.main(['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'no_reset', 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', '8MB', '0x0', extraesp32bins+'/S3/bootloader.bin', '0x8000', extraesp32bins+'/S3/partitions.bin', '0xE000', extraesp32bins+'/S3/boot_app0.bin', '0x10000', esp32s3fw])
	print(Fore.GREEN+"ESP32-S3 has been flashed with Marauder!"+Style.RESET_ALL)
	return

def update_option():
	print("Checking for and deleting the files before replacing them...")
	if os.path.exists("ESP32Marauder"):
		shutil.rmtree("ESP32Marauder")
	if os.path.exists("Extra_ESP32_Bins"):
		shutil.rmtree("Extra_ESP32_Bins")
	prereqcheck()
	return

prereqcheck()
choose_fw()
