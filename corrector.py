import getopt
import os
import sys

import cv2
import numpy as np
from matplotlib import pyplot as plt

from pdf2image import convert_from_path

image_path = 'static/pdf2image.jpg'
questions_coordinates = 'static/template.txt'

class File:
   def __init__(self, filename):
      self.fileName = filename

   def pdfToImage(self):
      provas = convert_from_path(self.fileName, 100)
      images = MultipleImages(provas)
      return images

   def readline(self):
      return self.fileName.readline()
   def openFileToWrite(self):
      self.fileName = open(self.fileName, 'w')
   def openFileToRead(self):
      self.fileName = open(self.fileName, 'r')

   def saveQuestion(self, templateAnswers):
      self.fileName.write(templateAnswers.getTestGrade())
      self.fileName.write(", ")
      for question in templateAnswers.getMarkedQuestions():
         self.fileName.write(question.getFormatedQuestion())
         self.fileName.write(", ")
      self.fileName.write("\n")
   
   def closeFile(self):
      self.fileName.close()

   def handleError(self):
      self.fileName.write("Unable to process image\n") 
      

   def getFileName(self):
      return self.fileName

class MultipleImages:
   def __init__(self, images):
      self.multipleImages = []
      for image in images:
         image = Image(image)
         self.addImage(image)

   def addImage(self, image):
      self.multipleImages.append(image)

   def getMultipleImages(self):
      return self.multipleImages

