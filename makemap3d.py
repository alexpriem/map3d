from math import log, log10
import os, sys, argparse, json,re
import shpUtils

import dateutil.parser






class mapmaker:

    def __init__(self, args):
        self.args=args
        self.shapes=[]
        self.total_length=0
        self.minx=None
        self.maxx=None
        self.miny=None
        self.maxy=None
        


    def read_keyfile(self,keyfile,sep):

        keylabel={}
        if keyfile is not None:
            f=open(keyfile)
            f.readline()
            for line in f.readlines():
                keyvalue=line.strip().split(sep)                
                if len(keyvalue)!=2:
                    raise RuntimeError("expected key/value pairs in file:"+keyfile)
                keylabel[keyvalue[0]]=keyvalue[1]
        return keylabel

    def write_keyfile(self,filename,keydict,prefix):
            f=open(filename,'w')
            keytxt=json.dumps(keydict.keys());
            f.write("var %s_keys=%s;\n\n" %(prefix,keytxt));
            valuestxt=json.dumps(keydict.values());
            f.write("var %s_labels=%s;\n\n" %(prefix,valuestxt));
            dicttxt=json.dumps(keydict);
            f.write("var %s_label2key=%s;\n\n" %(prefix,dicttxt));
            f.close()








    def rescale_color (self, val, minval, maxval):

        minval=0;
        maxval=log(maxval)    
        if val is None:
            return (1.0,1.0,1.0)
        if val!=0:
            val=log(val)
            
        if val<minval:
            val=minval
        if val>maxval:
            val=maxval
        val=(val-minval)/(1.0*(maxval-minval))   # range van 0 tot 1
        
      #  print 'ranged val:', val

        colorval=(1-val,1-val,1)
        colorval=(1,1-val,1-val)
        return colorval
        
        

    def get_max_data(self, filename):

        f=open(filename)
        f.readline()
        cols=f.readline().strip().split(',')
        maxdata=int(cols[-1])
        for line in f.readlines():
            cols=line.strip().split(',')
            val=int(cols[-1])
            if val>maxdata:
                maxdata=val
        return maxdata



    def read_frame(self, f,varnames, prevline=None):
        
        datadict={}    
        cols=prevline.strip().split(',')
        prevcol=None
        while prevcol is None or prevcol==cols[0]:        
            prevcol=cols[0]
            datadict[cols[1]]=int(cols[-1])
            line=f.readline()
            cols=line.strip().split(',')      
            if len(cols)<=1:
                return None, None, None
      #  print datadict.items()
        return datadict, prevcol, line


    def read_simple_frame(self, f, varnames):
        datadict={}

        for line in f.readlines():
            cols=line.strip().split(',')
            datadict[cols[0]]=int(cols[-1])
            if len(cols)<=1:
                return datadict
        return datadict


    def prep_js (self, args):

        csvfile=args['csvfile']
        csvdir=args['csvdir']
        
        sep=args['sep']
        outfile=args['outfile']
        recordinfo=args['recordinfo']
        recs=recordinfo.strip().split(',')
        # simpele syntaxcheck
        allowed_keys=['regio','regiolabel','keylabel','key','data','dummy','date','norm']
        for r in recs:            
            if r not in allowed_keys:
                raise RuntimeError('unknown key for recordinfo:'+str(r)+'\nallowed keys:'+str(allowed_keys))
        
        regiocol=recs.index('regio')
        regiolabelcol=None
        if 'regiolabel' in recs:
            regiolabelcol=recs.index('regiolabel')
        keylabelcol=None
        if 'keylabel' in recs:
            keylabelcol=recs.index('keylabel')
        keycol=None
        if 'key' in recs:
            keycol=recs.index('key')

        normcol=None
        if 'norm' in recs:
            normcol=recs.index('norm')
        datecol=None
        if 'date' in recs:
            datecol=recs.index('date')
        datacols = [i for i, x in enumerate(recs) if x == "data"]

        if csvdir:
            csvfiles = [ f for f in os.listdir(csvdir)] # if re.match(r'\w*\.csv', f) and os.path.isfile(csvdir+f) ]
            
            csvfile=csvdir+'/'+csvfiles[0]
            
        
        f=open (csvfile)

        g=open("js/data.js",'w')    

        varnames=f.readline().strip().split(sep)
        
        xlabel=args.get('xlabel','')
        ylabel=args.get('ylabel','')
        label_xpos=args.get('label_xpos','')
        label_ypos=args.get('label_ypos','')
        title=args.get('title','')
        g.write('var xlabel="%s";\n' % xlabel);
        g.write('var ylabel="%s";\n' % ylabel);
        g.write('var label_xpos=%s;\n' % label_xpos);
        g.write('var label_ypos=%s;\n' % label_ypos);
        g.write('var label="%s";\n' % title);
        
        
        s='var varnames=['
        if datecol is not None:        
            s+='"'+varnames[datecol]+'",'
        s+='"'+varnames[regiocol]+'",'
        s+=','.join(['"'+varnames[col]+'"' for col in datacols])+'];\n'
        g.write(s)
        
        var_types=[]
        if 'key' in recs:
            var_types.append('key')
        if not('key' in recs) and ('keylabel' in recs):
            var_types.append('keylabel')
        if 'date' in recs:
            var_types.append('date')
        if 'regio' in recs:
            var_types.append('regio')
        var_types+=['data']*len(datacols)                        
        s=json.dumps(var_types)    
        g.write('var var_types='+s+';\n\n')


        
        
        
        
        # build js-object: [keys], date, regio, data1, data2
        #

        var_min=[None]*len(datacols)
        var_max=[None]*len(datacols)
        mindatestr=None
        maxdatestr=None
        line_out='\n'
        g.write('var data=[\n')
        regiolabels={}
        keylabels={}


        total_regio={}
        total_date={}
        date_keys={}
        if keycol is not None:
            for key in keys.values():
                total_regio_key[key]={}
                total_date_key[key]={}


        
        for line in f.readlines():        
            g.write(line_out)
            cols=line.strip().split(sep)
            line_out='['
            regio=cols[regiocol]
            if regiolabelcol is not None:
                regiolabels[regio]=cols[regiolabelcol]
            if keylabelcol is not None:
                keylabels[regio]=cols[keylabelcol]

            if (datecol is not None):
                date=cols[datecol]
                d=dateutil.parser.parse(date)
                js_date="new Date('"+d.isoformat()+"')"
                if mindatestr is None or d<mindate:
                    mindate=d
                    mindatestr=js_date
                if maxdatestr is None or d>maxdate:
                    maxdate=d
                    maxdatestr=js_date
                #line_out+=date+","
                
                line_out+="new Date('"+date.replace(' ','T')+"'),"
            line_out+=regio + ','
            if keycol is not None:
                line_out+=cols[keycol]+','
            if keycol is None and keylabelcol is not None:
                line_out+=cols[keylabelcol]+','

            line_out+=','.join([cols[col] for col in datacols])
            line_out+='],\n'
            #print line_out
            numdatacols=len(datacols)
            for i,col in enumerate(datacols):
                val=float(cols[col])
                if var_min[i] is None or val<var_min[i]:
                    var_min[i]=val
                if var_max[i] is None or val>var_max[i]:
                    var_max[i]=val

                if not(regio in total_regio):
                    total_regio[regio]=[0]*numdatacols
                if not(js_date in total_date):
                    total_date[js_date]=[0]*numdatacols
                    date_keys[d]=0

                # aggegraten over dataset bepalen
                # naar regio, date
                # en naar key x regio, key x date
                total_regio[regio][i]+=val
                total_date[js_date][i]+=val
                if keycol is not None:
                    if not(regio in total_regio_key[key]):
                        total_regio_key[key][regio]=[0]*numdatacols                    
                    if not(date in total_date_key[key]):
                        total_date_key[key][js_date]=[0]*numdatacols
                    total_regio_key[key][regio][i]+=val
                    total_date_key[key][js_date][i]+=val
                    

                                


                
        var_min.insert(0,0)
        var_max.insert(0,0)
        if datecol is not None:
            var_min.insert(0,mindatestr)         # min /max datum invoegen?
            var_max.insert(0,maxdatestr)
            
        
                    
        line_out=line_out[:-2]
        g.write(line_out+'];\n')        
        total_regio=[[0, int(row[0])]+list(row[1]) for row in sorted(total_regio.items())]
        s=json.dumps(total_regio)
        
        g.write('\n\nvar total_regio='+s+';\n')
        # datum sorteren voor tijdreeks.        
        
        

        total_date=[[row[0]]+list(row[1]) for row in sorted(total_date.items())]
        s=json.dumps(total_date).replace('"','')
        # date-step bepalen
        date_keys=sorted(date_keys.keys())
        minms=None
        for i,val in enumerate(date_keys[1:]):
            dk=date_keys[i]-date_keys[i-1];            
            ms=dk.days*24*3600*1000+dk.seconds*1000 # to milliseconds
            if minms is None:   
                minms=ms
            if ms<minms and ms>0:
                minms=ms
            
        g.write('\n\nvar datestep_ms=%d;' % ms)
        
        
        

        
        g.write('\n\nvar total_date='+s+';\n')
        if keycol is not None:
            s=json.dumps(total_regio_key)
            g.write('\n\nvar total_regio_key='+s+';\n')
            for key in keys.values():
                total_date_key[key]=sorted(total_date_key[key].items())
            s=json.dumps(total_date_key)
            g.write('\n\nvar total_date_key='+s+';\n')

        f.close()

        if csvdir:
            s=json.dumps(csvfiles)
            g.write('\n\n var selectie='+s+';\n');

        keyfile=args['keyfile']
        if keyfile is not None:
            keylabels=self.read_keyfile(keyfile,sep)
        regiofile=args['regiofile']
        if regiofile is not None:
            regiolabels=self.read_keyfile(regiofile,sep)
                                
        self.write_keyfile('js/regiolabels.js',regiolabels,'regio')
        self.write_keyfile('js/keylabels.js',keylabels,'country')
            

            
        s=json.dumps(var_min).replace('"','') # quotes om datums verwijderen    
        g.write('\n\nvar var_min='+s+';\n')
        s=json.dumps(var_max).replace('"','')        
        g.write('\n\nvar var_max='+s+';\n')
        g.close()        





    def load_shapefile(self,infile):
        self.shaperecords=shpUtils.loadShapefile(infile)
        return self.shaperecords
        
            
    def autoscale (self, shpRecords=None):
        minx=None
        maxx=None
        miny=None
        maxy=None
        if shpRecords is None:
            shpRecords=self.shaperecords
        for i in range(0,len(shpRecords)):
            polygons=shpRecords[i]['shp_data']['parts']
            for poly in polygons:
                for point in poly['points']:
                    tempx=float(point['x'])
                    tempy=float(point['y'])
                    if minx is None or tempx<minx:
                        minx=tempx
                    if miny is None or tempy<miny:
                        miny=tempy
                    if maxx is None or tempx>maxx:
                        maxx=tempx
                    if maxy is None or tempy>maxy:
                        maxy=tempy
        #print minx, maxx, miny, maxy
        self.dx=maxx-minx
        self.dy=maxy-miny
        self.minx=minx
        self.maxx=maxx
        self.miny=miny
        self.maxy=maxy


    def build_area_js (self, shpRecords=None, field_id=None):
        
        if self.minx is None:
            self.autoscale(shpRecords)
        minx=self.minx
        miny=self.miny
        dx=self.dx
        dy=self.dy
        width=self.width
        height=self.height        
        
        js='var xy=[\n' 
        for i in range(0,len(shpRecords)):
            dbfdata=shpRecords[i]['dbf_data']            
            shape_id=dbfdata[field_id]    
            polygons=shpRecords[i]['shp_data']['parts']
            for shape_nr, poly in enumerate(polygons): 
                
                x = []
                y = []
                s='[' 
                point=poly['points'][0]        
                tempx = ((float(point['x'])-minx)/dx)*width
                tempy = ((float(point['y'])-miny)/dy)*height
                s+='[%.2f, %.2f],\n' % (tempx, tempy)
                for point in poly['points']:
                    tempx = ((float(point['x'])-minx)/dx)*width
                    tempy = ((float(point['y'])-miny)/dy)*height
                    x.append(tempx)
                    y.append(tempy)
                    
                    s+=' [%.2f, %.2f],\n' % (tempx,tempy)
                js+=s[:-2]+'],\n'
            
        js=js[:-2]+'];\n'
        
        return js


    def get_shapeids (self, shpRecords=None, field_id=None):
        if shpRecords is None:
            shpRecords=self.shaperecords

        shape_ids={}
        for i in range(0,len(shpRecords)):
            dbfdata=shpRecords[i]['dbf_data']
            shape_id=dbfdata[field_id]    
            polygons=shpRecords[i]['shp_data']['parts']
        
            regio=[]
            for shape_nr, poly in enumerate(polygons):
                regiopart='%d_%d' % (shape_id, shape_nr)
                regio.append(regiopart)
            shape_ids[shape_id]=regio
        return shape_ids




    def build_centroid_js (self, shpRecords=None, field_id=None):
        
        if self.minx is None:
            self.autoscale(shpRecords)
        minx=self.minx
        miny=self.miny
        dx=self.dx
        dy=self.dy
        width=self.width
        height=self.height        
        
        js='var centroids={\n'
        for i in range(0,len(shpRecords)):
            dbfdata=shpRecords[i]['dbf_data']            
            shape_id=dbfdata[field_id]    
            polygons=shpRecords[i]['shp_data']['parts']
            for shape_nr, poly in enumerate(polygons):                 
                point=poly['points'][0]        
                x = ((float(point['x'])-minx)/dx)*width
                y = ((float(point['y'])-miny)/dy)*height
                js+='%d:[%.3f,%.3f],\n' % (shape_id,x,y)
                
        js=js[:-2]+'};\n'
        return js



    def save_map(self, args):

        self.width=800
        self.height=800        
        
        shpRecords=shpUtils.loadShapefile(args["area_shapefile"])
        outlineRecords=shpUtils.loadShapefile(args["outline_shapefile"])
        centroidRecords=shpUtils.loadShapefile(args["centroid_shapefile"])
        area_js=self.build_area_js(shpRecords, args['shape_fieldID'])
        centroid_js=self.build_centroid_js(shpRecords, args['shape_fieldID'])
        labelID=args['shape_labelID']
        outfile=args['outfile']

        
        f=open("js\\area.js","w")
        f.write(area_js)
        f.write("\n")
        #f.write("var total_length=%d;\n" % self.total_length)
        f.write("var minx=%d;\n" % self.minx)
        f.write("var miny=%d;\n" % self.miny)
        f.write("var maxx=%d;\n" % self.maxx)
        f.write("var maxy=%d;\n" % self.maxy)
        f.write("var dx=%d;\n" % self.dx)
        f.write("var dy=%d;\n" % self.dy)
        f.write("var width=%d;\n" % self.width)
        f.write("var height=%d;\n" % self.height)
        
        f.close()

        f=open("js/centroids.js",'w')        
        f.write(centroid_js);
        f.close()

        regio_ids=self.get_shapeids(shpRecords, args['shape_fieldID'])
        for regio,shapes in regio_ids.items():
            regio_ids[regio]=[shape[1:] for shape in shapes]
                

