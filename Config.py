import os
from comfig import*

class Config(object):
      def __init__(self):
          self.ChunkSize = (PARTES_MB)
          self.up_zip = False
          self.url = ''
          self.subiendo = 'No'
          self.descargado = 0
          self.links = []
          self.name = ''
          self.user = (MOODLE_USER)
          self.password = (MOODLE_PASSWORD)

      def setChunkSize(self,chunk : int):
          self.ChunkSize = chunk

