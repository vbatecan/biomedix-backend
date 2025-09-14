import ultralytics


class TrainingService:
    def __init__(self, model: str, epochs=100, device: str = 'cpu'):
        self.model = model
        self.epochs = epochs
        self.device = device
