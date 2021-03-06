import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.table import Table
#from astroquery.ned import Ned
from astroquery.ipac.ned import Ned
from astroquery.sdss import SDSS
import multiprocessing as mp
import time
import itertools

#'''
###################################################
###################### NED ########################
###################################################

def nedqueryandcheck_df(name, ra,dec,velo):
    #initial query
    position = SkyCoord(ra = ra, dec = dec, unit=(u.deg, u.deg),frame='icrs')
    output_table = Ned.query_region(position, radius=30*u.arcsec, equinox='J2000')
    def_columns =['wallaby_id','delta_velocity_flag','delta_velocity','No.', 'Object Name','RA', 'DEC', 'Type', 'Velocity',\
                 'Redshift', 'Redshift Flag', 'Magnitude and Filter', 'Separation',\
                 'References', 'Notes', 'Photometry Points', 'Positions',\
                 'Redshift Points', 'Diameter Points', 'Associations']
    #check for empty table and return "null" array with len default array
    if len(output_table) < 1:
        nomatch = -9999.99*np.ones((1,20))
        nomatch = list(nomatch.astype(str))
        nomatch[0][0] = name
        nomatch[0][1] = 0
        out = pd.DataFrame(data=nomatch,columns=def_columns)
    else:
        #perform velocity check
        output_df = Table.to_pandas(output_table)
        output_match = output_df[np.abs(output_df.Velocity - velo)< 150]
        delta_v = output_df.Velocity - velo
        #output_match['wallaby_id'] = 
        if len(output_match) < 1:
            nomatch = -9999.99*np.ones((1,20))
            nomatch = list(nomatch.astype(str))
            nomatch[0][0] = name
            nomatch[0][1] = 1
            #output_match.insert(0, column='wallaby_id', value=name)
            #output_match.insert(1, column='delta_velocity',value=delta_v)
            out = pd.DataFrame(data=nomatch,columns=def_columns)
        else:
            output_match.insert(0,column='wallaby_id',value=name)
            output_match.insert(1, column='delta_velocity',value=delta_v)
            output_match.insert(1, column='delta_velocity_flag', value=2)
            out = output_match

    return out


###The list method seemed to be counterintuitive given that the query region output was in the form
###an astropy Table. Deconstructing and reconstructing it doesn't necessarily make much sense. It
###is marginally faster though.


def listappenddefault(lists,value):
    for li in lists:
            li.append(value)
    return lists

def nedqueryandcheck_list(name, ra,dec,velo):
    #initialize lists
    wallaby_id = [] 
    delta_velocity_flag = [] 
    delta_velocity = [] 
    No = [] 
    ObjectName = [] 
    RA = [] 
    DEC = [] 
    Type = [] 
    Velocity = [] 
    Redshift = [] 
    RedshiftFlag = [] 
    MagnitudeandFilter = [] 
    Separation = [] 
    References = [] 
    Notes = [] 
    PhotometryPoints = [] 
    Positions = [] 
    RedshiftPoints = [] 
    DiameterPoints = [] 
    Associations = []
    
    #initial query
    position = SkyCoord(ra = ra, dec = dec, unit=(u.deg, u.deg),frame='icrs')
    output_table = Ned.query_region(position, radius=30*u.arcsec, equinox='J2000')
    def_columns = [wallaby_id,delta_velocity_flag,delta_velocity,No, ObjectName,RA, DEC,\
                 Type, Velocity,Redshift, RedshiftFlag, MagnitudeandFilter, Separation,\
                 References, Notes, PhotometryPoints, Positions,RedshiftPoints,\
                 DiameterPoints, Associations]
    names_columns = ['wallaby_id','delta_velocity_flag','delta_velocity','No.', 'Object Name','RA', 'DEC', 'Type', 'Velocity',\
                 'Redshift', 'Redshift Flag', 'Magnitude and Filter', 'Separation',\
                 'References', 'Notes', 'Photometry Points', 'Positions',\
                 'Redshift Points', 'Diameter Points', 'Associations']
    #check for empty table and return "null" array with len default array
    if len(output_table) < 1:
        for i,col in enumerate(def_columns):
            if i == 0:
                col.append(name)
            else:
                col.append(-9999.99)
        #print(f'No match for {name}')
        
    else:
        #perform velocity check
        output_df = Table.to_pandas(output_table)
        #print(output_df['Object Name'])
        output_match = output_df[np.abs(output_df.Velocity - velo)< 150]
        delta_v = output_df.Velocity - velo
        #output_match['wallaby_id'] = 
        if len(output_match) < 1:
            #print(f'No match within delV range for {name}')
            for i,col in enumerate(def_columns):
                if i == 0:
                    col.append(name)
                elif i == 1:
                    col.append(1)
                
                else:
                    col.append(-9999.99)
        else:
            #print(f'Match for {name}')
            #print(output_match.loc[output_match.index[0]].to_list())
            for i,col in enumerate(def_columns):
                if i == 0:
                    col.append(name)
                elif i == 1:
                    col.append(2)
                elif i == 2:
                    if len(delta_v) > 1:
                        delta_v = delta_v.dropna().values[0]
                    col.append(delta_v)
                else:

                    col.append(output_match[names_columns[i]].values[0])
                    
    #create output dataframe
    #out = pd.DataFrame(data = def_columns, columns = str(def_columns))

    return list(itertools.chain(*def_columns))


