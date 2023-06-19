import sys
import re
import collections
import fitz  # PyMuPDF

def main(pdf_path):
    # Open the PDF
    doc = fitz.open(pdf_path)

    # Process each page
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        blocks = page.get_text("blocks")

        # Print the page number
        print(f"Page {page_number + 1}:")

        # Process each block
        for block in blocks:
            x, y, x1, y1 = block[:4]
            text = block[4]

            # Clean up the text
            text = re.sub(r'\s+', ' ', text).strip()

            # Print the location and text
            print(f"  ({x:.2f}, {y:.2f}, {x1:.2f}, {y1:.2f}): {text}")

        # Calculate the proportions of the text
        counter = collections.Counter(page.get_text())
        total_chars = sum(counter.values())

        print("\nText proportions:")
        for char, count in counter.most_common():
            if char.isalnum():
                proportion = count / total_chars
                print(f"  {char}: {proportion:.2%}")

        print("\n" + "-" * 40 + "\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} PDF_PATH")
        sys.exit(1)

    pdf_path = sys.argv[1]
    main(pdf_path)

