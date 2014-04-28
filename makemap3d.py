from shapely.geometry import Polygon
from shapely.wkb import loads
from osgeo import ogr, osr
from matplotlib import pyplot
from math import log, log10
import os, sys, argparse, json,re

import xml.etree.ElementTree as ET
from StringIO import StringIO
import dateutil






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


    def dump_element(self,element):
        path=element.get_path()
        vertices = [[vertex[0],vertex[1]] for (vertex,code) in path.iter_segments(simplify=False)]
        x_vertices= [v[0] for v in vertices]
        y_vertices= [v[1] for v in vertices]                 
        if self.minx is None:
            self.minx=x_vertices[0]
        if self.miny is None:
            self.miny=y_vertices[0]
        if self.maxx is None:
            self.maxx=x_vertices[0]
        if self.maxy is None:
            self.maxy=y_vertices[0]

        self.minx=min(x_vertices+[self.minx])
        self.miny=min(y_vertices+[self.miny])
        self.maxx=max(x_vertices+[self.maxx])
        self.maxy=max(y_vertices+[self.maxy])                
                        
        self.shapes.append(vertices)
        self.total_length+=len(vertices)


    def draw_areas(self,p,graph,color,regio_id):

        # returns a list of dom-id's for every polygon drawn
        # (multipolygons get
        # dom-id format:  r%regioid_%counter
        #

        if color is None:
            color=(1.0,1.0,1.0)
        bordercolor=(120/255.0,120/255.0,120/255.0)
        borderwidth=0.5
        
        if not(hasattr(p,'geoms')): 
            xList,yList = p.exterior.xy
            h=graph.fill(xList,yList, color=color)
            l=graph.plot(xList,yList, 
                       color=bordercolor,
                       linewidth=borderwidth)
            for il, element in enumerate(h):
                element.set_gid ("a%d_1" % regio_id)
                self.dump_element(element)
            for il, element in enumerate(l):
                element.set_gid ("l%d_1" % regio_id )
                self.dump_element(element)
            return ["a%d_1" % regio_id]
        else:
            j=1
            regs=[]
            for poly in p:
                xList,yList = poly.exterior.xy
                h=graph.fill(xList,yList, color=color)
                l=graph.plot(xList,yList,
                            color=bordercolor,
                            linewidth=borderwidth)            
                for il, element in enumerate(h):
                    element.set_gid ("a%d_%d" % (regio_id,j) )   # polylines gaan niet goed
                    self.dump_element(element)                                    
                for il, element in enumerate(l):
                    element.set_gid ("l%d_%d" % (regio_id,j) )
                    self.dump_element(element)
                regs.append("a%d_%d" % (regio_id, j))                
                j+=1
            
                
            return regs


    def draw_outline(self,p,graph,outline_id):

        # returns a list of dom-id's for every polygon drawn
        # (multipolygons get
        # dom-id format:  r%regioid_%counter
        #
        
        bordercolor=(40/255.0,40/255.0,40/255.0)
        borderwidth=1.5

        if not(hasattr(p,'geoms')):            
            xList,yList = p.xy
            l=graph.plot(xList,yList, 
                       color=bordercolor,
                       linewidth=borderwidth)
            for il, element in enumerate(l):
                element.set_gid ("o%d_1" % outline_id )
            return ["o%d_1" % outline_id]
        else:
            j=1
            regs=[]
            for poly in p:
                xList,yList = poly.xy
                l=graph.plot(xList,yList,
                            color=bordercolor,
                            linewidth=borderwidth)                            
                for il, element in enumerate(l):
                    element.set_gid ("o%d_%d" % (outline_id,j) )                
                regs.append("o%d_%d" % (outline_id, j))                
                j+=1            
            return regs


    def draw_centroid (self,p,graph,centroid_id):

        ids=[]
        bordercolor=(120/255.0,120/255.0,120/255.0)
        borderwidth=0.5
        
        if not(hasattr(p,'geoms')): 
            x,y = p.xy            
            l=graph.plot(x,y,
                        color=bordercolor,
                        linewidth=borderwidth)            
            l[0].set_gid ("c%d" % centroid_id)
            

        return ids


    def read_files (self):

        csvfile=args["csvfile"]               
        outfile=args["outfile"]
        fullhtml=args["fullhtml"]

        self.driver = ogr.GetDriverByName('ESRI Shapefile')
        self.area_shapefile=args["area_shapefile"] 
        self.area_sh = ogr.Open(self.area_shapefile)
        self.area_layer = self.area_sh.GetLayer()

        self.outline_shapefile=args["outline_shapefile"]
        if self.outline_shapefile is not None:
            self.outline_sh = ogr.Open(self.outline_shapefile)
            self.outline_layer = self.outline_sh.GetLayer()

        self.centroid_shapefile=args["centroid_shapefile"]
        if self.centroid_shapefile is not None:
            print 'opened centroidfile', self.centroid_shapefile
            self.centroid_sh = ogr.Open(self.centroid_shapefile)
            self.centroid_layer = self.centroid_sh.GetLayer()

        f=open (csvfile)
        varnames=f.readline().strip().split(',')
        self.maxdata=m.get_max_data(args["csvfile"])
        line=f.readline()
        #mapdata, datum, line=read_frame(f,varnames,line)
        self.mapdata=self.read_simple_frame(f,varnames)


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





    def save_map (self, args):

        layer=self.area_layer
        mapdata=self.mapdata
        fieldID=args['shape_fieldID']
        labelID=args['shape_labelID']
        outfile=args['outfile']

       
        fig = pyplot.figure(figsize=(7, 8),dpi=300)    
        ax = fig.add_subplot(1,1,1)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        fig.frameon=False        
     #   for item in [fig, ax]:
     #       item.patch.set_visible(False)
        
        nonecounter=0
        regios=[]
        regio_ids={}
        regiolabels={}
        for feature in self.area_layer:
           # print feature.GetFieldCount()        
            regio=int(feature.GetField(fieldID))
            if labelID is not None:
                label=feature.GetField(labelID)
                regiolabels[regio]=label            
            geom=feature.GetGeometryRef()
            if geom is not None:    
                geometryParcel = loads(geom.ExportToWkb())
                ids= self.draw_areas(geometryParcel, ax, None, regio)    
                regios=regios+ids;
                regio_ids[regio]=ids
        print 'saving img:%s (nones:%d)' % (outfile, nonecounter)

        s=json.dumps(self.shapes)
        s=s.replace("]","]\n")
        s="var xy="+s+";"
        f=open("js\\area.js","w")
        f.write(s)
        f.write("\n")
        f.write("var total_length=%d;\n" % self.total_length)
        f.write("var minx=%d;\n" % self.minx)
        f.write("var miny=%d;\n" % self.miny)
        f.write("var maxx=%d;\n" % self.maxx)
        f.write("var maxy=%d;\n" % self.maxy)
        dx=self.maxx-self.minx
        dy=self.maxy-self.miny
        f.write("var dx=%d;\n" % dx)
        f.write("var dy=%d;\n" % dy)
        
        f.close()

        
        

        if self.outline_shapefile is not None:
            fieldID=args['outline_fieldID']
            labelID=args['outline_labelID']
            outfile=args['outfile']                
            
            outline_regios=[]
            outline_regio_ids={}
            outline_labels={}
            
            for feature in self.outline_layer:
               # print feature.GetFieldCount()        
                outline_regio=int(feature.GetField(fieldID))
                val=mapdata.get(outline_regio,None)
                if val is None:
                    nonecounter+=1                
                geom=feature.GetGeometryRef()
                if geom is not None:    
                    geometryParcel = loads(geom.ExportToWkb())
                    ids= self.draw_outline(geometryParcel , ax, outline_regio)    
                    outline_regios=outline_regios+ids;
                    outline_regio_ids[outline_regio]=ids


        centroid_ids={}
        if self.centroid_shapefile is not None:
            print 'reading centroid'
            fieldID=args['centroid_fieldID']            
            outfile=args['outfile']        
            for feature in self.centroid_layer:
                regio=int(feature.GetField(fieldID))
                #print regio
                geom=feature.GetGeometryRef()
                if geom is not None:    
                    geometryParcel = loads(geom.ExportToWkb())
                    ids= self.draw_centroid(geometryParcel , ax, regio)
                    centroid_ids[regio]=ids
                    
        # add classes to DOM-objects
        
        f = StringIO()
        pyplot.savefig(f, format="svg", bbox_inches = 'tight', pad_inches = 0)
        tree, xmlid = ET.XMLID(f.getvalue())
        
        
        centroids={}
        for r in regios:
            regio_nr=r[1:].split('_')[0]
            
            el = xmlid[r]  # lookup regio_id  in xml
            children=el.findall("*")
            child=children[0]   # altijd maar een child       
            child.attrib.pop("clip-path")
            child.set('class',"outline")
            child.set('data-regio',regio_nr)            
            child.set('id',r)
           # child.attrib.pop("style")  # inline style verwijderen-- performanceissue?
            el.attrib.pop("id")
            #sys.exit()
            
            
            
            # lookup border around regions
            line='l'+r[1:]    
            el = xmlid[line]  # lookup regio_id  in xml        
            el.set('class', "border")
            ochildren=el.findall("*")
            ochild=ochildren[0]
            ochild.attrib.pop("clip-path")
           # ochild.attrib.pop("style")
            

            # smerige hack om centroides uit data te krijgen
            dot='c'+regio_nr
            el = xmlid[dot]  # lookup centroids
            #el.set('class', "centroid_g")
            cchildren=el.findall("*")
            c_child=cchildren[0]
            try:
                c_child.attrib.pop("clip-path")
            except:
                pass
            c_child.set('id','p'+regio_nr)
            c_child.set('class','centroid')
            txt=c_child.get('d').strip()
            x,y=txt[1:].split(' ')
            #print x,y            
            centroids[int(regio_nr)]=[float(x),float(y)]
            
            
            
           # ochild.attrib.pop("style")

       
        del (xmlid['patch_1'])
        del (xmlid['patch_2'])
        del (xmlid['patch_3'])
        del (xmlid['patch_4'])
        #del (xmlid['patch_5'])
        
        root=el.find("..")        
        ET.ElementTree(tree).write(outfile+'.svg')
        
        for regio,shapes in regio_ids.items():
            regio_ids[regio]=[shape[1:] for shape in shapes]
        
        
        f=open("js/centroids.js",'w')        
        s=json.dumps(centroids);
        f.write("var centroids="+s+';\n');
        f.close()

        s=json.dumps(regio_ids);
        f=open

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
        
        
    




    
# Apparently, the `register_namespace` method works only with 
# python 2.7 and up and is necessary to avoid garbling the XML name
# space with ns0.
ET.register_namespace("","http://www.w3.org/2000/svg")    


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


m.read_files()





#print mapdata.items()

m.prep_js(args)
m.save_map (args)
m.save_html (args)

        
