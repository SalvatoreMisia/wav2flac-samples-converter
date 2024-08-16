# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 14:39:54 2024

@author: salva
"""

####~ Modules recall    ~####
import os
from os.path import isdir, isfile, join, basename, splitext, dirname, exists
from pydub import AudioSegment
from tqdm import tqdm
import shutil
from unidecode import unidecode

####~ Requirements      ~####
if shutil.which('ffmpeg') == None:
    raise Exception('You must have ffmpeg installed! Otherwise flac files will be corrupted!')

####~ Functions         ~####
def pthdirnav(path_start):
    list_pth_el = os.listdir(path_start)
    full_paths = [join(path_start, i) for i in list_pth_el]
    list_sub_pths, list_files, list_machidd = list(), list(), list()
    for curr_path in full_paths:
        if isdir(curr_path):
            if basename(curr_path).lower() == '__macosx': # Path full of hidden files, not meaningful for windows. If you have macOS it will be rebuilt
                try:
                    shutil.rmtree(curr_path)
                except:
                    list_machidd.append(curr_path)
                    list_sub_pths.append(curr_path)
            else:
                list_sub_pths.append(curr_path)
        else:
            list_files.append(curr_path)
    return list_sub_pths, list_files, list_machidd

def wav2flac(wav_path):
    flac_path = splitext(wav_path)[0] + '.flac'
    wav_sampl = AudioSegment.from_wav(wav_path)
    wav_sampl.export(flac_path, format = "flac")
    
def gaudio2flac(gaudio_path):
    flac_path = splitext(gaudio_path)[0] + '.flac'
    gad_sampl = AudioSegment.from_file(gaudio_path)
    gad_sampl.export(flac_path, format = "flac")
    
def fileconv(curr_path, remExsWav=True, moveMIDI=False, orig_path=os.getcwd()):
    success = False
    if isfile(curr_path):
        file_ext = splitext(curr_path)[1].lower()
        file_bsn = basename(curr_path)
        
        comm_path_prfx = os.path.commonpath([curr_path, orig_path])
        rltv_path_sffx = os.path.relpath(dirname(curr_path), comm_path_prfx)
        
        midi_fldnm = 'MIDI'
        oldsmpl_fldnm = '_old_wav_check'
        
        if file_bsn[:2] == '._' or file_bsn == '.DS_Store': # Stupid fake, hidden, and not necessary files (macos...)
            os.remove(curr_path)
            
        elif rltv_path_sffx[:len(oldsmpl_fldnm)] == oldsmpl_fldnm:
            success = True # The process is skipped because the current file is in the Old Wav Path (no conversion needed)
            
        else:
            if file_ext == '.wav' or file_ext == '.aif' or file_ext == '.aiff':
                if file_ext == '.wav':
                    wav2flac(curr_path)
                else:
                    gaudio2flac(curr_path)
                    
                if remExsWav:
                    os.remove(curr_path)
                else:
                    if not(rltv_path_sffx[:len(oldsmpl_fldnm)] == oldsmpl_fldnm): # Continue only if the file is not yet in Old Wav Folder   
                        new_move_path = join(comm_path_prfx, oldsmpl_fldnm, rltv_path_sffx)
                        
                        if not(exists(new_move_path)):
                            os.makedirs(new_move_path) # To create nested directories
                            
                        new_move_pth_fl = join(new_move_path, file_bsn)
                        shutil.move(curr_path, new_move_pth_fl)
                    
                success = True
                
            elif file_ext == '.asd' or file_ext == '.reapeaks': # Analysis files of: Ableton, Reaper
                os.remove(curr_path)
                
            elif file_ext == '.mid' and moveMIDI: # Move midi files to new MIDI folder, inside origin_scan_path
                if not(rltv_path_sffx[:len(midi_fldnm)] == midi_fldnm): # Continue only if the file is not yet in MIDI folder    
                    new_move_path = join(comm_path_prfx, midi_fldnm, rltv_path_sffx)
                    
                    if not(exists(new_move_path)):
                        os.makedirs(new_move_path) # To create nested directories
                        
                    new_move_pth_fl = join(new_move_path, file_bsn)
                    shutil.move(curr_path, new_move_pth_fl)
                
    return success
    
####~ Core              ~####
scan_path = [input(f'Samples folder ([{os.getcwd()}]): ') or os.getcwd()]
origin_scan_path = scan_path.copy()
all_paths = scan_path.copy()

rem_usr_in = input('Do you want to remove pre-existing wav files? (y/[n]): ') or 'n'
if rem_usr_in == 'y':
    rem_wav = True
elif rem_usr_in == 'n':
    rem_wav = False
    print("A new folder (_old_wav_check) will be created and " \
          "all the pre-existing samples will be moved there!")
else:
    raise Exception('Just "y" or "n", fucking asshole!')
    
move_midi_in = input('Do you want to move midi file in a separate MIDI folder? ([y]/n): ') or 'y'
if move_midi_in == 'y':
    move_mid = True
    print("A new folder (MIDI) will be created in: [" \
          f"{origin_scan_path[0]}] " \
          "and all midi files will be moved there!")
elif move_midi_in == 'n':
    move_mid = False
else:
    raise Exception('Just "y" or "n", fucking asshole!')
    
files_conv, fold_hidd_nr = list(), list()
while len(scan_path) >= 1:
    temp_sub_dirs, temp_files, temp_hidd = pthdirnav(scan_path[0])
    
    scan_path += temp_sub_dirs
    all_paths += temp_sub_dirs
    files_conv += temp_files
    fold_hidd_nr += temp_hidd
    
    scan_path.pop(0)
    
files_succ_conv = 0
files_err = list()
for idx in tqdm(range(len(files_conv))):
    curr_fl_pth = files_conv[idx]
    try:
        succ = fileconv(curr_fl_pth, remExsWav=rem_wav, moveMIDI=move_mid, orig_path=origin_scan_path[0])
        if succ:
            files_succ_conv += 1
    except:
        # print('Error with sample: '+curr_fl_pth)
        files_err.append(curr_fl_pth)

some_fld_empty = True
remvd_flds = list()
while some_fld_empty:
    some_fld_empty = False
    for curr_fold in all_paths:
        if exists(curr_fold) and (len(os.listdir(curr_fold)) == 0):
            try:
                os.rmdir(curr_fold)
                remvd_flds.append(curr_fold)
                some_fld_empty = True
            except:
                fold_hidd_nr.append(curr_fold)

if len(remvd_flds) > 0:
    print(f"{len(remvd_flds)} folders were empty -> deleted! (check deleted_folders.txt for info)")
    
del_report_filename = join(origin_scan_path[0],'deleted_folders.txt')
if exists(del_report_filename):
    os.remove(del_report_filename)

if len(remvd_flds) > 0:
    with open(del_report_filename, 'w') as d:
        d.write('The following folders were deleted because empty: \n')
        for line in remvd_flds:
            d.write(f"{unidecode(line)}\n")
    d.close()

err_report_filename = join(origin_scan_path[0],'wav_errors.txt')
if exists(err_report_filename):
    os.remove(err_report_filename)
    
if len(files_err) > 0 or len(fold_hidd_nr) > 0:
    with open(err_report_filename, 'w') as f:
        if len(files_err) > 0:
            f.write('The following files were not converted (please consider renaming): \n')
            for line in files_err:
                f.write(f"{unidecode(line)}\n")
        if len(fold_hidd_nr) > 0:
            f.write('\nThe following hidden (or empty) folders were not deleted (please check file permission): \n')
            for line in fold_hidd_nr:
                f.write(f"{unidecode(line)}\n")
    f.close()
    
print(f"Succesfully coverted {files_succ_conv} (of {files_succ_conv+len(files_err)}) wav files into flac")

input('Press Enter to exit...')