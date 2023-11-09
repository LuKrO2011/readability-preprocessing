import os
from tempfile import TemporaryDirectory

from src.readability_preprocessing.utils.utils import load_code
from src.readability_preprocessing.preprocessing.visual import code_to_image

RES_DIR = os.path.join(os.path.dirname(__file__), "../../res/")
CODE_DIR = RES_DIR + "code_snippets/"


def test_code_to_image():
    # Create temporary directory
    temp_dir = TemporaryDirectory()
    output_file = os.path.join(temp_dir.name, "out.png")

    # Load the code
    filename = "AreaShop/AddCommand.java/execute.java"

    # Load the code
    code = load_code(CODE_DIR + filename)

    # Convert the code to an image
    code_to_image(code, output=output_file)

    # Check if the image was created successfully
    assert os.path.exists(output_file)

    # # Show the image
    # from PIL import Image
    # img = Image.open(output_file)
    # img.show()

    # Clean up temporary directories
    temp_dir.cleanup()


def test_code_to_image_towards():
    # Create temporary directory
    temp_dir = TemporaryDirectory()
    output_file = os.path.join(temp_dir.name, "out.png")

    # Load the code
    filename = "towards.java"

    # Load the code
    code = load_code(CODE_DIR + filename)

    # Convert the code to an image
    code_to_image(code, output=output_file)

    # Check if the image was created successfully
    assert os.path.exists(output_file)

    # # Show the image
    # from PIL import Image
    # img = Image.open(output_file)
    # img.show()

    # Clean up temporary directories
    temp_dir.cleanup()
