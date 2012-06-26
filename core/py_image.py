import ImageOps
import Image

class PyImage():
    
    def __init__(self,base_im,width,height):
        self.base_im=base_im
        self.base_width =width
        self.base_height=height
        self.base_im = self.base_im.resize((self.base_width, self.base_height))
    
    def paste(self,polygon,q_im):
        q=polygon
        qxmin, qxmax, qymin, qymax = q.boundingBox()
        q_width, q_height = q_im.size
        offset_y = int(self.base_height-qymin)
        q_box = (0,0,q_width,q_height)
        #offset for polygon q and orientation, since the output polygon is potted at a 90 rotated plane
        q_box_offset =  (int(0+qymin),int(0+qxmin),int(q_width+qymin),int(q_height+qxmin))    
     
    #    print '\n\nmove to',qxmin,  qymin, qxmax,qymax
    #    print 'qbox cut at%s'%str(q_box)
    #    print 'qbox paste at%s'%str(q_box_offset)
        q_region = q_im.crop(q_box)
        #cut the image from the original image and paste it at the offset location
        self.base_im.paste(q_region,q_box_offset,q_region)
        
                
    def show(self):
        self.base_im.show()    
    
    def save(self,path=''):
        self.base_im.save("%sPyImage_save.png" % path, "PNG")