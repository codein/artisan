"""Extension to the Polygon Module
"""
import Polygon,Polygon.IO
import Polygon.Shapes
from math import sin, cos, pi, ceil, sqrt, pow
from operator import itemgetter
import Image
import Polygon, Polygon.IO
import ImageOps
import os



""" PyPolygon adds to functionality to Polygon """
class PolygonUtil():

    """ Calcuates radius of a bounding circle
    of one contour. Similar to the boundingBox function
    """
    def boundingCircleRadius(self,polygon):
        qxmin, qxmax, qymin, qymax = polygon.boundingBox()
        diameter_x = abs(qxmin - qxmax)
        diameter_y = abs(qymin - qymax)
        if diameter_x > diameter_y:
            radius =   ceil(diameter_x/2)
        else:        
            radius =  ceil(diameter_y/2)
        
        return radius+2

    """Re-draws around the given point (xs,ys)
    such that the re-drawn polygon has the center (xs,ys)
    """
    def redraw(self,polygon,xs,ys):
        xc,yc = polygon.center()
        #print xc,yc
        polygon.shift(xs-xc,ys-yc)
        xc,yc = polygon.center()
        #print xc,yc
    """Fit Polygon q around t and returns best possible fit with no overlap"""
    def fit(self,t,q,output_count=5, write = False):
        print '#Finding fits.'
        fits = self.fitAround(t, q,output_count = output_count,write=write)
        tx, ty = t.center()        
        for fit in fits:
            x,y = fit.get('center')
            x -= tx 
            y -= ty
            fit['distance'] = sqrt(pow(y,2)+pow(x,2)) 
        fits = sorted(fits, key=itemgetter('distance'))
        print '#Found %d fits. %s Choosen' % (len(fits), fits[0])
        return fits[0] 
        
    """Fit Polygon q around t and returns every possible centers and orientation for q around t with no overlap"""
    def fitAround(self,t,q,output_count = 32, rotation_start = 0, rotation_end = 1, write = False ): 
        qx, qy = q.center()
        qradius = self.boundingCircleRadius(q)
#        print qx, qy, qradius
        
        tx, ty = t.center()
        tradius = self.boundingCircleRadius(t)
#        print tx, ty, tradius
        outputs = []        
        surface = Polygon.Shapes.Circle(radius = (2*qradius)+tradius, center = (tx, ty))
        surface = surface - t
        start_radius = 0
        for i in range(int(qradius+tradius)):
            c = Polygon.Shapes.Circle(radius = i, center = t.center())
            if not t.covers(c):
                start_radius = i
                break
            
        for i in range(start_radius,int(qradius+tradius)):
#            print i,t.center()      
            c = Polygon.Shapes.Circle(radius = i, center = t.center())
            for (x,y) in c.contour(0):
#                print i,output_count,x,y,surface.isInside(x,y)
                if surface.isInside(x,y):
                    temp_q = Polygon.Polygon(q)
                    self.redraw(temp_q,x,y)
                    for angle in range(rotation_start,rotation_end,1):
                        temp_q.rotate(angle, x, y)
                        if (not temp_q.overlaps(t)) and (surface.covers(temp_q)) and output_count !=0:
                            output_count-=1 
                            print "##%d Remaining" % output_count
                            surface = surface - temp_q
                            outputs.append(dict(angle = angle, center = (x,y)))    
                        if output_count ==0:   
                            break
            if output_count ==0:   
                break 
        if write:
            Polygon.IO.writeSVG('surface%d.svg' % output_count, (surface,))
        return outputs  
    
    """Given a image get a polygon constituting the image"""
    def getPolygon(self,file):
        im= Image.open(file)
        pixels = list(im.getdata())
        width, height = im.size
        print width,height
        pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
        p = Polygon.Polygon()
        x_contours_first = []
        x_contours_last = []
        y_contours_first = []
        y_contours_last = []
        for y in range(width-1):
            first,last = 0,0
            for x in range(height-1):
                if (pixels[x][y] != pixels[x+1][y]):
                    if first == 0:
                        first = (x,y)
                    else:
                        last = (x,y)
            if first != 0:
                x_contours_first.append(first)
            if last != 0:
                x_contours_last.append(last)
        x_contours_last.reverse()
        
        p.addContour(x_contours_first+x_contours_last)
        xmin, xmax, ymin, ymax = p.boundingBox()