#        f=open("js/regioshapes2.js",'w')        
#        s=json.dumps(regiocoords);
#        f.write("var regioshapes2="+s+';\n');
        #f.close()


        s='{}'    
        if labelID is not None:
            self.write_keyfile('js/regiolabels.js',labels,'regio')




    def save_html (self, args):

        outfile=args["outfile"]
        fullhtml=args['fullhtml']
        verbose=args['verbose']
        
        html=open ("map.html",'r').read()    
        f=open(outfile+'.html','w')
        
        cssfrags=html.split('<link href="')
        
        f.write(cssfrags[0])
        cssfiles=[cssfrag.split('"')[0] for cssfrag in cssfrags[1:]]                
        for cssfrag in cssfrags[1:]:
            cssfile=cssfrag.split('"')[0]
            
           # print cssfile
            if fullhtml:
                f.write('\n<style>\n')
                css=open(cssfile,"r").read()
                f.write(css)
                f.write('\n</style>\n')
                if verbose:
                    print cssfile,'included'
            else:
                s='<link href="'+cssfile+'" rel="stylesheet" type="text/css">'
                f.write(s)
                if verbose:
                    print cssfile,'skipped'
                
                

        if fullhtml:
            not_replaceable_js=[]
        else:        
            not_replaceable_js=['js-lib/jquery-2.0.3.min.js',
                            'js-lib/three.min.js',
                            'js-lib/Detector.min.js',
                            'js-lib/stats.min.js',
#                            'js-lib/chroma.min.js',
#                            'js/colormaps.js',                        
                            'js/centroids.js',
                            'js/area.js'
                           ]
        jsfrags=html.split('script src="')            
        for jsfrag in jsfrags[1:]:
            jsfile=jsfrag.split('"')[0]
            if jsfile in not_replaceable_js:
                s='<script type="text/javascript" src="'+jsfile+'"> </script>\n'
                f.write(s)
                if verbose:
                    print jsfile,'skipped'
            else:
                f.write('\n<script type="text/javascript">\n')        
                js=open(jsfile,'r').read()    
                f.write(js)
                f.write('</script>\n')
                if verbose:
                    print jsfile,'included'
            

        body=html.split("<body>")
        body=body[1]
        svg=open(outfile+'.svg','r').read()                        
        body=body.replace('<svg > </svg>',svg)
        f.write("</head>\n")
        f.write("<body>\n")
        f.write(body)
        f.close()
        
        
    




    


