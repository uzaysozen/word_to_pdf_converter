import pika, json, tempfile, os
from bson.objectid import ObjectId
from docx2pdf import convert
import PyPDF2


def start(message, fs_word_files, fs_pdfs, channel):
    message = json.loads(message)
    
    # Create a temporary file for the PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    # word contents
    doc = fs_word_files.get(ObjectId(message["word_fid"]))
    
    # Use the docx2pdf module to convert the Word file to PDF
    pdf_file = convert(doc)

    # Open the PDF file and the temporary file
    with open(pdf_file, 'rb') as pdf, open(temp_file.name, 'wb') as temp:
        # Use PyPDF2 to read the PDF and write it to the temporary file
        reader = PyPDF2.PdfFileReader(pdf)
        writer = PyPDF2.PdfFileWriter()
        writer.addPage(reader.getPage(0))
        writer.write(temp)

    # Close the files and delete the PDF file
    pdf.close()
    temp.close()
    os.remove(pdf_file)

    # The PDF file is now saved to a temporary file, which can be accessed using temp_file.name
    print('PDF file saved to', temp_file.name)
    
    with open(temp_file.name, 'rb') as file:
        # Store the file in GridFS
        pdf_id = fs_pdfs.put(file, filename=f"{message['word_fid']}.pdf")
        os.remove(temp_file.name)
        # Print the ID of the uploaded file
        print("PDF file uploaded with ID:", pdf_id)
        
    message["pdf_fid"] = str(pdf_id)
    
    try: 
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("PDF_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                pika.spec.PERSISTENT_DELIVERY_MODE
                )
        )
    except Exception as err:
        fs_pdfs.delete(pdf_id)
        return "failed to publish message"
        
    
    
   
    