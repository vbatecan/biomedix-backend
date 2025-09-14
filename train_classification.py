from ultralytics import YOLO

model = YOLO("yolo11n-cls.pt")
dataset = {
    "location": "/home/vbatecan/Projects/medicine-storage-system/datasets/medicine-detection-classification-3"
}


def train():
    result = model.train(
        data=dataset["location"],
        epochs=100,
        imgsz=128,
        batch=-1,
        patience=50,
        name="medicine-classification"
    )
    model.export("onnx")
    model.export("tfjs")

    val = model.val()
    e_val = model.eval()


if __name__ == "__main__":
    train()
