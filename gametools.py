import cv2
import numpy
import random
import time
class GameTable():

    def __init__(self,height,width):
        self.window_height = height
        self.window_width = width
        self.window_center = (height//2, width//2)

            
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.window_width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT,self.window_height)
        

        self.score_table_x = self.window_height - 175
        self.score_table_y = 40
        self.score_table_color = (0,255,0)
        self.score_table_thickness = 2
        self.score_table_font_size = 1
        self.score = 0
        self.false = 0
        
        self.energy_limit = 10
        self.energy = 60

        self.center_line_color = (255,0,0)
        self.center_line_thickness = 3

        self.tracker = cv2.TrackerCSRT_create()
        

    def run(self):
        self.findHand()
        self.is_run = True
        self.pickTargetSide()
        while self.is_run:
            ret, self.frame = self.camera.read()
            
            pressed_key = cv2.waitKey(1)
            self.keyAction(pressed_key)
            self.update(self.frame)
            cv2.imshow('Oyun Ekrani', self.frame)
        gameover_screen = numpy.zeros_like(self.frame)
  
        gameover_screen = cv2.putText(gameover_screen,
            'Game Over'.format(self.score),
            (self.window_height//2-50, self.window_width//2-50),
            cv2.FONT_HERSHEY_SIMPLEX,
            self.score_table_font_size,
            self.score_table_color,
            self.score_table_thickness,
            cv2.LINE_AA)

        gameover_screen = cv2.putText(gameover_screen,
            'Socre: {}'.format(self.score),
            (self.window_height//2-50, self.window_width//2),
            cv2.FONT_HERSHEY_SIMPLEX,
            self.score_table_font_size,
            self.score_table_color,
            self.score_table_thickness,
            cv2.LINE_AA)
        
        cv2.imshow('Oyun Ekrani',gameover_screen)
        self.camera.release()
        key = cv2.waitKey(0)
        self.keyAction(key)
    def update(self,frame):
        t1 = time.time()
        self.drawHandRectangle(frame)
        self.scoreTable(frame)
        self.drawCenterLine(frame)
        self.paintTargetSide(frame)s
        t2 = time.time()
        fps = self.calculateFPS(t1,t2)
        self.drawRemainingEnergy(frame)
        self.drawFPS(frame,fps)
        self.calculateScore()
        
    def updateEnergy(self):
        if not self.energy<self.energy_limit:
            self.energy-=1
    def drawRemainingEnergy(self, frame):
        self.frame = cv2.putText(frame,
            'Remaining Energy: {:.0f}'.format(self.energy),
            (25 , self.score_table_y+35),
            cv2.FONT_HERSHEY_SIMPLEX,
            self.score_table_font_size,
            self.score_table_color,
            self.score_table_thickness,
            cv2.LINE_AA)
    def drawFPS(self,frame,fps):
        self.frame = cv2.putText(frame,
            'FPS: {}'.format(fps),
            (self.score_table_x , self.score_table_y+35),
            cv2.FONT_HERSHEY_SIMPLEX,
            self.score_table_font_size,
            self.score_table_color,
            self.score_table_thickness,
            cv2.LINE_AA)
    def drawHandRectangle(self,frame):
        (success, self.hand_box) = self.tracker.update(self.frame)
        if success:
            (x, y, w, h) = [int(v) for v in self.hand_box]
            cv2.rectangle(self.frame, (x, y), (x + w, y + h),
                            (0, 255,  0), 2)
            
    def findHand(self):

        while True:
            self.ret, self.frame = self.camera.read()
            cv2.imshow('Eli Bul', self.frame)
            pressed_key = cv2.waitKey(1)
            if pressed_key == ord('s'):
                self.hand_box = cv2.selectROI('Eli Bul', self.frame, fromCenter = False)
                if sum(self.hand_box):
                    self.tracker.init(self.frame, self.hand_box)
                    cv2.destroyAllWindows()
                    break
    def pickTargetSide(self):

        self.side_points = random.choice([(0,0,self.window_height,self.window_center[0])
                              ,(0,self.window_center[0],self.window_width,self.window_height)])

        
    def paintTargetSide(self,frame):
        
        self.frame[self.side_points[0]:self.side_points[2],
                   self.side_points[1]:self.side_points[3],:] = self.frame[self.side_points[0]:self.side_points[2],
                                                                           self.side_points[1]:self.side_points[3],:]*0.5 + (0,127,0)
        
    def scoreTable(self,frame):
        
        cv2.putText(frame,
                    'Skor: {}'.format(self.score),
                    (self.score_table_x, self.score_table_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    self.score_table_font_size,
                    self.score_table_color,
                    self.score_table_thickness,
                    cv2.LINE_AA)
    def calculateScore(self):
        self.energy -= self.false/(1+self.fps)
        if self.calculateOverlap() > 0:
            self.score+=1
            self.pickTargetSide()
            self.false = 0
            self.updateEnergy()
        else:
            
            self.false+=1
        if self.energy<0:
            self.gameOver()

    def gameOver(self):
        self.is_run = False
        
        
    def drawCenterLine(self,frame):
        cv2.line(frame, (self.window_center[0],0),
                 (self.window_center[0],self.window_height),
                 self.center_line_color,
                 self.center_line_thickness)
    def calculateOverlap(self):
        dx1 = self.hand_box[0] - self.side_points[1]
        dx2 = self.side_points[3] - self.hand_box[0] - self.hand_box[2]
       
        return dx1*dx2
    def calculateFPS(self,t1,t2):
        self.fps = 1/(t2 - t1)
        return self.fps
    def keyAction(self,key):

        if key == ord('q'):
            self.is_run = False
            cv2.destroyAllWindows()
