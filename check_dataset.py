import os

def check_yolo_dataset(dataset_path):
    issues = False
    splits = ['train', 'valid']

    for split in splits:
        print(f"\nChecking '{split}' split:")
        img_dir = os.path.join(dataset_path, 'images', split)
        label_dir = os.path.join(dataset_path, 'labels', split)

        if not os.path.isdir(img_dir):
            print(f"❌ Image directory not found: {img_dir}")
            issues = True
            continue
        if not os.path.isdir(label_dir):
            print(f"❌ Label directory not found: {label_dir}")
            issues = True
            continue

        img_files = sorted([f for f in os.listdir(img_dir) if f.endswith(('.jpg', '.png', '.jpeg'))])
        label_files = sorted([f for f in os.listdir(label_dir) if f.endswith('.txt')])

        img_names = set(os.path.splitext(f)[0] for f in img_files)
        label_names = set(os.path.splitext(f)[0] for f in label_files)

        missing_labels = img_names - label_names
        missing_images = label_names - img_names

        if missing_labels:
            print(f"⚠️ Images with no matching labels: {sorted(missing_labels)}")
            issues = True
        if missing_images:
            print(f"⚠️ Labels with no matching images: {sorted(missing_images)}")
            issues = True

        if not missing_labels and not missing_images:
            print("✅ All images and labels match.")

    if not issues:
        print("\n✅ Dataset structure looks good!")
    else:
        print("\n⚠️ Dataset has issues. Please fix them before training.")

# Example usage
check_yolo_dataset("people_dataset")
