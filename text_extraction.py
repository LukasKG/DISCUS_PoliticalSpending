from pdf2image import convert_from_path
from PIL import Image
from pytesseract import pytesseract
import pandas as pd
import os

# load csv, saved locally, obtained from the website

data_full = pd.read_csv('spending_2019.csv')
data = data_full.iloc[:,[0,1,3,4,5,7, 15]] # only relevant columns

# rename invoice_id column
data['invoice_id'] = data['RedactedSupportingInvoiceId']
data.pop('RedactedSupportingInvoiceId')

# change invoices_trial to invoices
invoice_directory = 'C:/Users/Helena/DISCUS_polspending/DISCUS_Hack_PoliticalSpending/invoices'

# print("Files and directories in a specified path:")

for filename in os.listdir(invoice_directory):
    f = os.path.join(invoice_directory, filename)
    if os.path.isfile(f):
        # print(f)

        pdfs = f
        pages = convert_from_path(pdfs, 350)

        i = 1
        invoice_id = f[-9:-4]
        # print('invoice no.' + invoice_id + 'converted and saved')

        for page in pages:
            image_name = invoice_id + "_Page_" + str(i) + ".jpg"
            page.save('images/' + image_name, "JPEG")
            i = i + 1

print('all pdfs converted to images')

# extracting text from images

images_directory = 'C:/Users/Helena/DISCUS_polspending/DISCUS_Hack_PoliticalSpending/images'
path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

dict_invoices = {'invoice_id': [], 'text': []}

# print("Files and directories in a specified path:")

for filename in os.listdir(images_directory):

    f = os.path.join(images_directory, filename)
    if os.path.isfile(f):
        # print(f)

        image_path = f

        img = Image.open(image_path)
        pytesseract.tesseract_cmd = path_to_tesseract

        invoice_no = image_path[-16:-11]

        text = pytesseract.image_to_string(img)

        # text needs to be appended to a dictionary: key = invoice_id, all pages are text

        dict_invoices["invoice_id"].append(invoice_no)
        dict_invoices["text"].append(text)

#         print('invoice_no.:'+ invoice_no + '\n********************\n'+text +'\n\n')


print('all text extracted and saved in a dictionary')


# creating a dataframe

invoice_info_df = pd.DataFrame(data = dict_invoices)

# change invoice_id type from string to numeric - necessary for merging later

invoice_info_df['invoice_id'] = invoice_info_df['invoice_id'].apply(pd.to_numeric)

# merge data and invoice_data on invoice_id variable

data_final = data.merge(invoice_info_df, left_on='invoice_id', right_on ='invoice_id')

data_final.head()

data_final.to_csv('data_incl_ExtractedText.csv')