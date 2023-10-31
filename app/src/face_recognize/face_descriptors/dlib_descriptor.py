import os

import cv2
import dlib
import numpy as np
from PIL import Image

"""
PRE-PROCESSING
"""

face_detector = dlib.get_frontal_face_detector()

point_detector = dlib.shape_predictor(
    'data/Weights/shape_predictor_68_face_landmarks.dat')

face_descriptor_extractor = dlib.face_recognition_model_v1(
    'data/Weights/dlib_face_recognition_resnet_model_v1.dat')

index = {}
idx = 0
face_descriptors = None
paths = [os.path.join('data/Datasets/yalefaces/train', f)
         for f in os.listdir('data/Datasets/yalefaces/train')]

"""
FACE DESCRIPTIONS
"""
for path in paths:
    image = Image.open(path).convert('RGB')
    image_np = np.array(image, 'uint8')

    detec = face_detector(image_np, 1)
    for face in detec:
        l, t, r, b = face.left(),  face.top(), face.right(), face.bottom()
        cv2.rectangle(image_np, (l, t), (r, b), (0, 255, 0), 1)

        points = point_detector(image_np, face)

        for point in points.parts():
            cv2.circle(image_np, (point.x, point.y), 2, (0, 255, 255), 1)

        face_descriptor = face_descriptor_extractor.compute_face_descriptor(
            image_np, points)
        face_descriptor = [f for f in face_descriptor]
        face_descriptor = np.asarray(face_descriptor, dtype=np.float64)
        face_descriptor = face_descriptor[np.newaxis, :]

        if (face_descriptors is None):
            face_descriptors = face_descriptor
        else:
            face_descriptors = np.concatenate((
                face_descriptors, face_descriptor), axis=0)

    index[idx] = path
    idx += 1

"""
TEST DISTANCE BETWEEN FACES
"""
face_descriptors[131]

# calculate the distance between vectors or similarities
# if sim --> 0 = more similar

sim = np.linalg.norm(face_descriptors[131] - face_descriptors[1:], axis=1)
less_d = np.argmin(sim)
print(less_d)

"""
FACE DETECTION
"""
min_confidance = 0.5

paths = [os.path.join('data/Datasets/yalefaces/test', f)
         for f in os.listdir('data/Datasets/yalefaces/test')]

for path in paths:
    image = np.array(Image.open(path).convert('RGB'), 'uint8')

    detections = face_detector(image, 1)

    for face in detections:
        points = point_detector(image, face)
        face_descriptor = face_descriptor_extractor.compute_face_descriptor(
            image, points)

        # converting to list
        face_descriptor = [f for f in face_descriptor]

        # transforming to np array
        face_descriptor = np.asarray(face_descriptor, dtype=np.float64)

        # add new axis
        face_descriptor = face_descriptor[np.newaxis, :]

        distance = np.linalg.norm(face_descriptor - face_descriptors, axis=1)
        min_index = np.argmin(distance)
        min_distance = distance[min_index]

        if (min_distance <= min_confidance):
            pred_name = int(os.path.split(index[min_index])[
                            1].split('.')[0].replace('subject', ''))
        else:
            pred_name = None

        real_name = int(os.path.split(index[min_index])[
            1].split('.')[0].replace('subject', ''))

        cv2.putText(image, 'Pred: ' + str(pred_name), (10, 30),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0))
        cv2.putText(image, 'Exp: ' + str(real_name), (10, 50),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0))

        cv2.imshow("img", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
