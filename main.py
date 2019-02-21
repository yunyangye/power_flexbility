import convert as ct
import subprocess
from shutil import copyfile,rmtree
from os import makedirs,remove

# run model
def runModel(eplus_path,weather_file,eplus_file,output_file):
    df = subprocess.Popen([eplus_path, "-w", weather_file, "-r", "-d", output_file, eplus_file], stdout=subprocess.PIPE)
    output, err = df.communicate()
    print(output.decode('utf-8'))
    if not err is None:
        print(err.decode('utf-8'))

idf_file = './baseline'
weather_file = 'USA_NM_Albuquerque.Intl.Sunport.723650_TMY3'
eplus_path = 'C:/EnergyPlusV8-6-0/energyplus.exe'

# modify the default idf file
line_record = ct.idfUpdate(idf_file)

# run the default idf file
runModel(eplus_path,weather_file + '.epw',idf_file + '.idf','./temp')

# extract the output for default model
f = open('./temp/eplusout.csv','r')
lines=f.readlines()
f.close()

indx_T = []
title = 'Date/Time'
data_required = ['Zone Mean Air Temperature [C](TimeStep)',
                 'Zone Thermostat Heating Setpoint Temperature [C](TimeStep)',
                 'Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)',
                 'Whole Building:Facility Total Electric Demand Power [W](TimeStep)']

for ind,x in enumerate(lines[0].split(',')):
    for data in data_required:
        if data in x:
            indx_T.append(ind)
            title += ','
            title += x.replace('\n','')
title += '\n'

data = []
for x in lines[1:]:
    if '08/01' in x.split(',')[0]:
        temp = x.split(',')[0]
        for i in indx_T:
            temp += ','
            temp += x.split(',')[i].replace('\n','')
        temp += '\n'
        data.append(temp)

makedirs('./result')
f = open('./result/0.0_0.0.csv','wb')
f.writelines(title)
for i in range(len(data)):
    f.writelines(data[i])
f.close()

# copy baseline.idf into folder
makedirs('./model')
copyfile('./'+idf_file+'.idf','./model/0.0_0.0.idf')
rmtree('./temp')

# generate new models
# 0.5 hour one time
for m in range(12,36):    
    # modify schedules+1.11 C
    f = open('./'+idf_file+'.idf','r')
    lines=f.readlines()
    f.close()
    
    ind_num = []
    for y in line_record:
        for ind,line in enumerate(lines):
            if y == line:
                ind_num.append(ind)
    pre_idex = 0
    new_lines = []
    for i in ind_num:
        for k in range(pre_idex,i):
            new_lines.append(lines[k])
        for j in range(len(lines)):
            if ';' not in lines[i+j]:
                new_lines.append(lines[i+j])
            else:
                temperature = float(lines[i+j].split(',')[1].split(';')[0]) + 1.11
                new_lines.append(lines[i+j].replace('24:00',str(int(m/2))+':'+str(m%2*3)+str(0)).replace(';',','))
                new_lines.append('    Until: 24:00,'+str(temperature)+';                   !- Field '+str(j-1)+'\n')
                pre_idex = i + j + 1
                break
        
    for i in range(pre_idex,len(lines)):
        new_lines.append(lines[i])
        
    f = open('./temp.idf','w')
    for i in range(len(new_lines)):
        f.writelines(new_lines[i])
    f.close()

    # run the default idf file
    runModel(eplus_path,weather_file + '.epw','./temp.idf','./temp')
        
    # extract the output for default model
    f = open('./temp/eplusout.csv','r')
    lines=f.readlines()
    f.close()

    data = []
    for x in lines[1:]:
        if '08/01' in x.split(',')[0]:
            temp = x.split(',')[0]
            for i in indx_T:
                temp += ','
                temp += x.split(',')[i].replace('\n','')
            temp += '\n'
            data.append(temp)
    
    f = open('./result/'+'%.1f' % (m/2.0)+'_1.11.csv','wb')
    f.writelines(title)
    for i in range(len(data)):
        f.writelines(data[i])
    f.close()
    
    # copy baseline.idf into folder
    copyfile('./temp.idf','./model/'+'%.1f' % (m/2.0)+'_1.11.idf')
    rmtree('./temp')
    remove('./temp.idf')

    # modify schedules-1.11 C
    f = open('./'+idf_file+'.idf','r')
    lines=f.readlines()
    f.close()
    
    ind_num = []
    for y in line_record:
        for ind,line in enumerate(lines):
            if y == line:
                ind_num.append(ind)
    pre_idex = 0
    new_lines = []
    for i in ind_num:
        for k in range(pre_idex,i):
            new_lines.append(lines[k])
        for j in range(len(lines)):
            if ';' not in lines[i+j]:
                new_lines.append(lines[i+j])
            else:
                temperature = float(lines[i+j].split(',')[1].split(';')[0]) - 1.11
                new_lines.append(lines[i+j].replace('24:00',str(int(m/2))+':'+str(m%2*3)+str(0)).replace(';',','))
                new_lines.append('    Until: 24:00,'+str(temperature)+';                   !- Field '+str(j-1)+'\n')
                pre_idex = i + j + 1
                break
        
    for i in range(pre_idex,len(lines)):
        new_lines.append(lines[i])
        
    f = open('./temp.idf','w')
    for i in range(len(new_lines)):
        f.writelines(new_lines[i])
    f.close()

    # run the default idf file
    runModel(eplus_path,weather_file + '.epw','./temp.idf','./temp')
        
    # extract the output for default model
    f = open('./temp/eplusout.csv','r')
    lines=f.readlines()
    f.close()

    data = []
    for x in lines[1:]:
        if '08/01' in x.split(',')[0]:
            temp = x.split(',')[0]
            for i in indx_T:
                temp += ','
                temp += x.split(',')[i].replace('\n','')
            temp += '\n'
            data.append(temp)
    
    f = open('./result/'+'%.1f' % (m/2.0)+'_-1.11.csv','wb')
    f.writelines(title)
    for i in range(len(data)):
        f.writelines(data[i])
    f.close()
    
    # copy baseline.idf into folder
    copyfile('./temp.idf','./model/'+'%.1f' % (m/2.0)+'_-1.11.idf')
    rmtree('./temp')
    remove('./temp.idf')