parser = argparse.ArgumentParser(description='generate calendar from repeating data')

parser.add_argument('-sh', '--shapefile', dest='area_shapefile',  help='esri intput shapefile', required=True)
parser.add_argument('-sf', dest='shape_fieldID',  help='shapefile area key variabele', required=True, default=None)
parser.add_argument('-sl', dest='shape_labelID',  help='shapefile area label variabele', required=False, default=None)

parser.add_argument('-l', '--outlinefile', dest='outline_shapefile',  help='esri intput shapefile', required=False, default=None)
parser.add_argument('-lf', dest='outline_fieldID',  help='shapefile area key variabele', required=False, default=None)
parser.add_argument('-ll', dest='outline_labelID',  help='shapefile area label variabele', required=False, default=None)

parser.add_argument('-ch','--centroidfile', dest='centroid_shapefile',  help='centroidfile', required=False)
parser.add_argument('-cf', dest='centroid_fieldID',  help='centroid shapefile key variabele', required=False, default=None)

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-c', '--csvfile', dest='csvfile',  help='csv input file name')
group.add_argument('-cd', '--csvdir', dest='csvdir',  help='directory with csv input files')
parser.add_argument('-s', '--sep', dest='sep',  help='delimiter of csv infile', required=False, default=',')
parser.add_argument('-o', dest='outfile',  help='output basename for .svg/.js', required=False, default='')
parser.add_argument('-fullhtml', dest='fullhtml',  help='include everything (js, css) in html file', required=False, default=False, action='store_true')
parser.add_argument('-verbose', dest='verbose',  help='verbose debuginfo', required=False, default=False, action='store_true')
parser.add_argument('-r', '--record', dest='recordinfo',  help='recordbeschrijving: regiokey, norm, data, regiolabel, dummy, key, keylabel', required=True)
parser.add_argument('-xlabel', dest='xlabel',  help='xaxis label', required=False, default=0.1)
parser.add_argument('-ylabel', dest='ylabel',  help='yaxis label', required=False, default=0.9)
parser.add_argument('-label_xpos', dest='label_xpos',  help='xpos label', required=False, default=0.1)
parser.add_argument('-label_ypos', dest='label_ypos',  help='ypos label', required=False, default=0.9)
parser.add_argument('-title', dest='title',  help='title', required=False, default='')
parser.add_argument('-kf','--keyfile', dest='keyfile',  help='keyfile', required=False)
parser.add_argument('-rf','--regiofile', dest='regiofile',  help='regiofile', required=False)


args=vars(parser.parse_args())
m=mapmaker(args)


m.prep_js(args)
m.save_map (args)
m.save_html (args)

        
