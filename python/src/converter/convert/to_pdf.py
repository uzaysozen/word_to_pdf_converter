import pika, json, tempfile, os
from bson.objectid import ObjectId
import subprocess

def start(message, fs_word_files, fs_pdfs, channel):
    message = json.loads(message)

    # Create a temporary file for the Word document
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_word_file:
        temp_word_file.write(fs_word_files.get(ObjectId(message["word_fid"])).read())
        temp_word_file_path = temp_word_file.name
        print(f"Temporary Word file created: {temp_word_file_path}")

    try:
        # Create a temporary file for the PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf_file:
            temp_pdf_file_path = temp_pdf_file.name
            print(f"Temporary PDF file created: {temp_pdf_file_path}")

        # Use unoconv to convert the Word file to PDF
        command = ['unoconv', '-f', 'pdf', '-o', temp_pdf_file_path, temp_word_file_path]
        subprocess.run(command, check=True)
        print("Word to PDF conversion completed")

        # Read the PDF file
        with open(temp_pdf_file_path, "rb") as pdf_file:
            pdf_data = pdf_file.read()
            print("PDF file read")

        # Save the PDF file to MongoDB
        pdf_id = fs_pdfs.put(pdf_data)
        print(f"PDF file saved to MongoDB with ID: {pdf_id}")

        # Delete the temporary files
        os.remove(temp_word_file_path)
        os.remove(temp_pdf_file_path)
        print("Temporary files deleted")

        message["pdf_fid"] = str(pdf_id)

        try:
            channel.basic_publish(
                exchange="",
                routing_key=os.environ.get("PDF_QUEUE"),
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE, content_type='application/json')
            )
            print("Message published successfully")
        except Exception as err:
            fs_pdfs.delete(pdf_id)
            print("Failed to publish message", err)
            return "Failed to publish message"
    except subprocess.CalledProcessError as e:
        print(f"Error converting Word to PDF: {e}")
        return "Failed to convert Word to PDF"

    print("Conversion completed successfully")