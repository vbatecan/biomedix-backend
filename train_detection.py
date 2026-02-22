from sqlalchemy.orm.path_registry import path_is_entity
from ultralytics import YOLO

model = YOLO("yolo11n.pt")
dataset = {
    "location": "/home/nytri/Projects/biomedix/biomedix-backend/datasets/medicine-detection-9"
}


def tune():
    search_space = {
        "lr0": (1e-5, 1e-1),
        "degrees": (0.0, 45.0),
        "translate": (0.0, 0.5),
        "scale": (0.5, 1.5),
        "shear": (0.0, 10.0),
        "perspective": (0.0, 0.001),
        "flipud": (0.0, 1.0),
        "fliplr": (0.0, 1.0),
        "mosaic": (0.0, 1.0),
        "mixup": (0.0, 1.0),
        "copy_paste": (0.0, 1.0),
        "hsv_h": (0.0, 0.015),
        "hsv_s": (0.0, 0.7),
        "hsv_v": (0.0, 0.4),
        "box": (0.02, 0.2),
        "cls": (0.0, 2.0),
    }

    result = model.tune(
        data=dataset["location"] + "/data.yaml",
        epochs=50,
        imgsz=800,
        batch=16,
        patience=20,
        space=search_space,
        name="medicine-detection-yolov11n-tune"
    )


def train():
    result = model.train(
        data=dataset["location"] + "/data.yaml",
        epochs=200,
        imgsz=800,
        batch=12,
        patience=16,
        optimizer="adamw",
        name="medicine-detection-yolov11n"
    )

    val = model.val()
    e_val = model.eval()


if __name__ == "__main__":
    # tune()
    train()
