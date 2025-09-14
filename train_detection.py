from sqlalchemy.orm.path_registry import path_is_entity
from ultralytics import YOLO

model = YOLO("yolo11n.pt")
dataset = {
    "location": "/home/vbatecan/Projects/medicine-storage-system/datasets/medicine-detection-6"
}


def train():
    result = model.train(
        data=dataset["location"] + "/data.yaml",
        epochs=200,
        imgsz=640,
        batch=-1,
        patience=75,
        name="medicine-detection-yolov11n"
    )

    val = model.val()
    e_val = model.eval()



if __name__ == "__main__":
    train()
