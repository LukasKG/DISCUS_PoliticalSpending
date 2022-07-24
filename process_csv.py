import numpy as np
import os
import pandas as pd
   
in_path = 'data/raw'
out_path = 'data/processed'
    
df_t = pd.read_csv(os.path.join(in_path,'coding_transport.csv'), dtype="object", header = 1)
df_n = pd.read_csv(os.path.join(in_path,'coding_notransport.csv'), dtype="object", header = 1)

frames = []
for df in (df_t, df_n):
    # Remove empty columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Remove whitespaces
    df.columns = df.columns.str.strip()

    # Drop unneccesary columns
    df.drop(['Notes','More than 1 service','Supplier .1','Supplier.1','Missing invoices?'], axis=1, errors='ignore', inplace=True)
    
    # Rename for uniform names and clarity
    df.rename(columns = {
        'ADVERTISING AND PRESS': 'Advertising and Press',
        'Ambiguous and needs discussion': 'Ambiguous',
        'Campaign database or CRM (including SQL)': 'Campaign database or CRM',
        'Creative content owned by a third party (e.g. Getty images, PA images, demo music)': 'Creative content',
        'Event costs/ Production/ Venue hire': 'Event costs/Venue hire',
        'Office infrastructure and supplies': 'Office supplies',
        'Office supplies (staples, paperclips, IT equipment, envelopes)' : 'Office supplies',
        'Online advertising (i.e. web advertising but not online newspapers or social media)': 'Online advertising',
        'Online advertising (not social media,  i.e. web advertising but not online newspapers or social media)': 'Online advertising',
        'Other forms of advertising (billboards, advans, digital posters outside)': 'Other forms of advertising',
        'Direct Mail/ Leaflet delivery/ postage': 'Postage',
        'Paid leaflet delivery/ postage': 'Postage',
        'Video editing/ production': 'Video editing/production',
        
    }, inplace = True)
    
    frames.append(df)

print("\nUnique columns left:")
t,n = list(frames[0].columns),list(frames[1].columns)
for col in sorted(set(t+n)):
    if col in t and col in n:
        continue
    elif col in t:
        print("    Transport:",col)
    else:
        print("Non-Transport:",col)


df = pd.concat(frames, axis=0)

# Fill NaNs with '0'
df.fillna('0', inplace=True)

# Add ID column
df.insert(0, 'ID', [str(n) for n in range(len(df))])

'''
0 - ID
1 - Supplier
2 - Party
3 - Total Spend
4 - Expense Category
'''

# Convert string into float values
for col in ['Total Spend']+list(df.columns[5:]):
    df[col] = df[col].str.replace('£', '')
    df[col] = df[col].str.replace(',', '')
    df[col] = df[col].astype(float)


print("\nAll",len(df.columns),"column names:")
for col, col_type in zip(df.columns,df.dtypes):
    print("   NaNs" if df[col].isnull().values.any() else "No NaNs",col_type,col)

df_coding = df
df = None    



'''

 Invoice list

'''

# Open invoice list
df_invoice = pd.read_csv(os.path.join(in_path,'invoice_list.csv'))

# Drop entries w/o provided invoices
#df_invoice = df_invoice[df_invoice['RedactedSupportingInvoiceId'].notna()]
df_invoice['RedactedSupportingInvoiceId'] = df_invoice['RedactedSupportingInvoiceId'].fillna(0)

# Convert invoice ID to str
df_invoice['RedactedSupportingInvoiceId'] = df_invoice['RedactedSupportingInvoiceId'].astype(int).astype(str)

# Convert total spend to float
df_invoice['TotalExpenditure'] = df_invoice['TotalExpenditure'].str.replace('£', '')
df_invoice['TotalExpenditure'] = df_invoice['TotalExpenditure'].str.replace(',', '')
df_invoice['TotalExpenditure'] = df_invoice['TotalExpenditure'].astype(float)
    
print("\nInvoice column names:")
for col, col_type in zip(df_invoice.columns,df_invoice.dtypes):
    print("   NaNs" if df_invoice[col].isnull().values.any() else "No NaNs",col_type,col)

    
    
def print_sets(name,lst_coding,lst_invoice):
    print("\n"+name+" Coding:")
    for item in lst_coding:print(item)

    print("\n"+name+" Invoices:")
    for item in lst_invoice:print(item)

    print("\nUnique "+name+" left:")
    for item in sorted(set(lst_invoice+lst_coding)):
        if item in lst_invoice and item in lst_coding:
            continue
        print(" Coding:" if item in lst_coding else "Invoice:",item)

