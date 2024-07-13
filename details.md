A GUI application written in Python using tkinter for creating a graphical user interface. It allows users to download images from URLs and view them within the application. Here's a breakdown of the functionalities:

**Classes:**

* **Util:** This class provides utility functions for:
    * Extracting filename and extension from a URL.
    * Listing files in a directory by their creation date.
* **Download:** This class handles image downloads:
    * Takes URL and destination path as input.
    * Allows setting a callback function for progress updates.
    * Downloads the image with progress bar and error handling.
* **MenuWindow:** This class represents the main window:
    * Creates UI elements like labels, buttons, and manages their states.
    * Provides methods for opening other child windows for various functionalities.
    * Loads image paths using the `Util` class.
* **EntradaWindow:** This class represents the child window for entering a URL to download an image:
    * Creates UI elements like labels, entry field, button, and message label.
    * Validates user input and calls the `Download` class for download.
    * Updates the message label based on the download status.
    * Disables the download button in the main window while processing.
    * Re-enables the button and closes itself upon successful download.
* **ViewAllImagesWindow:** This class represents a child window to display all downloaded images as thumbnails:
    * Lists image paths using the `Util` class.
    * Creates scrollable frames to display image thumbnails.
    * Uses PIL (Python Imaging Library) to load and resize images.
    * Binds buttons to each thumbnail to open the selected image in another window.
    * Disables the "Show All Images" button in the main window while processing.
    * Re-enables the button and closes itself upon closing the window.
* **WindowImageViewer:** This class represents a child window to display a single image:
    * Takes the image path and a reference to the main window as input.
    * Creates UI elements for displaying the image with scrollbars.
    * Uses PIL to load and display the image.
    * Handles potential errors if the image file doesn't exist.
    * Disables the "Show Last Image" button in the main window while processing.
    * Re-enables the button and closes itself upon closing the window.

**Main execution:**

1. **Import necessary libraries:**
   - tkinter for GUI creation
   - Your `gui` module containing the classes defined above
   - `ssl` for handling HTTPS connections (commented out for simplicity)

2. **Create the main window:**
   - Create a `tk.Tk()` instance for the main application window.
   - Instantiate the `MenuWindow` class, passing the main window and a title.

3. **Start the main event loop:**
   - Call `app.mainloop()` to start the GUI's main loop, which listens for user interactions and updates the window.