class Image:
   def __init__(self, image):
      image.save(image_path, 'JPEG')
      self.image = cv2.imread(image_path)

   def showImage (self):
      cv2.imshow("Teste", self.image)
      cv2.waitKey(0)

   def preProcessImage (self):
      # load the image, convert it to grayscale
      img_grey = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
      # CLAHE (Contrast Limited Adaptive Histogram Equalization) 
      clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
      img_grey = clahe.apply(img_grey)
      # Blur
      img_grey = cv2.medianBlur(img_grey,3) 
      # threshold the image
      thresh = cv2.adaptiveThreshold(img_grey, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 75, 10)
      thresh = cv2.bitwise_not(thresh)
      self.image = thresh

   def findContours(self):
      contours, hierarchy = cv2.findContours(self.image,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
      return contours

   def drawAlternativesContours(self):
      contours = self.findContours()
      for contour in contours:
         epsilon = 0.01*cv2.arcLength(contour,True)
         poly_pts = cv2.approxPolyDP(contour,epsilon,True)
         x,y,width,height = cv2.boundingRect(poly_pts)
         cv2.rectangle(self.image,(x+3,y+3),(x+width-3,y+height-3),(0,0,0),6)

   def extractTemplateRectangle(self):   
      #Find contour of the biggest rectangle
      contours = self.findContours()
      templateRectangle = max(contours, key=cv2.contourArea)
      
      ## Stract the polygon points
      epsilonCurve = 0.01*cv2.arcLength(templateRectangle,True)
      polygonExternalPoints = cv2.approxPolyDP(templateRectangle,epsilonCurve,True)

      self.cutImage(polygonExternalPoints)
      
   def cutImage(self, polygonExternalPoints):
      # Define the corners of the target rectangle
      width, height = 608, 1080
      cutOutPoints = np.zeros(polygonExternalPoints.shape, dtype=np.float32)
      cutOutPoints[0] = (0, 0)
      cutOutPoints[1] = (0, height)
      cutOutPoints[2] = (width, height)
      cutOutPoints[3] = (width, 0)

      transformationMatrix = cv2.getPerspectiveTransform(polygonExternalPoints.astype(np.float32), cutOutPoints)

      # Apply perspective transformation  
      rectangleImage = cv2.warpPerspective(self.image, transformationMatrix, (width,height))
      
      self.image = rectangleImage   

   def getImage(self):
      return self.image

class Question:
   questionWidth = 28
   questionHeight = 18

   def __init__(self, number, questionLetter):
      self.questionNumber = number
      self.questionLetter = questionLetter
      

   def getFormatedQuestion(self):
      return str(self.questionNumber+1)+str(":")+str(self.questionLetter)

class Template:
   def __init__(self, image):
      self.markedQuestions = []
      self.templateImage = image
      self.grade = 0

   def getMarkedQuestions(self):
      return self.markedQuestions

   def setMarkedQuestions(self, numberOfQuestions): 
      minPixelsToValidate = 60
      with open(questions_coordinates) as f :
         for questionInPage in range(numberOfQuestions) :
            markedQuestionLocation = -1
            lastMostPainted = 0
            for j in range(5) :
               line = f.readline() 
               paintedPixelsTotal = 0
               for number in self.verifyQuestionPixels(line):
                  paintedPixelsTotal += number
               if (paintedPixelsTotal>minPixelsToValidate):
                  if (paintedPixelsTotal > lastMostPainted):
                     lastMostPainted = paintedPixelsTotal
                     markedQuestionLocation = j
            question = Question(questionInPage, self.getQuestionLetter(markedQuestionLocation))
            self.markedQuestions.append(question)
            f.readline()

   def getQuestionLetter(self, markedPlace):
      if(markedPlace==0):
         questaoMarcada = "A"
      elif(markedPlace==1):
         questaoMarcada = "B"
      elif(markedPlace==2):
         questaoMarcada = "C"
      elif(markedPlace==3):
         questaoMarcada = "D"
      elif(markedPlace==4):
         questaoMarcada = "E"
      else:
         questaoMarcada = "N"
      return questaoMarcada
  
   def verifyQuestionPixels(self, line):
      upsideLeftX,upsideLeftY = eval(line)
      verifiedQuestionPixels = self.templateImage.getImage()[upsideLeftY:upsideLeftY+Question.questionHeight, upsideLeftX:upsideLeftX+Question.questionWidth]
      verifiedQuestionPixels = np.count_nonzero(verifiedQuestionPixels, axis=1)
      return verifiedQuestionPixels.tolist()

   def getTestGrade(self):
      return str(round(self.grade,2))

   def compareTemplateWithAnswers(self, position, rightAnswers):
      return (self.getMarkedQuestions()[position]==rightAnswers.getTestRightAnswers()[position])
      
   def setTestGrade(self, rightAnswers):
      numberOfQuestions = len(rightAnswers.getTestRightAnswers())
      pointsForEachQuestion = (10 / numberOfQuestions)

      for position in range(numberOfQuestions):
         if (self.compareTemplateWithAnswers(position, rightAnswers)):
            self.grade += pointsForEachQuestion

   def resolveTemplate(self, outputfile, rightAnswers):
      self.templateImage.preProcessImage()
      self.templateImage.extractTemplateRectangle()
      self.templateImage.drawAlternativesContours()
      self.setMarkedQuestions(len(rightAnswers.getTestRightAnswers()))
      self.setTestGrade(rightAnswers)
      outputfile.saveQuestion(self)

class RightAnswers:
   def __init__(self, rightAnswers):
      self.testRightAnswers = rightAnswers
   
   def getTestRightAnswers(self):
      return self.testRightAnswers

def main(inputfile, answers):
   outputfile = 'static/output.csv'

   print('Input file is ', inputfile)
   print('Output file is ', outputfile)

   inputfile = File('input/'+inputfile)
   outputfile = File(outputfile)
   outputfile.openFileToWrite()

   testRightAnswers = RightAnswers(answers)

   if inputfile.getFileName()[-4:] == ".pdf" :
      images = inputfile.pdfToImage()
      for image in images.getMultipleImages():
         try:
            templateAnswers = Template(image)
            templateAnswers.resolveTemplate(outputfile,testRightAnswers)
         except:   
            outputfile.handleError()
   else :
      try:
         image = Image(inputfile)
         templateAnswers = Template(image)
         templateAnswers.resolveTemplate(outputfile, rightAnswers)
      except:
         outputfile.handleError()
   outputfile.closeFile()
