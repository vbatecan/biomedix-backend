import os
import uuid

import albumentations as A
import cv2
import ultralytics

augmentor = A.Compose([
    # Orientation
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.2),

    # Realistic lighting conditions
    A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.6),
    A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.15, hue=0.05, p=0.4),

    # Blur & camera imperfections
    A.MotionBlur(blur_limit=3, p=0.3),  # simulate shaky hand
    A.GaussianBlur(blur_limit=(3, 5), p=0.3),  # out-of-focus
    A.GaussNoise(p=0.3),  # low-quality camera noise

    # Slight geometric variation (not too strong for pills/labels)
    A.Affine(
        shear=(-10, 10),
        p=0.3,
        fill_mask=False,
        border_mode=0,
    ),

    A.OpticalDistortion(distort_limit=0.05, p=0.3),
    A.Perspective(scale=(0.02, 0.05), p=0.3),

    # Standardize image size for training
    A.Resize(128, 128)
])


def augment_training_data(input_dir="uploads/training", output_dir="uploads/training_aug", n_aug=10):
    """
    Augment training images and save them into output_dir,
    preserving class folder structure.
    """
    # Remove existing augmented data if any
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    for class_name in os.listdir(input_dir):
        class_dir = os.path.join(input_dir, class_name)
        if not os.path.isdir(class_dir):
            continue

        out_class_dir = os.path.join(output_dir, class_name)
        os.makedirs(out_class_dir, exist_ok=True)

        print(f"🔄 Augmenting class: {class_name}")
        for filename in os.listdir(class_dir):
            file_path = os.path.join(class_dir, filename)

            # Read image
            image = cv2.imread(file_path)
            if image is None:
                continue

            # Apply augmentations multiple times
            for _ in range(n_aug):
                augmented = augmentor(image=image)
                aug_image = augmented["image"]

                # Save augmented image into output class folder
                aug_filename = f"{uuid.uuid4().hex}.jpg"
                aug_path = os.path.join(out_class_dir, aug_filename)
                cv2.imwrite(aug_path, aug_image)

        print(f"✅ Finished augmenting {class_name}")


def retrain_classification_model():
    model = ultralytics.YOLO("models/classification.pt")

    augment_training_data(input_dir="uploads/training", n_aug=20)

    data_path = 'uploads/training_aug'
    epochs = 75
    batch_size = 16

    model.train(
        data=data_path,
        epochs=epochs,
        batch=batch_size,
        imgsz=128,
        patience=10,
    )

    model.save('models/classification.pt')
