import cv2
import numpy as np

def video_to_dionela_text_video_horizontal(
    input_video_path,
    output_video_path="dionela_text_art_horizontal.mp4",
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
    Unlike the 'global cycle' version, this code repeats 'letters' horizontally on each row.
    That is, each row restarts at letters[0].
    
    Parameters
    ----------
    input_video_path : str
        Path to the input video file.
    output_video_path : str
        Path to the output video file (e.g. 'output.mp4').
    letters : str
        A string of letters to cycle through horizontally, e.g. "DIONELA".
    downscale : float
        Factor by which to shrink the original frame before mapping pixels to text cells.
    cell_size : int
        The size of each "cell" in the final output. Each downscaled pixel
        becomes a cell_size×cell_size block where we draw one letter.
    font_scale : float
        The font scale for cv2.putText.
    thickness : int
        The thickness for cv2.putText.
    background_threshold : tuple or None
        (B, G, R) threshold. If set, any pixel whose B, G, R are all <= that threshold
        is treated as "background" and skipped (the cell remains black).
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

    # The output video will have each downscaled pixel expanded to a cell of size cell_size x cell_size
    out_w = new_w * cell_size
    out_h = new_h * cell_size

    print(f"Original video size: {orig_w} x {orig_h}, total frames: {frame_count}")
    print(f"Downscaled to: {new_w} x {new_h}")
    print(f"Output text-art video size: {out_w} x {out_h}, FPS: {fps:.2f}")

    # Setup output video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or 'XVID', 'H264', etc.
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

        for y in range(new_h):
            for x in range(new_w):
                b, g, r = small_frame[y, x]

                # If using background threshold, skip near-dark (or near some color) pixels
                if background_threshold is not None:
                    th_b, th_g, th_r = background_threshold
                    if b <= th_b and g <= th_g and r <= th_r:
                        # Don't draw a letter (i.e., cell remains black)
                        continue

                # Choose the letter based on the column only
                # Each row restarts the cycle at letters[0]
                letter = letters[x % letter_count]

                # Calculate the cell's top-left corner in the output image
                cell_x = x * cell_size
                cell_y = y * cell_size

                # Position to put the text (roughly near the bottom-left of each cell)
                text_x = cell_x + 2
                text_y = cell_y + cell_size - 2

                # Draw the letter with the BGR color from the pixel
                cv2.putText(
                    text_frame,
                    letter,
                    (text_x, text_y),
                    font,
                    font_scale,
                    (int(b), int(g), int(r)),
                    thickness=thickness,
                    lineType=cv2.LINE_AA
                )

        out.write(text_frame)

        if frame_index % 10 == 0:
            print(f"Processing frame {frame_index}/{frame_count}", end='\r')

    cap.release()
    out.release()
    print("\nDone processing frames.")
    print("Output saved to:", output_video_path)


if __name__ == "__main__":
    # Example usage:
    input_path = "dionelavideo.mp4"  # your video
    output_path = "dionela_text_art_horizontal_repeat.mp4"
    video_to_dionela_text_video_horizontal(
        input_video_path=input_path,
        output_video_path=output_path,
        letters="DIONELA",
        downscale=0.2,       # adjust based on performance and desired resolution
        cell_size=12,        # each "pixel" becomes a 12x12 cell
        font_scale=0.4,
        thickness=1,
        background_threshold=(30, 30, 30)  # skip near-dark for silhouette effect; set None to disable
    )
