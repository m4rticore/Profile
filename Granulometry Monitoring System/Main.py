
#http://85.143.163.195:555/FL1UOB3j?container=mjpeg&stream=main
#Изображение с сайта в окно


import cv2

from ultralytics import YOLO

# Load the YOLO11 model
model = YOLO("AiModules/grana.pt")





# Open the video file
img = "Images/2.jpg"
cap = cv2.imread(img)

# Loop through the video frames
while 1:
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLO11 tracking on the frame, persisting tracks between frames
        results = model.predict(frame, line_width=2, max_det=5000,
                                save=True, show=False,imgsz=1440,show_labels=False,show_conf=False,show_boxes=True)
        # Visualize the results on the frame
        annotated_frame = results[0].plot()
        for result in results:
            boxes = result.boxes  # Boxes object for bounding box outputs
            print(boxes)
            masks = result.masks  # Masks object for segmentation masks outputs
            keypoints = result.keypoints  # Keypoints object for pose outputs
            probs = result.probs  # Probs object for classification outputs
            obb = result.obb  # Oriented boxes object for OBB outputs
            result.save(filename="result.jpg")  # save to disk

        cv2.imshow("YOLO11 Tracking", frame)
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()

