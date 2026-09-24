from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import FastAPI, APIRouter, Depends, UploadFile
from models import ResponseSignal
import os
import re

class DataController (BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1024 ** 2 # to scale MBs to bytes
    
    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.settings.FILE_ALLOWED_EXTENSIONS:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORT.value
        
        if file.size > self.settings.FILE_MAX_SIZE*(self.size_scale):
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value
        
        return True, ResponseSignal.FILE_VALIDATE_SCUCCEDED.value
    
    def generate_unique_file_path(self, file_name: str, project_id: str):
        random_key = self.generate_random_string() # length = 12
        project_path = ProjectController.get_project_path(self, project_id)

        cleaned_file_name = self.get_clean_file_name(file_name)

        new_file_path = os.path.join(project_path, random_key + "_" + cleaned_file_name)

        # recheck so that the name does not exist
        while os.path.exists(new_file_path):
            random_key = self.generate_random_string() # length = 12
            new_file_path = os.path.join(project_path, random_key + "_" + cleaned_file_name)
        
        return new_file_path, random_key + "_" + cleaned_file_name

    def get_clean_file_name(self, file_name: str):
        cleaned_file_name = re.sub(r"[^\w.]", '', file_name.strip())
        cleaned_file_name = cleaned_file_name.replace(' ', '_')
        return cleaned_file_name