import cv2
import argparse

from ultralytics import YOLO
import supervision as sv
import numpy as np

ZONE_POLYGON = np.array([
    [0, 0],
    [1260 // 2, 0],
    [1280 // 2, 720],
    [0, 720]
])

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 live")
    parser.add_argument(
        "--webcam-resolution",
        default=[1280, 720],
        nargs=2,
        type=int
    )
    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()
    frame_width, frame_height = args.webcam_resolution

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    model = YOLO("model.pt")

    box_annotatar = sv.BoxAnnotator(
        thickness = 2,
        text_thickness = 2,
        text_scale = 1
    )

    zone = sv.PolygonZone(polygon=ZONE_POLYGON, frame_resolution_wh=tuple(args.webcam_resolution))
    zone_annotator = sv.PolygonZoneAnnotator(
        zone = zone,
        color = sv.Color.red(),
        thickness = 2,
        text_thickness = 4,
        text_scale = 1
    )

    while True:
        ret, frame = cap.read()

        result = model(frame)[0]
        #talvez essa esteja certa
        detections = sv.Detections.from_ultralytics(result)
        #detections = sv.Detections.from_yolov8(result)
        detections = detections[detections.class_id != 0]
        print("detections")
        for det in detections:
            print(det)
        labels = [
            f"{model.model.names[class_id]} {confidence:0.2f}"
            for _, _, confidence, class_id, _, _
            in detections
        ]

        frame = box_annotatar.annotate(
            scene=frame,
            detections=detections,
            labels=labels
        )
        zone.trigger(detections=detections)
        frame = zone_annotator.annotate(scene=frame)
        cv2.imshow("nome", frame)
        if cv2.waitKey(1) == ord('d'):
            break

if __name__ == "__main__":
    main()