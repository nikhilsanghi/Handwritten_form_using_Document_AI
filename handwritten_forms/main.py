from google.cloud import documentai_v1 as documentai


def process_document(project_id: str, location: str,
                     processor_id: str, file_path: str,
                     mime_type: str) -> documentai.Document:
    # Creating the the document ai client
    documentai_client = documentai.DocumentProcessorServiceClient()

    resource_name = documentai_client.processor_path(
        project_id, location, processor_id)

    # loading the file into the memory
    with open(file_path, "rb") as image:
        image_content = image.read()

        # Loading the data into the object
        raw_document = documentai.RawDocument(
            content=image_content, mime_type=mime_type)

        request = documentai.ProcessRequest(
            name=resource_name, raw_document=raw_document)

        result = documentai_client.process_document(request=request)

        return result.document


def extract_form_data(document: documentai.Document):
    # creating empty list
    form_data = []

    # extracting the form data from the result page

    document_pages = document.pages

    for page in document_pages:
        for form_field in page.form_fields:
            # filter out the field names and process the text for extra spaces
            field_name = get_text(form_field.field_name, document)
            # confidence is the probability factor of how correct the text is.
            field_name_confidence = form_field.field_name.confidence

            # obtaining the field value
            field_value = get_text(form_field.field_value, document)

            # obtaining the field value confidence
            field_value_confidence = form_field.field_value.confidence

            #appending all the data together in the list
            form_data.append({
                'field_name': field_name,
                'field_value': field_value,
                'field_name_confidence': field_name_confidence,
                'field_value_confidence': field_value_confidence
            })

    return form_data


def get_text(doc_element: dict, document: documentai.Document) -> str:
    # empty string to store the response
    response = ""
    # for text in multiple lines, it is stored in different text segments after the processing, so it is required to \
    # make sure that allt he necessary lines are connected
    for segment in doc_element.text_anchor.text_segments:
        start_index = (
            int(segment.start_index)
            if segment in doc_element.text_anchor.text_segments
            else 0
        )
        end_index = int(segment.end_index)
        response += document.text[start_index:end_index]
    return trim_text(response)

# trimming all the unecessary line spaces
def trim_text(text: str):
    return text.strip().replace("\n", " ")

# print out the output in tabular format
def print_form_data(form_data: list):
    print(f"{'Field Name': >60} | {'Field Value': <60} | {'Name Confidence': ^15} | {'Value Confidence': ^16} |\n")

    for field in form_data:
        print(
            f"{field['field_name']: >60} | {field['field_value']: <60} | {field['field_name_confidence']: ^15.4f} | {field['field_value_confidence']: ^16.4f} |")


def main():
    # project id
    project_id = 'vertex-ai-projects'
    # location of the processor
    location = 'us'
    # processor id
    processor_id = 'b8958b0c5b8eaf81'

    # file to be tested
    file_path = 'input_files/form.pdf'

    # mime type of the file
    mime_type = 'application/pdf'

    document = process_document(project_id=project_id, location=location,
                                processor_id=processor_id, file_path=file_path,
                                mime_type=mime_type)
    form_data = extract_form_data(document)
    print_form_data(form_data)


if __name__ == '__main__':
    main()
