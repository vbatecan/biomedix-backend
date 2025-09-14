from roboflow import Roboflow

rf = Roboflow(api_key="LPBoQk8BkTKtnNQnaEl9")
project = rf.workspace("vbatecan").project("medicine-detection-ei8ns")
version = project.version(6)
dataset = version.download("yolov11")
classification_project = rf.workspace("vbatecan").project("medicine-detection-classification-exxxl")
classification_version = classification_project.version(3)
classification_dataset = classification_version.download("folder")