def replace_items(df,col_name,d):
    for k,v in d.items():
        df[col_name].replace(k,v,inplace=True)
        
'''
    ###################
       Handle Parties
    ###################
'''
d_party = {
    'Christian Party "Proclaiming Christ\'s Lordship"': 'Christian Party',
    'Co-operative Party': 'Co-op Party',
    'Conservative and Unionist Party': 'Conservative Party',
    'Conservatives ': 'Conservative Party',
    'Greens': 'Green Party',
    'Labour': 'Labour Party',
    'Plaid Cymru - The Party of Wales': 'Plaid Cymru',
    'Scottish National Party (SNP)': 'Scottish National Party',
    'Scottish Green Party': 'Green Party',
    'The Women\'sEquality Party': 'Womens Equality Party',
    'UK Independence Party (UKIP)': 'UKIP',
    'Women\'s Equality Party': 'Womens Equality Party',
}
replace_items(df_coding,col_name='Party',d=d_party)   
coding_parties = sorted(df_coding['Party'].unique())

replace_items(df_invoice,col_name='RegulatedEntityName',d=d_party)
invoice_parties = sorted(df_invoice['RegulatedEntityName'].unique())

print_sets(name='Parties',lst_coding=coding_parties,lst_invoice=invoice_parties)
    
        
'''
    ###################
       Handle Suppliers
    ###################
'''

# Remove "Limited" and "The "
for word in ['The ',' Limited',' limited',' Limitd',' LIMITED',' ltd',' ltD',' lTd',' lTD',' Ltd',' LTD',' LTd',' LtD',' Inc']:
    df_coding['Supplier'] = df_coding['Supplier'].str.replace(word,'')
    df_invoice['SupplierName'] = df_invoice['SupplierName'].str.replace(word,'')

# Remove Whitespaces
df_coding['Supplier'] = df_coding['Supplier'].str.strip()
df_invoice['SupplierName'] = df_invoice['SupplierName'].str.strip()