df_columns = ['wallaby_id','delta_velocity_flag','delta_velocity','No.', 'Object Name','RA', 'DEC', 'Type', 'Velocity',\
                 'Redshift', 'Redshift Flag', 'Magnitude and Filter', 'Separation',\
                 'References', 'Notes', 'Photometry Points', 'Positions',\
                 'Redshift Points', 'Diameter Points', 'Associations']
#'''



###################################################
###################### SDSS #######################
###################################################


def sdssqueryandcheck(name, wall_ra, wall_dec, velo):
    wallaby_id = [] 
    delta_velocity_flag = [] 
    delta_velocity = [] 
    objID = [] 
    ra = [] 
    dec = [] 
    objtype = [] 
    modelMag_u = [] 
    modelMag_g = [] 
    modelMag_r = [] 
    modelMag_i = [] 
    modelMag_z = [] 
    modelMagErr_u = [] 
    modelMagErr_g = [] 
    modelMagErr_r = [] 
    modelMagErr_i = [] 
    modelMagErr_z = [] 
    z = [] 
    zErr = []
    def_columns = [wallaby_id, delta_velocity_flag, delta_velocity, objID, ra, dec, objtype,\
                    modelMag_u, modelMag_g, modelMag_r, modelMag_i, modelMag_z, modelMagErr_u,\
                    modelMagErr_g, modelMagErr_r, modelMagErr_i, modelMagErr_z, z, zErr]
    #phot_columns = ['objID', 'ra', 'dec', 'type', 'modelMag_u', 'modelMag_g', 'modelMag_r',\
    #                'modelMag_i', 'modelMag_z', 'modelMagErr_u', 'modelMagErr_g', 'modelMagErr_r',\
    #                'modelMagErr_i', 'modelMagErr_z']
    phot_columns = ['objid', 'ra', 'dec', 'type', 'u', 'g', 'r',\
                    'i', 'z', 'err_u', 'err_g', 'err_r',\
                    'err_i', 'err_z']
    spec_columns = ['z_best', 'zErr']
    names_columns = phot_columns + spec_columns
    total_columns = ['wallaby_id', 'delta_velocity_flag', 'delta_velocity'] + names_columns
    position = SkyCoord(ra = wall_ra, dec = wall_dec, unit=(u.deg, u.deg),frame='icrs')
    #try:
    #    output_table = SDSS.query_region(position,radius=60*u.arcsec,photoobj_fields=phot_columns,spectro=False) #specobj_fields=spec_columns
    #except:
    #    print('No values')
    #    for i,col in enumerate(def_columns):
    #        if i == 0:
    #            col.append(name)
    #        else:
    #            col.append(-9999.99)
    sql_query_string_1 = "select p.objid, p.ra, p.dec, p.u, p.err_u, p.g, p.err_g, p.r, p.err_r, p.i, "
    sql_query_string_2 = "p.err_i, p.z, p.err_z, s.z as z_best, s.zErr from Galaxy p, specobj s,"
    sql_query_string_3 = f"dbo.fgetNearByObjEq({wall_ra}, {wall_dec}, 1) n "
    sql_query_string_4 = "where p.objid=s.bestobjid and p.objid=n.objid and s.bestobjid=n.objid"
    sql_query_string = sql_query_string_1+sql_query_string_2+sql_query_string_3+ sql_query_string_4
    #print(sql_query_string_3)
    try:
        output_table = SDSS.query_sql(sql_query_string)
    except:
        #if len(output_table) < 1:
            #print('No match')
            nomatch = -9999.99*np.ones((1,19))
            nomatch = list(nomatch.astype(str))
            nomatch[0][0] = name
            nomatch[0][1] = 1
            #output_match.insert(0, column='wallaby_id', value=name)
            #output_match.insert(1, column='delta_velocity',value=delta_v)
            out = pd.DataFrame(data=nomatch,columns=total_columns)
        
    else:
        #perform velocity check
        if output_table is None:
            nomatch = -9999.99*np.ones((1,19))
            nomatch = list(nomatch.astype(str))
            nomatch[0][0] = name
            nomatch[0][1] = 1
            #output_match.insert(0, column='wallaby_id', value=name)
            #output_match.insert(1, column='delta_velocity',value=delta_v)
            out = pd.DataFrame(data=nomatch,columns=total_columns)
        #print(output_table['objid'])
        else:
            output_df = Table.to_pandas(output_table)
            print(len(output_df['objid']))
            output_match = output_df#[np.abs(output_df.z*299792.458 - velo)< 150]
            delta_v = output_df.z*299792.458 - velo
            #output_match['wallaby_id'] = 
            '''
            if len(output_match) < 1:
                #print(f'No match within delV range for {name}')
                for i,col in enumerate(def_columns):
                    if i == 0:
                        col.append(name)
                    elif i == 1:
                        col.append(1)
                    
                    else:
                        col.append(-9999.99)
            else:
                #print(f'Match for {name}')
                #print(output_match.loc[output_match.index[0]].to_list())
                for i,col in enumerate(def_columns):
                    if i == 0:
                        col.append(name)
                    elif i == 1:
                        col.append(2)
                    elif i == 2:
                        if len(delta_v) > 1:
                            delta_v = delta_v.dropna().values[0]
                        col.append(delta_v)
                    else:
                        print(output_match[names_columns[i]].values[0])
                        col.append(output_match[names_columns[i]].values[0])
            '''
            if len(output_match) < 1:
                nomatch = -9999.99*np.ones((1,20))
                nomatch = list(nomatch.astype(str))
                nomatch[0][0] = name
                nomatch[0][1] = 1
                #output_match.insert(0, column='wallaby_id', value=name)
                #output_match.insert(1, column='delta_velocity',value=delta_v)
                out = pd.DataFrame(data=nomatch,columns=total_columns)
            else:
                output_match.insert(0,column='wallaby_id',value=name)
                output_match.insert(1, column='delta_velocity',value=delta_v)
                output_match.insert(1, column='delta_velocity_flag', value=2)
                out = output_match
        # '''
    return out         
    #create output dataframe
    #out = pd.DataFrame(data = def_columns, columns = str(def_columns))
    #print(list(itertools.chain(*def_columns)))
    #return list(itertools.chain(*def_columns))

df_columns = ['wallaby_id', 'delta_velocity_flag', 'delta_velocity', 'objID', 'ra', 'dec', 'objtype',\
                    'modelMag_u', 'modelMag_g', 'modelMag_r', 'modelMag_i', 'modelMag_z', 'modelMagErr_u',\
                    'modelMagErr_g', 'modelMagErr_r', 'modelMagErr_i', 'modelMagErr_z']#, 'z', 'zErr']

