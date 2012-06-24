"""Extension to the Polygon Module
"""
import Polygon,Polygon.IO
import Polygon.Shapes
from math import sin, cos, pi, ceil, sqrt, pow
from operator import itemgetter
import Image
import Polygon, Polygon.IO
import ImageOps




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
        for i in range(int(tradius/2),int(qradius+tradius)):
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
        contours_first = []
        contours_last = []
        for y in range(width-1):
            first,last = 0,0
            for x in range(height-1):
                if (pixels[x][y] != pixels[x+1][y]):
                    if first == 0:
                        first = (x,y)
                    else:
                        last = (x,y)
            if first != 0:
                contours_first.append(first)
            if last != 0:
                contours_last.append(last)
#            print first,last,'\n'        
        contours_last.reverse()        
        p.addContour(contours_first+contours_last)
        xmin, xmax, ymin, ymax = p.boundingBox()
        print abs(xmin - xmax), abs(ymin - ymax)
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
    c = Polygon.Shapes.Circle(radius = 1, center = (0,0))
    d = Polygon.Shapes.Circle(radius = 1, center = (5,0))
    e = Polygon.Shapes.Circle(radius = 1, center = (10,0))
    f = Polygon.Shapes.Circle(radius = 1, center = (0,0))
    g = Polygon.Shapes.Circle(radius = 1, center = (0,5))
    h = Polygon.Shapes.Circle(radius = 1, center = (0,10))    
    o = c+d+e+f+g+h
    Polygon.IO.writeSVG('o.svg', (o,))

def image_merge():
 
    filenamet,filenameq= '/home/codein/workspace3/artist/Untitled.png','/home/codein/workspace3/artist/celctic.png'
#    filenameq,filenamet='/home/codein/workspace3/artist/rectangle.png','/home/codein/workspace3/artist/triangle1.png'
    filenameq,filenamet=    '/home/codein/workspace3/artist/Celtic_Tribal_Howling_Coyote_by_WildSpiritWolf.png','/home/codein/workspace3/artist/Eagle_Tribal_Tattoo_by_Debaser2020.jpg'
    filenameq,filenamet= '/home/codein/workspace3/artist/Eagle-Tribal-Tattoo.bmp','/home/codein/workspace3/artist/img2.png'
    
    t_im= Image.open(filenamet)
    q_im= Image.open(filenameq)
    t_im=poly_util.convert_to_alpha(t_im)
    q_im=poly_util.convert_to_alpha(q_im)
#    t_im = t_im.rotate(90)
#    q_im = q_im.rotate(90)
    q_width, q_height = q_im.size
    t_width, t_height = t_im.size 
    
    t = poly_util.getPolygon(filenamet)
    Polygon.IO.writeSVG('testt.svg', (t,))
    q = poly_util.getPolygon(filenameq)
    Polygon.IO.writeSVG('testq.svg', (q,))
    fit_config = poly_util.fit(q,t,output_count=1)
    x,y = fit_config.get('center')
    angle =fit_config.get('angle')
    
    
    
    poly_util.redraw(t, x, y)
    t.rotate(fit_config.get('angle'), x, y)
    print 'q bounding'
    xmin, xmax, ymin, ymax = q.boundingBox()
    print xmin, xmax, ymin, ymax
    print abs(xmin - xmax), abs(ymin - ymax)
    
    print 't bounding'
    xmin, xmax, ymin, ymax = t.boundingBox()
    print xmin, xmax, ymin, ymax
    print abs(xmin - xmax), abs(ymin - ymax)
    
    offset_x,offset_y = 0,0
    if xmin<0:
        offset_x = -xmin
    if ymin <0:
        offset_y = -ymin    
    
    t_x,t_y = t.center()
    poly_util.redraw(t, t_x+offset_x, t_y+offset_y)
    q_x,q_y = q.center()
    poly_util.redraw(q, q_x+offset_x, q_y+offset_y)
    
    print 'q bounding'
    qxmin, qxmax, qymin, qymax = q.boundingBox()
    print qxmin, qxmax, qymin, qymax
    
    print 't bounding'
    txmin, txmax, tymin, tymax = t.boundingBox()
    print txmin, txmax, tymin, tymax
    
    output = q + t

    base_im = Image.open('/home/codein/workspace3/artist/base.png')
    
    print 'output bounding'
    outputxmin, outputxmax, outputymin, outputymax = output.boundingBox()
    print  outputxmin, outputxmax, outputymin, outputymax
    base_width, base_height =  int(max((q_width+qymin),(t_width+tymin))), int(max((q_height+qxmin),(t_height+txmin)))
    base_im = base_im.resize((base_width, base_height))

    offset_y = int(base_height-qymin)
    q_box = (0,0,q_width,q_height)
    q_box_offset =  (int(0+qymin),int(0+qxmin),int(q_width+qymin),int(q_height+qxmin))    
 
    print '\n\nmove to',qxmin,  qymin, qxmax,qymax
    print 'qbox cut at%s'%str(q_box)
    print 'qbox paste at%s'%str(q_box_offset)
    q_region = q_im.crop(q_box)
    base_im.paste(q_region,q_box_offset,q_region)
    
    offset_y = int(base_height-tymin)
    t_box = (0,0,t_width,t_height)
    t_box_offset =  (int(0+tymin),int(0+txmin),int(t_width+tymin),int(t_height+txmin))    
    print '\n\nmove to',txmin,  tymin, txmax,tymax
    print 'tbox cut at%s'%str(t_box)
    print 'tbox paste at%s'%str(t_box_offset)
    t_region = t_im.crop(t_box)
    base_im.paste(t_region,t_box_offset,t_region)
    
    base_im.show()
    

    Polygon.IO.writeSVG('testb.svg', (output,))
    base_im.save("img2.png", "PNG")



    
if __name__ == "__main__":
    image_merge()






