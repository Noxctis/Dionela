import cv2
import time
import sys

def print_video_as_text(
    video_path,
    letters="DIONELA",
    downscale=0.1,
    fps_limit=None,
    background_threshold=None
):
    """
    Streams a video as colored text (using ANSI escape sequences) in your console.
    Each pixel is replaced by one letter from the repeating sequence in 'letters',
    colored by that pixel's BGR color.

    Parameters
    ----------
    video_path : str
        Path to the input video file.
    letters : str
        The string of letters to cycle through (e.g. 'DIONELA').
    downscale : float
        Resize factor for reducing the original frame width/height.
        e.g. 0.1 means 10% original size.
    fps_limit : float or None
        If set, will limit the displayed FPS to this value.  If None, uses video's FPS.
    background_threshold : tuple or None
        If set, treat near-black (or near this color) as “transparent”/space.
        Example: (10,10,10) – any pixel whose BGR is all <=10 is replaced with space.
        This is a simple approach to skip “background.” 
        For more advanced silhouette detection, see note below.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video:", video_path)
        return

    # Get original video FPS (used if fps_limit is None)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    if fps_limit is None:
        fps_limit = video_fps if video_fps > 0 else 25.0  # fallback

    # The time between frames to roughly maintain the chosen fps_limit
    frame_delay = 1.0 / fps_limit

    # Get original width/height
    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Compute scaled size
    new_w = max(1, int(orig_w * downscale))
    new_h = max(1, int(orig_h * downscale))

    print(f"Original size: {orig_w} x {orig_h}, scaled to: {new_w} x {new_h}")
    print(f"Video FPS: {video_fps:.2f}, displaying at ~{fps_limit:.2f} FPS")
    print("Press Ctrl+C to stop.\n")
    time.sleep(1)

    # For cycling letters
    letter_count = len(letters)
    global_letter_index = 0  # increment as we go across each pixel

    # We'll read frames in a loop
    last_time = time.time()
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break  # end of video

            # Resize the frame (downscale)
            small_frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

            # Move the cursor to top-left (so we overwrite the console output)
            # \033[H moves cursor to top-left; \033[J can clear screen below the cursor if you want
            # But clearing the whole screen each frame can flicker. We'll just move to top for overwriting.
            print("\033[H", end="")

            # Build the text output for this frame row by row
            text_lines = []
            for y in range(new_h):
                line_chars = []
                for x in range(new_w):
                    b, g, r = small_frame[y, x]

                    # OPTIONAL: skip background-like pixels if you want a "silhouette" effect
                    # e.g., if they're nearly black or below a certain threshold
                    if background_threshold is not None:
                        tb, tg, tr = background_threshold
                        if b <= tb and g <= tg and r <= tr:
                            # Use blank space (no letter) instead
                            line_chars.append(" ")
                            continue

                    # Choose the next letter in "DIONELA"
                    letter = letters[global_letter_index % letter_count]
                    global_letter_index += 1

                    # Construct the ANSI color code (foreground color)
                    # \033[38;2;R;G;B m  -- set truecolor text
                    color_code = f"\033[38;2;{r};{g};{b}m"
                    # Combine color code + letter + reset
                    # We won't reset after *every* letter, just after the line, for performance
                    line_chars.append(color_code + letter)
                
                # Reset color at the end of the line, then join
                text_lines.append("".join(line_chars) + "\033[0m")

            # Join all lines with newline
            frame_text = "\n".join(text_lines)

            # Print it in one go
            print(frame_text)

            # Wait enough to maintain fps_limit
            now = time.time()
            elapsed = now - last_time
            wait = frame_delay - elapsed
            if wait > 0:
                time.sleep(wait)
            last_time = time.time()

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        cap.release()
        print("Done.")


if __name__ == "__main__":
    """
    Example usage:
      1. Update the 'input_video.mp4' with your actual video file path.
      2. Run in a terminal that supports 24-bit ANSI color.
      3. Enjoy the text-art rendering. (Ctrl+C to quit)
    """
    input_video = "pmo.mp4"  # <-- replace with your video
    
    print_video_as_text(
        video_path=input_video,
        letters="DIONELA",
        downscale=0.1,          # Make this smaller or larger depending on your terminal size
        fps_limit=15,           # Try 10-15 for stability in the terminal
        background_threshold=(10,10,10)  # Treat near-black as "transparent" so it looks like a silhouette
    )