d_supplier = {
    'A.G.A Print t/a Solopress': 'AGA Print',
    'AGA Print t/a Solopress': 'AGA Print',

    'Airbnb Inc': 'Airbnb',
    'Airbnb Ireland UC': 'Airbnb',
    'Airbnb Payments UK': 'Airbnb',
    
    'Amazon UK': 'Amazon',
    'Amazon Services Europe 38 Avenue John F. Kennedy, L-1855, Luxemb': 'Amazon',
    
    'Bluetree Design & Print': 'Bluetree',
    'Bluetree Design & Print t/a Instantprint': 'Bluetree',
    'Bluetree Website Services': 'Bluetree',
    
    'Blueway Creative Media': 'Blueway',
    
    'British Airways plc': 'British Airways',
    'British Airways?Plc': 'British Airways',
    
    'Burgoynes (Lyonshall)': 'Burgoynes',
    
    'Cardiff Bay Print': 'Cardiff Bay Printing',

    'Cameraworks': 'Camera Works',
    
    'cheapest print online': 'Cheapestprintonline',
    
    'Co-Operative Group': 'Co-op',
    'Co-operative Business Consultants': 'Co-op',
    
    'DC Thomsom & Co': 'DC Thomson & Co',
    
    'deliveroo': 'Deliveroo',
    
    'D X G Media': 'DXG Media',
    'DGX Media': 'DXG Media',

    'easyjet': 'Easyjet',
    'easyJet Airline Company': 'Easyjet',
    
    'Enterprise Rent-A-Car UK': 'Enterprise',
    
    'Eurocar': 'Europcar',
    'Europ Car': 'Europcar',
    
    'Facebook Ireland': 'Facebook',
    'Facebook UK': 'Facebook',

    'Field Media Strategy': 'Field Media',
    
    'Fullpoint Communications': 'Full Point Communications',

    'Getty Images International': 'Getty Images',
    'Getty Images-': 'Getty Images',
    
    'GOOGLE UK': 'Google',
    'Google Ireland': 'Google',

    'Hamilton Hotel': 'Hamilton',
    'Hamilton Rentals': 'Hamilton',
    
    'Helloprint': 'HelloPrint',
    
    'Hertz UK': 'Hertz',

    'Hilton Aberdeen TECA': 'Hilton',
    'Hilton Hotels & Resorts': 'Hilton',
    'Hilton Templepatrick': 'Hilton',
    'Hilton Garden Inn': 'Hilton',
    'Hilton Hotels': 'Hilton',

    
    'HinksBrandwise Digital': 'HinksBrandwise',
    
    'Humphreys signs': 'Humphreys Signs',
    
    'International Centre Telford': 'International Centre',
    
    'Intercontinental Hotels Group': 'InterContinental Hotels Group',
    'InterContinental Hotels Group PLC': 'InterContinental Hotels Group',
    
    'JPI MEDIA': 'JPI Media',
    'JPI Media Publishing': 'JPI Media',
    'JPIMedia Publishing': 'JPI Media',
    
    'JEWISH CHRONICLE NEWSPAPER': 'Jewish Chronicle',
    
    'LDM (UK)': 'LDM',
    'LDM UK': 'LDM',
    
    'Lazar Print': 'Lazer Print',
    
    'Leafletfrog': 'Leaflet Frog',
    
    'Little\'s': 'Littles',
    'Little?s Chauffeur Drive': 'Littles',
    
    'M Media Group': 'M Media',
    
    'MB  Productions': 'MB Productions',
    
    'MessageSpace': 'Message Space',
    
    'Microsoft Ireland Operations': 'Microsoft',
    
    'Minuteman Press Newport': 'Minuteman Press',
    
    'MGI London': 'MGI',
    
    'Neopost UK': 'Neopost', 
    
    'Newsquest (London)': 'Newsquest',
    'Newsquest Media Group': 'Newsquest',

    'O\'Donnell': 'O Donnell',
    'O\'Donnell and Associates': 'O Donnell',
    
    'Paragon CC': 'Paragon Customer Communications',
    'Paragon Customer Communications London': 'Paragon Customer Communications',
    
    'Postal Choices t/a Onepost': 'Postal Choices',
    
    'Potts Print UK': 'Potts Print',
    
    'Printech (Europe)': 'Printech',
    'Printech Express': 'Printech',
    
    'Radisson Blue': 'Radisson Blu',
    'Radisson Blu Hotel Cardiff': 'Radisson Blu',
    
    'Ratio Digital Marketing': 'Ratio',
    
    'Royal Mail Group': 'Royal Mail',

    'Sainsbury\'s': 'Sainsburys',
    'Sainsbury\'s Supermarkets': 'Sainsburys',

    'Sarsen Press.': 'Sarsen Press',
    
    'Snap Group': 'Snapchat',
    'Snap': 'Snapchat',
    
    'Tangent Marketing Services': 'Tangent',
    
    'Tesco Stores': 'Tesco',
    'Tesco PLC': 'Tesco',
    'Tesco Express': 'Tesco',
    'Tesco Neath Abbey': 'Tesco',

    'Tindle Newspapers Devon': 'Tindle Newspapers',
    'Tindle Newspapers Wales & Borders': 'Tindle Newspapers',
    'Tindle Newspapers West Country': 'Tindle Newspapers',
    
    'TradePrint Distribuiton': 'Tradeprint',
    
    'International Centre Telford': 'International Centre',
    
    'Train Line': 'Trainline',
    'thetrainline.com': 'Trainline',
    'Trainline.com': 'Trainline',
    
    'Trosol Cyf': 'Trosol',
    
    'Twitter International Company': 'Twitter',
    'Twitter International': 'Twitter',
    'Twitter Uk': 'Twitter',
    
    'Uber Eats': 'Uber',
    'Uber London': 'Uber',
    'UBER': 'Uber',
    'Uber1': 'Uber',
    
    
    'Wirral Allaince Print Services': 'Wirral Alliance Print Services',
    
    'Whistl (Doordrop Media) Ltd' : 'Whistl',
    'Whistl UK' : 'Whistl',
    
    'YouGov UK': 'YouGov',
    'YouGov plc': 'YouGov',
    'YouGovUK': 'YouGov',

    'Zoom Display': 'Zoom',
    'Zoom Video Communications': 'Zoom',

}

replace_items(df_coding,col_name='Supplier',d=d_supplier)  
coding_suppliers = sorted(df_coding['Supplier'].unique())

replace_items(df_invoice,col_name='SupplierName',d=d_supplier) 
invoice_suppliers = sorted(df_invoice['SupplierName'].unique())

print_sets(name='Supplier',lst_coding=coding_suppliers,lst_invoice=invoice_suppliers)



# Save processed csv
df_coding.to_csv(os.path.join(out_path,'coding_both.csv'),index=False)  
df_invoice.to_csv(os.path.join(out_path,'invoices.csv'),index=False) 
