import cv2
import numpy as np

def video_to_dionela_text_video(
    input_video_path,
    output_video_path="dionela_text_art.mp4",
    letters="DIONELA",
    downscale=0.1,
    cell_size=12,
    font_scale=0.4,
    thickness=1,
    background_threshold=None
):
    """
    Convert each frame of a video into a text-art frame using letters from 'letters'.
    The color of each letter is based on the pixel's BGR color in the original frame.
    The resulting frames are written to an output video file (e.g., MP4).

    Parameters
    ----------
    input_video_path : str
        Path to the input video file.
    output_video_path : str
        Path to the output video file (e.g. 'output.mp4').
    letters : str
        A string of letters to cycle through, e.g. "DIONELA".
    downscale : float
        Factor by which to shrink the original frame (for mapping pixels to text).
        e.g. 0.1 → 10% of original width/height.
    cell_size : int
        The size of each "cell" in the final output. Each downscaled pixel
        will become a cell_size×cell_size block where we draw one letter.
    font_scale : float
        The scale for cv2.putText.
    thickness : int
        The thickness for cv2.putText.
    background_threshold : tuple or None
        (B, G, R) threshold. If set, any pixel whose B, G, R are all <= threshold
        is treated as "background" and skipped (no letter drawn, cell remains black).
        e.g. (30,30,30) to skip near-dark pixels for a silhouette effect.
    """

    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video {input_video_path}")
        return

    # Get video properties
    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Compute new size after downscaling
    new_w = max(1, int(orig_w * downscale))
    new_h = max(1, int(orig_h * downscale))

    # The output video will have each "downscaled pixel" expanded to a cell of size cell_size x cell_size
    out_w = new_w * cell_size
    out_h = new_h * cell_size

    print(f"Original video size: {orig_w} x {orig_h}, total frames: {frame_count}")
    print(f"Downscaled to: {new_w} x {new_h}")
    print(f"Output text-art video size: {out_w} x {out_h}, FPS: {fps:.2f}")

    # Setup output video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 'mp4v' or 'XVID' etc.
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (out_w, out_h))

    font = cv2.FONT_HERSHEY_SIMPLEX
    letter_count = len(letters)
    frame_index = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # end of video

        frame_index += 1
        # Downscale the frame
        small_frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Create a black canvas for text-art frame
        text_frame = np.zeros((out_h, out_w, 3), dtype=np.uint8)

        # We'll cycle through letters in row-major order so that horizontally
        # adjacent cells also get sequential letters in "DIONELA"
        letter_index = 0

        for y in range(new_h):
            for x in range(new_w):
                b, g, r = small_frame[y, x]

                # If background_threshold is used, skip this pixel if it's "under" the threshold
                if background_threshold is not None:
                    th_b, th_g, th_r = background_threshold
                    if b <= th_b and g <= th_g and r <= th_r:
                        letter_index += 1
                        continue

                # The letter to draw
                letter = letters[letter_index % letter_count]
                letter_index += 1

                # The cell's top-left corner in the output image
                cell_x = x * cell_size
                cell_y = y * cell_size

                # Position to put the text (roughly centered in the cell)
                # Adjust offsets to taste
                text_x = cell_x + 2
                text_y = cell_y + cell_size - 2

                # Draw the letter with the color (BGR) from the pixel
                cv2.putText(
                    text_frame,
                    letter,
                    (text_x, text_y),
                    font,
                    font_scale,
                    (int(b), int(g), int(r)),  # OpenCV is BGR
                    thickness=thickness,
                    lineType=cv2.LINE_AA
                )

        # Write the generated text frame to output video
        out.write(text_frame)

        # Optional: show progress in console
        if frame_index % 10 == 0:
            print(f"Processing frame {frame_index}/{frame_count}", end='\r')

    print("\nDone processing frames.")
    cap.release()
    out.release()
    print("Output saved to:", output_video_path)


if __name__ == "__main__":
    """
    Example usage:
      python dionela_text_art.py
    (Make sure to install OpenCV first: pip install opencv-python)
    """
    input_path = "dionelavideo.mp4"  # Replace with your video file
    output_path = "dionela_text_art_output.mp4"

    video_to_dionela_text_video(
        input_video_path=input_path,
        output_video_path=output_path,
        letters="DIONELA",
        downscale=0.2,                # Adjust for performance/visual effect
        cell_size=12,                 # Each downscaled pixel becomes a 12×12 block in the final video
        font_scale=0.4,
        thickness=1,
        background_threshold=(30,30,30)  # e.g., skip near-dark to create silhouette. Set to None to disable
    )
