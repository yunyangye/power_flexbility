import os

####################################
# idf_file: path of idf (e.g. /home/user/eplus/model)
####################################
def idfUpdate(idf_file):
    # read idf file
    f=open(idf_file+'.idf','r')
    lines=f.readlines()
    f.close()
    
    # identify the zones
    sch=[]# get 'ZoneControl:Thermostat,' !- Control 1 Name
    zone=[]# get 'ZoneControl:Thermostat,' !- Zone or ZoneList Name
    for i in range(len(lines)):
        if lines[i].find('ZoneControl:Thermostat,')!=-1:
            index=i+1
            num=0
            while lines[index].find(';')==-1:
                index=index+1
                num=num+1
            if num>5:
                print "complicated control detected"+lines[i+5].split(' ')[0]
            else:
                sch.append(lines[i+5].split(';')[0].replace('    ',''))
                zone.append(lines[i+2].split(',')[0].replace('    ',''))
    
    # identify the existing schedules
    sch_adjl=[]# !- Control 1 Name
    line_sch=[]# line number of !- Cooling Setpoint Temperature Schedule Name
    sch_al=[]# !- Cooling Setpoint Temperature Schedule Name
    zone_al=[]# !- Zone or ZoneList Name
    for i in range(len(lines)):
        for j in range(len(sch)):
            if lines[i].find(' '+sch[j]+',')!=-1:
                if lines[i-1].find('Dual')!=-1:
                    line_sch.append(i+2)
                    sch_temp=lines[i+2].split(';')[0].replace('    ','')
                    sch_al.append(sch_temp)
                    zone_al.append(zone[j])
                    sch_adjl.append(sch[j])
                
                elif lines[i-1].find('Cooling')!=-1:
                    line_sch.append(i+1)
                    sch_temp=lines[i+1].split(';')[0].replace('    ','')
                    sch_al.append(sch_temp)
                    zone_al.append(zone[j])
                    sch_adjl.append(sch[j])
    
    # divide sch
    # line with 'Actuated' or '! ...' (Use EMS)
    # line without 'Actuated' or '! ...' (Do not use EMS)
    sch_av=[]# !- Cooling Setpoint Temperature Schedule 
    sch_adj=[]# !- Control 1 Name
    zone_av=[]# !- Zone or ZoneList Name
    sch_av_ems=[]# !- Cooling Setpoint Temperature Schedule Name
    sch_adj_ems=[]# !- Control 1 Name
    zone_av_ems=[]# !- Zone or ZoneList Name
    for i in range(len(sch_al)):
        for j in range(len(lines)):
            if lines[j].lower().find(sch_al[i].lower()+',')!=-1 and (lines[j].find('Actuated')!=-1 or lines[j][0]=='!'):
                temp=True
                break
            temp=False
        if temp==False:
            sch_av.append(sch_al[i])
            sch_adj.append(sch_adjl[i])
            zone_av.append(zone_al[i])
        
        if temp==True:
            sch_av_ems.append(sch_al[i])
            sch_adj_ems.append(sch_adjl[i])
            zone_av_ems.append(zone_al[i])
    
    # collect existing cooling setpoint schedules
    sch_record=[]
    for i in range(len(lines)):
        for j in range(len(sch_av)):
            temp=[]
            if lines[i].split(',')[0].replace(' ','')==sch_av[j] and lines[i].split(',')[1].replace(' ','').replace('\n','')=='!-Name':
                for k in range(i+1,len(lines)):
                    temp.append(lines[k])
                    if ';' in lines[k]:
                        break
                sch_record.append(temp)
    
    sch_record_ems=[]
    for i in range(len(lines)):
        for j in range(len(sch_av_ems)):
            temp=[]
            if lines[i].split(',')[0].replace(' ','')==sch_av_ems[j] and lines[i].split(',')[1].replace(' ','').replace('\n','')=='!-Name':
                for k in range(i+1,len(lines)):
                    temp.append(lines[k])
                    if ';' in lines[k]:
                        break
                sch_record_ems.append(temp)
    
    # collect the minimum values of stpt
    default=[]
    for j in range(len(sch_av)):
        for i in range(len(lines)):
            if lines[i].lower().find(' '+sch_av[j].lower()+',')!=-1:
                index=i+1
                while lines[index].find(';')==-1:
                    index=index+1
                stpt=[]
                for k in range(i+1,index+1):
                    if lines[k].find(',')!=-1 and lines[k].find(';')==-1:
                        if len(lines[k].split(','))>2:
                            text=lines[k].split(',')[1].replace(' ','')
                        else:
                            text=lines[k].split(',')[0].replace(' ','').replace('!','')
                    elif lines[k].find(';')!=-1 and lines[k].find(',')==-1:
                        text=lines[k].split(';')[0].replace(' ','').replace('!','').replace(' ','')
                    elif lines[k].find(';')!=-1 and lines[k].find(',')!=-1:
                        text=lines[k].split(',')[1].split(';')[0].replace(' ','')
                        
                    if text.replace(".", "", 1).isdigit():
                        stpt.append(float(text))
                default.append(min(stpt))
                break
    
    # disable the existing schedules
    heat_sch=[]
    sch_type=[]
    control_type=[]
    heat_sch_ems=[]
    sch_type_ems=[]
    control_type_ems=[]
    
    for i in range(len(lines)):
        for j in range(len(sch_adj)):
            if lines[i].find(' '+sch_adj[j]+';')!=-1:
                if lines[i].find('!    ')==-1:
                    lines[i]='!'+lines[i]
                index=i-1
                while lines[index].find('ZoneControl:Thermostat')==-1:
                    if lines[index].find('!    ')==-1:
                        lines[index]='!'+lines[index]
                    index=index-1
                if lines[index].find('ZoneControl:Thermostat')!=-1 and lines[index].find('!')==-1:
                    lines[index]='!'+lines[index]
                control_type.append(lines[i-2])
            
            if lines[i].find(' '+sch_adj[j]+',')!=-1:
                if lines[i].find('!    ')==-1:
                    lines[i-1]='!'+lines[i-1]
                    lines[i]='!'+lines[i]
                index=i+1
                while lines[index].find(';')==-1:
                    if lines[index].find('!    ')==-1:
                        lines[index]='!'+lines[index]
                    index=index+1
                if lines[index].find(';')!=-1 and lines[index].find('!    ')==-1:
                    lines[index]='!'+lines[index]
                if index>i+1:
                    heat_sch.append(lines[i+1].replace('!    ','    '))
                else:
                    heat_sch.append(None)
                sch_type.append(lines[i-1].replace('!',''))	
                
        for j in range(len(sch_adj_ems)):
            if lines[i].find(' '+sch_adj_ems[j]+';')!=-1:
                if lines[i].find('!    ')==-1:
                    lines[i]='!'+lines[i]
                index=i-1
                while lines[index].find('ZoneControl:Thermostat')==-1:
                    if lines[index].find('!    ')==-1:
                        lines[index]='!'+lines[index]
                    index=index-1
                if lines[index].find('ZoneControl:Thermostat')!=-1 and lines[index].find('!')==-1:
                    lines[index]='!'+lines[index]
                control_type_ems.append(lines[i-2])
        
            if lines[i].find(' '+sch_adj_ems[j]+',')!=-1:
                if lines[i].find('!    ')==-1:
                    lines[i-1]='!'+lines[i-1]
                    lines[i]='!'+lines[i]
                index=i+1
                while lines[index].find(';')==-1:
                    if lines[index].find('!    ')==-1:
                        lines[index]='!'+lines[index]
                    index=index+1
                if lines[index].find(';')!=-1 and lines[index].find('!    ')==-1:
                    lines[index]='!'+lines[index]
                if index>i+1:
                    heat_sch_ems.append(lines[i+1].replace('!    ','    '))
                else:
                    heat_sch_ems.append(None)
                sch_type_ems.append(lines[i-1].replace('!',''))
    
    # add new zone control
    line_new=[]
    
    # check whether there are duplicate items
    # w/o EMS
    dup_index=[]
    for i in range(len(sch_av)):
        for j in range(len(sch_av)):
            if i!=j and zone_av[i]==zone_av[j]:
                if len(dup_index)>1:
                    for k in range(len(dup_index)):
                        if dup_index[k]==i:
                            include=True
                            break
                        include=False
                else:
                    include=False
                if not include:
                    dup_index.append(i)
    
    dup_index_ems=[]
    for i in range(len(sch_av_ems)):
        for j in range(len(sch_av_ems)):
            if i!=j and zone_av_ems[i]==zone_av_ems[j]:
                if len(dup_index_ems)>1:
                    for k in range(len(dup_index_ems)):
                        if dup_index_ems[k]==i:
                            include=True
                            break
                        include=False
                else:
                    include=False
                if not include:	
                    dup_index_ems.append(i)
    
    line_record = []
    for i in range(len(sch_av)):
        included=False
        for j in range(len(dup_index)):
            if i == dup_index[j]:
                included=True
                break
            included=False
        if not included:
            line_new.append('Schedule:Compact,'+'\n')
            line_new.append('    '+zone_av[i].replace('\n','')+'_'+sch_av[i].replace('\n','')+',  !- Name'+'\n')
            #line_new.append('    Temperature,             !- Schedule Type Limits Name'+'\n')
            #line_new.append('    Through: 12/31,          !- Field 1'+'\n')
            #line_new.append('    For: AllDays,            !- Field 2'+'\n')
            #line_new.append('    Until: 24:00,'+str(default[i])+';                   !- Field 3'+'\n')
            for x in sch_record[i]:
                line_new.append(x)
            line_new.append('\n')
            line_record.append('    '+zone_av[i].replace('\n','')+'_'+sch_av[i].replace('\n','')+',  !- Name'+'\n')
            
            line_new.append(sch_type[i])
            line_new.append('    '+zone_av[i].replace('\n','')+'_setpoint'+',  !- Name'+'\n')
            if heat_sch[i] is not None:
                line_new.append(heat_sch[i])
            line_new.append('    '+zone_av[i].replace('\n','')+'_'+sch_av[i].replace('\n','')+';                !- Cooling Setpoint Temperature Schedule Name'+'\n')
            line_new.append('\n')
            
            line_new.append('ZoneControl:Thermostat,'+'\n')
            line_new.append('    '+zone_av[i].replace('\n','')+'_Thermostat, !- Name'+'\n')
            line_new.append('    '+zone_av[i].replace('\n','')+', !- Name'+'\n')
            line_new.append(control_type[i].replace('!    ','    '))
            line_new.append('    '+sch_type[i].replace('\n','')+' !- Control 1 Object Type'+'\n')
            line_new.append('    '+zone_av[i].replace('\n','')+'_setpoint'+';  !- Control Name'+'\n')
            line_new.append('\n')
            
    for i in range(len(sch_av_ems)):
        included=False
        for j in range(len(dup_index_ems)):
            if i == dup_index_ems[j]:
                included=True
                break
            included=False
        if not included:
            line_new.append('Schedule:Compact,'+'\n')
            line_new.append('    '+zone_av_ems[i].replace('\n','')+'_'+sch_av_ems[i].replace('\n','')+',  !- Name'+'\n')
            #line_new.append('    Temperature,             !- Schedule Type Limits Name'+'\n')
            #line_new.append('    Through: 12/31,          !- Field 1'+'\n')
            #line_new.append('    For: AllDays,            !- Field 2'+'\n')
            #line_new.append('    Until: 24:00,'+str('26.7')+';                   !- Field 3'+'\n')
            #line_new.append('    Until: 24:00,'+str(default[i])+';                   !- Field 3'+'\n')
            for x in sch_record_ems[i]:
                line_new.append(x)
            line_new.append('\n')
            line_record.append('    '+zone_av_ems[i].replace('\n','')+'_'+sch_av_ems[i].replace('\n','')+',  !- Name'+'\n')
            
            line_new.append(sch_type_ems[i])
            line_new.append('    '+zone_av_ems[i].replace('\n','')+'_setpoint'+',  !- Name'+'\n')
            if heat_sch_ems[i] is not None:
                line_new.append(heat_sch_ems[i])
            line_new.append('    '+zone_av_ems[i].replace('\n','')+'_'+sch_av_ems[i].replace('\n','')+';                !- Cooling Setpoint Temperature Schedule Name'+'\n')
            line_new.append('\n')
            
            line_new.append('ZoneControl:Thermostat,'+'\n')
            line_new.append('    '+zone_av_ems[i].replace('\n','')+'_Thermostat, !- Name'+'\n')
            line_new.append('    '+zone_av_ems[i].replace('\n','')+', !- Name'+'\n')
            line_new.append(control_type_ems[i].replace('!    ','    '))
            line_new.append('    '+sch_type_ems[i].replace('\n','')+' !- Control 1 Object Type'+'\n')
            line_new.append('    '+zone_av_ems[i].replace('\n','')+'_setpoint'+';  !- Control Name'+'\n')
    
    # Output:Variable
    # EnergyManagementSystem:OutputVariable
    # EnergyManagementSystem:ProgramCallingManager
    # EnergyManagementSystem:Program
    # EnergyManagementSystem:GlobalVariable
    f=open('template/out_temp.txt','r')
    lines_output=f.readlines()
    f.close()
    
    # combine the lines, new lines, and output lines together
    for i in range(len(lines)):
        if lines[i].lower().find('simulationcontrol,')!=-1:
            if lines[i+5].lower().find('no')!=-1:
                lines[i+5]=lines[i+5].replace('No','Yes')
                lines[i+5]=lines[i+5].replace('no','Yes')
    
    lines=lines+line_new+lines_output
    
    for i in range(len(lines)):
        if lines[i].lower().find('runperiod,')!=-1:
            lines[i+2]='    8,                       !- Begin Month'+'\n'
            lines[i+3]='    1,                       !- Begin Day of Month'+'\n'
            lines[i+4]='    8,                      !- End Month'+'\n'
            lines[i+5]='    1,                      !- End Day of Month'+'\n'
            lines[i+6]='    Monday,                  !- Day of Week for Start Day'+'\n'
            
    for i in range(len(lines)):
        if lines[i].lower().find('timestep,')!=-1 and lines[i].lower().find('update frequency')==-1:
            if lines[i].lower().find(';')!=-1:
                lines[i]='  Timestep,60;'+'\n'
            else:
                lines[i+1]='  60;'+'\n'
    
    os.rename(idf_file+'.idf', idf_file+'.idf-bak')# change the original idf file into .idf-bak
    
    # generate the new idf file
    f=open(idf_file+'.idf','w')
    for i in range(len(lines)):
        f.writelines(lines[i])
    f.close()
    
    return line_record