#        print abs(xmin - xmax), abs(ymin - ymax)
        return p         
    
    def convert_to_alpha(self,im):
        img = im.convert("RGBA")
        datas = img.getdata()
        newData = list()        
        for item in datas:
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        img.putdata(newData)
        return img

    """Fit image fileq around filet and returns best possible fit with no overlap"""
    def image_merge(self,filet,fileq,output_count=5,write=False,show=False):
     

        print 'Merging %s & %s for %d outputs' % (filet, fileq, output_count)
        t_im= Image.open(filet)
        q_im= Image.open(fileq)
        t_im=poly_util.convert_to_alpha(t_im)
        q_im=poly_util.convert_to_alpha(q_im)
    #    t_im = t_im.rotate(90)
    #    q_im = q_im.rotate(90)
        q_width, q_height = q_im.size
        t_width, t_height = t_im.size 
        
        t = poly_util.getPolygon(filet)
        Polygon.IO.writeSVG('testt.svg', (t,))
        q = poly_util.getPolygon(fileq)
        Polygon.IO.writeSVG('testq.svg', (q,))
        
        #fits polygon q arounf t
        fit_config = poly_util.fit(q,t,output_count=output_count)
        x,y = fit_config.get('center')
        angle =fit_config.get('angle')
        #offset the polygon for suggested fit
        poly_util.redraw(t, x, y)
        t.rotate(fit_config.get('angle'), x, y)
    #####before shifting    
    #    print 'q bounding'
    #    xmin, xmax, ymin, ymax = q.boundingBox()
    #    print xmin, xmax, ymin, ymax
    #    print abs(xmin - xmax), abs(ymin - ymax)
    #    
    #    print 't bounding'
        xmin, xmax, ymin, ymax = t.boundingBox()
    #    print xmin, xmax, ymin, ymax
    #    print abs(xmin - xmax), abs(ymin - ymax)    
        #polygons are shifted so that both polygons after merge lie in the first quadrant
        offset_x,offset_y = 0,0
        if xmin<0:
            offset_x = -xmin
        if ymin <0:
            offset_y = -ymin        
        t_x,t_y = t.center()
        poly_util.redraw(t, t_x+offset_x, t_y+offset_y)
        q_x,q_y = q.center()
        poly_util.redraw(q, q_x+offset_x, q_y+offset_y)
    #####after shifting     
    #    print 'q bounding'
        qxmin, qxmax, qymin, qymax = q.boundingBox()
    #    print qxmin, qxmax, qymin, qymax
    #    
    #    print 't bounding'
        txmin, txmax, tymin, tymax = t.boundingBox()
    #    print txmin, txmax, tymin, tymax
         
        output = q + t
        
        #merge the image to reflect suggested fit_config of output polygon
        base_im = Image.open('/home/codein/workspace3/artist/base.png')
        
    #    print 'output bounding'
        outputxmin, outputxmax, outputymin, outputymax = output.boundingBox()
#        print  outputxmin, outputxmax, outputymin, outputymax
        #render a base image big enought o hold both the images after merging
        base_width, base_height =  int(max((q_width+qymin),(t_width+tymin))), int(max((q_height+qxmin),(t_height+txmin)))
        base_im = base_im.resize((base_width, base_height))
        base_im=poly_util.convert_to_alpha(base_im)
        
        offset_y = int(base_height-qymin)
        q_box = (0,0,q_width,q_height)
        #offset for polygon q and orientation, since the output polygon is potted at a 90 rotated plane
        q_box_offset =  (int(0+qymin),int(0+qxmin),int(q_width+qymin),int(q_height+qxmin))    
     
    #    print '\n\nmove to',qxmin,  qymin, qxmax,qymax
    #    print 'qbox cut at%s'%str(q_box)
    #    print 'qbox paste at%s'%str(q_box_offset)
        q_region = q_im.crop(q_box)
        #cut the image from the original image and paste it at the offset location
        base_im.paste(q_region,q_box_offset,q_region)
        
        offset_y = int(base_height-tymin)
        t_box = (0,0,t_width,t_height)
        t_box_offset =  (int(0+tymin),int(0+txmin),int(t_width+tymin),int(t_height+txmin))    
    #    print '\n\nmove to',txmin,  tymin, txmax,tymax
    #    print 'tbox cut at%s'%str(t_box)
    #    print 'tbox paste at%s'%str(t_box_offset)
        t_region = t_im.crop(t_box)
        base_im.paste(t_region,t_box_offset,t_region)
        
        if show:
            base_im.show()
        
        if write:
            Polygon.IO.writeSVG('testb.svg', (output,))
            base_im.save("img2.png", "PNG")
        print 'Merged %s %s' % (filet,fileq)
        return base_im
    
         
        
poly_util = PolygonUtil()
        
#TODO:(codein) change this to a actual unit test using unittest module
def unit_test():
    q = Polygon.Polygon(((0.0, 0.0), (10.0, 0.0), (10.0, 5.0), (0.0, 5.0)))
    t = Polygon.Polygon(((1.0, 1.0), (3.0, 1.0), (2.0, 3.0)))
    poly_util = PolygonUtil()
    a = q+t
    Polygon.IO.writeSVG('testa.svg', (a,))
    poly_util.redraw(t, 5, 5)
    a = q+t
    Polygon.IO.writeSVG('testb.svg', (a,))
    
def polygon_merge():
    q = Polygon.Polygon(((0.0, 0.0), (10.0, 0.0), (10.0, 5.0), (0.0, 5.0)))
    t = Polygon.Polygon(((1.0, 1.0), (3.0, 1.0), (2.0, 3.0)))
    poly_util = PolygonUtil()
    fit_config = poly_util.fit(q,t)
    x,y = fit_config.get('center')
    poly_util.redraw(t, x, y)
    t.rotate(fit_config.get('angle'), x, y)
    q = q + t
    Polygon.IO.writeSVG('testb.svg', (q,))
    
def image_read():
    file = '/home/codein/artist/test1/eagle-tribal-tattoo-design-free-designs--2-1-tattoodonkey.com.jpg'
    t = poly_util.getPolygon(file)
    Polygon.IO.writeSVG('/home/codein/artist/test1/testb.svg', (t,))
    
def iamge_merge():
    filet,fileq = '/home/codein/artist/test1/eagle-tribal-tattoo-design-free-designs--2-1-tattoodonkey.com.jpg','/home/codein/artist/test1/Inca_Bird_Tattoo_by_Rustyoldtown.jpg'
    base = poly_util.image_merge(filet, fileq, 5, True)
    base_file ="%s/Merging.png" % '/home/codein/artist/test1/'    
    
def images_merge():         
    path = '/home/codein/artist/test1'
    listing = os.listdir(path)
    base = None
    count = 0
    for infile in listing:
        file = "%s/%s" %( path,infile)
        if not base:
            base = file            
        else:
            count+=1
            print base,file
            base = poly_util.image_merge(base, file, 5)
            base_file ="%s/Merging.png" % path
            base.save(base_file, "PNG")
            base = base_file            

    
if __name__ == "__main__":
    images_merge()






