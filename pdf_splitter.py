import logging
import os

import PyPDF2

logger = logging.getLogger(__name__)


def split_pdf(
    input_pdf_path: str, output_folder_path: str, pages_per_chunk: int = 1
) -> bool:
    """
    Splits a PDF file into multiple smaller PDF files, each containing a specified number of pages.

    Args:
        input_pdf_path (str): Path to the input PDF file.
        output_folder_path (str): Directory where the generated PDFs will be saved.
        pages_per_chunk (int, optional): Number of pages per output PDF file. Defaults to 1.

    Returns:
        bool: True if the process completed successfully, False otherwise.
    """
    try:
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)
            logger.info(f"Created folder: {output_folder_path}")

        with open(input_pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            logger.info(f"Total pages in the PDF: {total_pages}")

            for i in range(0, total_pages, pages_per_chunk):
                writer = PyPDF2.PdfWriter()

                for j in range(i, min(i + pages_per_chunk, total_pages)):
                    writer.add_page(reader.pages[j])

                output_filename = os.path.join(
                    output_folder_path, f"split_{(i // pages_per_chunk) + 1}.pdf"
                )
                with open(output_filename, "wb") as output_file:
                    writer.write(output_file)

                logger.info(f"Generated file: {output_filename}")

        return True
    except Exception as e:
        logger.error(f"Error splitting the PDF: {str(e)}")
        return False


# Example usage:
if __name__ == "__main__":
    # Input PDF file path (update as needed)
    test_pdf = "nombre_pdf.pdf"
    # Output folder where split files will be saved
    output_dir = "output"
    split_pdf(test_pdf, output_dir, pages_per_chunk=3)
